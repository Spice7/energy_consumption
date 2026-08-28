from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from energy_consumption.web.schemas import (
    DrivingConditions,
    Factor,
    PredictionResult,
    SimulationRequest,
    SimulationResult,
)
from energy_consumption.web.services.prediction import PredictionService
from energy_consumption.web.services.simulation import SimulationService


def create_router(templates: Jinja2Templates) -> APIRouter:
    router = APIRouter()

    def prediction_service(request: Request) -> PredictionService:
        return request.app.state.prediction_service

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"factors": prediction_service(request).important_factors()},
        )

    @router.get("/health")
    async def health(request: Request) -> dict[str, str]:
        service = prediction_service(request)
        return {"status": "ok", "target": service.bundle.target_column}

    @router.post("/api/predict", response_model=PredictionResult)
    async def predict(payload: DrivingConditions, request: Request) -> PredictionResult:
        return prediction_service(request).predict(payload)

    @router.post("/api/simulate", response_model=SimulationResult)
    async def simulate(payload: SimulationRequest, request: Request) -> SimulationResult:
        service = SimulationService(prediction_service(request))
        return service.compare(payload)

    @router.get("/api/factors", response_model=list[Factor])
    async def factors(request: Request) -> list[Factor]:
        return prediction_service(request).important_factors()

    return router
