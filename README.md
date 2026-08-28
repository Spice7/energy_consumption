# 전기차 에너지 소비량 예측 웹서비스

저장된 머신러닝 모델을 이용해 운행 조건별 예상 에너지 소비량을 확인하고 현재 계획과 대안 계획을 비교하는 실습용 FastAPI 웹서비스입니다. 웹서비스 실행 중 모델을 다시 학습하지 않습니다.

## 제공 기능

- 9개 운행 조건을 이용한 예상 소비량(kWh/100km)과 예상 총소비 에너지 계산
- 현재 계획과 대안 계획의 조건별 시뮬레이션 및 예상 절감률 비교
- 저장 모델의 Feature Importance를 이용한 소비량 관련 주요 요인 표시
- 학습 데이터 관측 범위를 벗어난 입력에 대한 예측 불확실성 경고

Feature Importance는 모델 예측에 활용된 상대적 중요도이며 인과관계를 의미하지 않습니다. 이 서비스는 교육 및 실습용으로, 실제 운영 의사결정에는 추가 검증이 필요합니다.

## Ubuntu + uv 실행

프로젝트 루트에서 다음 명령을 실행합니다.

```bash
uv sync
uv run uvicorn energy_consumption.web.app:app --host 0.0.0.0 --port 8000 --reload
```

브라우저에서 <http://localhost:8000>에 접속합니다. API 문서는 <http://localhost:8000/docs>, 상태 확인은 <http://localhost:8000/health>에서 볼 수 있습니다.

## 프로젝트 구조

```text
data/                                  원본 CSV와 서비스 기획 노트북
model/                                 학습 완료된 최종 joblib 모델
src/energy_consumption.ipynb           분석 및 모델링 노트북
src/energy_consumption/
├── paths.py                           프로젝트·데이터·모델 경로
└── web/
    ├── app.py                         FastAPI 앱 생성 및 모델 시작 로드
    ├── routes.py                      페이지와 API 라우트
    ├── schemas.py                     입력 범위 및 응답 스키마
    ├── services/
    │   ├── prediction.py              모델 로드·예측·중요 요인
    │   └── simulation.py              현재/대안 비교
    ├── templates/index.html           Jinja2 화면
    └── static/                        CSS와 JavaScript
```

모델 및 데이터 경로는 절대경로나 현재 working directory가 아니라 `energy_consumption.paths`의 `MODEL_DIR`, `DATA_DIR`를 사용합니다.

## API 예시

```bash
curl -X POST http://localhost:8000/api/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "speed_kmh": 70,
    "payload_kg": 180,
    "ambient_temp_C": 20,
    "hvac_power_kw": 1.5,
    "road_grade_pct": 0,
    "battery_temp_C": 25,
    "driving_style_index": 0.5,
    "tire_pressure_bar": 2.4,
    "trip_distance_km": 50
  }'
```
