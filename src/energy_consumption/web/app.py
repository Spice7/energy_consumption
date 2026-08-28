from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from energy_consumption.paths import PROJECT_ROOT
from energy_consumption.web.routes import create_router
from energy_consumption.web.services.prediction import PredictionService, load_model_bundle

WEB_DIR = PROJECT_ROOT / "src" / "energy_consumption" / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 한 번만 로드한 서비스를 모든 요청에서 재사용한다.
    app.state.prediction_service = PredictionService(load_model_bundle())
    yield


app = FastAPI(
    title="전기차 에너지 소비량 예측 실습 서비스",
    description="저장된 모델을 이용한 조건별 시뮬레이션",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
app.include_router(create_router(Jinja2Templates(directory=WEB_DIR / "templates")))
