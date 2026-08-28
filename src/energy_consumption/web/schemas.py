from pydantic import BaseModel, ConfigDict, Field


class DrivingConditions(BaseModel):
    """모델 입력용 운행 조건. 관측 범위 이탈은 별도 경고로 처리한다."""

    model_config = ConfigDict(extra="forbid")

    speed_kmh: float = Field(title="평균 속도")
    payload_kg: float = Field(title="적재량")
    ambient_temp_C: float = Field(title="외기 온도")
    hvac_power_kw: float = Field(title="공조 전력")
    road_grade_pct: float = Field(title="도로 경사도")
    battery_temp_C: float = Field(title="배터리 온도")
    driving_style_index: float = Field(title="운전 성향 지수")
    tire_pressure_bar: float = Field(title="타이어 공기압")
    trip_distance_km: float = Field(title="주행 거리")


class PredictionResult(BaseModel):
    consumption_kwh_per_100km: float
    total_energy_kwh: float
    warnings: list[str] = Field(default_factory=list)


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current: DrivingConditions
    alternative: DrivingConditions


class SimulationResult(BaseModel):
    current: PredictionResult
    alternative: PredictionResult
    consumption_difference_kwh_per_100km: float
    savings_rate_pct: float | None
    message: str


class Factor(BaseModel):
    feature: str
    label: str
    importance: float
