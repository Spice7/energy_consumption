from energy_consumption.web.schemas import SimulationRequest, SimulationResult
from energy_consumption.web.services.prediction import PredictionService


class SimulationService:
    def __init__(self, prediction_service: PredictionService):
        self.prediction_service = prediction_service

    def compare(self, request: SimulationRequest) -> SimulationResult:
        current = self.prediction_service.predict(request.current)
        alternative = self.prediction_service.predict(request.alternative)
        difference = alternative.consumption_kwh_per_100km - current.consumption_kwh_per_100km

        savings_rate = None
        if alternative.consumption_kwh_per_100km < current.consumption_kwh_per_100km:
            savings_rate = round(
                (current.consumption_kwh_per_100km - alternative.consumption_kwh_per_100km)
                / current.consumption_kwh_per_100km
                * 100,
                2,
            )
            message = "대안 계획의 모델 기반 예상 소비량이 현재 계획보다 낮습니다."
        else:
            message = "대안 계획의 예상 절감률은 계산되지 않습니다(예상 소비량이 더 낮지 않음)."

        return SimulationResult(
            current=current,
            alternative=alternative,
            consumption_difference_kwh_per_100km=round(difference, 2),
            savings_rate_pct=savings_rate,
            message=message,
        )
