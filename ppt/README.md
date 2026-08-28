# 전기차 에너지 소비량 예측 프로젝트 보고서

## 산출물

- `EV_에너지_소비량_예측_프로젝트_보고서.pptx`: 15장 보고서형 발표자료
- `assets/`: 노트북 분석 결과 기반 차트와 실제 웹서비스 캡처

## 구성

기업 상급자가 이해하기 쉬운 업무 문제와 활용 가치를 본문 흐름으로 삼고, 강사 평가에 필요한 데이터·모델·구현 근거를 함께 포함했습니다.

1. Executive summary
2. 비즈니스 문제 및 분석 흐름
3. 데이터 구조와 EDA
4. 모델 비교·성능·Feature Importance
5. 웹서비스 구조와 실제 화면
6. 한계·리스크·향후 계획

발표자료의 예측값은 저장된 `energy_consumption_best_model.joblib`을 사용했으며, 웹 화면은 실제 서비스를 실행해 캡처했습니다.

## 재생성

```bash
uv sync
uv run uvicorn energy_consumption.web.app:app --host 127.0.0.1 --port 8765
uv run python ppt/capture_web.py
uv run python ppt/build_presentation.py
```

`capture_web.py` 실행 시 로컬 웹서비스가 `127.0.0.1:8765`에서 실행 중이어야 합니다.
