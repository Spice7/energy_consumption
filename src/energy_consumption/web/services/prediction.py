from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from joblib import load

from energy_consumption.paths import MODEL_DIR
from energy_consumption.web.schemas import DrivingConditions, Factor, PredictionResult

MODEL_FILENAME = "energy_consumption_best_model.joblib"
EXPECTED_FEATURES = {
    "speed_kmh",
    "payload_kg",
    "ambient_temp_C",
    "hvac_power_kw",
    "road_grade_pct",
    "battery_temp_C",
    "driving_style_index",
    "tire_pressure_bar",
    "trip_distance_km",
}
FEATURE_LABELS = {
    "speed_kmh": "평균 속도",
    "payload_kg": "적재량",
    "ambient_temp_C": "외기 온도",
    "hvac_power_kw": "공조 전력",
    "road_grade_pct": "도로 경사도",
    "battery_temp_C": "배터리 온도",
    "driving_style_index": "운전 성향 지수",
    "tire_pressure_bar": "타이어 공기압",
    "trip_distance_km": "주행 거리",
}
OBSERVED_RANGES = {
    "speed_kmh": (20, 130),
    "payload_kg": (0, 500),
    "ambient_temp_C": (-10, 40),
    "hvac_power_kw": (0, 5),
    "road_grade_pct": (-5, 8),
    "battery_temp_C": (15, 45),
    "driving_style_index": (0, 1),
    "tire_pressure_bar": (2.0, 2.8),
    "trip_distance_km": (5.1, 200),
}


@dataclass(frozen=True)
class ModelBundle:
    model: Any
    feature_columns: tuple[str, ...]
    target_column: str
    best_params: dict[str, Any]
    metrics: dict[str, float]


def load_model_bundle(model_path: Path | None = None) -> ModelBundle:
    """저장된 최종 모델을 한 번 로드하고 웹 입력과의 호환성을 확인한다."""
    path = model_path or MODEL_DIR / MODEL_FILENAME
    raw = load(path)
    required = {"model", "feature_columns", "target_column", "best_params", "metrics"}
    missing = required.difference(raw)
    if missing:
        raise ValueError(f"모델 파일에 필수 항목이 없습니다: {sorted(missing)}")

    feature_columns = tuple(raw["feature_columns"])
    if len(feature_columns) != len(EXPECTED_FEATURES) or set(feature_columns) != EXPECTED_FEATURES:
        raise ValueError("저장 모델의 feature_columns가 웹 입력 스키마와 일치하지 않습니다.")

    return ModelBundle(
        model=raw["model"],
        feature_columns=feature_columns,
        target_column=raw["target_column"],
        best_params=raw["best_params"],
        metrics=raw["metrics"],
    )


class PredictionService:
    def __init__(self, bundle: ModelBundle):
        self.bundle = bundle

    def predict(self, conditions: DrivingConditions) -> PredictionResult:
        values = conditions.model_dump()
        # 저장 모델의 열 순서가 유일한 최종 기준이다.
        frame = pd.DataFrame(
            [[values[column] for column in self.bundle.feature_columns]],
            columns=list(self.bundle.feature_columns),
        )
        consumption = float(self.bundle.model.predict(frame)[0])
        total = consumption * conditions.trip_distance_km / 100
        warnings = self.range_warnings(values)
        return PredictionResult(
            consumption_kwh_per_100km=round(consumption, 2),
            total_energy_kwh=round(total, 2),
            warnings=warnings,
        )

    @staticmethod
    def range_warnings(values: dict[str, float]) -> list[str]:
        warnings = []
        for feature, value in values.items():
            minimum, maximum = OBSERVED_RANGES[feature]
            if not minimum <= value <= maximum:
                warnings.append(
                    f"{FEATURE_LABELS[feature]} {value:g}은(는) 학습 데이터 관측 범위 "
                    f"{minimum:g}~{maximum:g} 밖입니다. 예측의 불확실성이 높을 수 있습니다."
                )
        return warnings

    def important_factors(self, limit: int = 5) -> list[Factor]:
        estimator = getattr(self.bundle.model, "named_steps", {}).get("model", self.bundle.model)
        importances = getattr(estimator, "feature_importances_", None)
        if importances is None or len(importances) != len(self.bundle.feature_columns):
            return []
        factors = [
            Factor(feature=feature, label=FEATURE_LABELS[feature], importance=float(importance))
            for feature, importance in zip(self.bundle.feature_columns, importances, strict=True)
        ]
        return sorted(factors, key=lambda item: item.importance, reverse=True)[:limit]
