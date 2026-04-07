from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.runtime import DashboardRuntime
from app.web.schemas import (
    BrightnessRequest,
    BrightnessResponse,
    ConfigResponse,
    OverrideRequest,
    OverrideResponse,
    PagesResponse,
    PinPageRequest,
    PinPageResponse,
    ReloadResponse,
    ScheduleResponse,
    StatusResponse,
    WidgetsResponse,
)


def create_web_app(runtime: DashboardRuntime) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if not runtime.state.running:
            await runtime.start()
        yield
        if runtime.state.running:
            await runtime.stop()

    app = FastAPI(title="Blinky LED Dashboard", version="3.1.0", lifespan=lifespan)
    base = Path(__file__).parent
    templates = Jinja2Templates(directory=str(base / "templates"))
    app.mount("/static", StaticFiles(directory=str(base / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "status": runtime.status(),
                "pages": [p.model_dump() for p in runtime.pages],
                "widgets": list(runtime.widgets.keys()),
            },
        )

    @app.get("/api/status", response_model=StatusResponse)
    async def api_status() -> StatusResponse:
        return StatusResponse.model_validate(runtime.status())

    @app.get("/api/widgets", response_model=WidgetsResponse)
    async def api_widgets() -> WidgetsResponse:
        return WidgetsResponse(
            data={k: v.model_dump(mode="json") for k, v in runtime.state.widget_data.items()},
            status={k: v.model_dump(mode="json") for k, v in runtime.state.widget_status.items()},
        )

    @app.get("/api/pages", response_model=PagesResponse)
    async def api_pages() -> PagesResponse:
        return PagesResponse(pages=runtime.pages)

    @app.get("/api/config", response_model=ConfigResponse)
    async def api_config() -> ConfigResponse:
        return ConfigResponse(config=runtime.config)

    @app.get("/api/preview")
    async def api_preview() -> Response:
        return Response(content=runtime.preview_png(), media_type="image/png")

    @app.post("/api/override", response_model=OverrideResponse)
    async def api_override(payload: OverrideRequest) -> OverrideResponse:
        runtime.set_override(payload.message)
        return OverrideResponse(message=payload.message)

    @app.post("/api/brightness", response_model=BrightnessResponse)
    async def api_brightness(payload: BrightnessRequest) -> BrightnessResponse:
        runtime.set_brightness(payload.brightness)
        return BrightnessResponse(brightness=runtime.state.brightness)

    @app.get("/api/schedule", response_model=ScheduleResponse)
    async def api_schedule() -> ScheduleResponse:
        return ScheduleResponse(schedule=runtime.config.schedule)

    @app.post("/api/pin-page", response_model=PinPageResponse)
    async def api_pin_page(payload: PinPageRequest) -> PinPageResponse:
        page_id = payload.page_id
        if page_id and page_id not in {p.page_id for p in runtime.pages}:
            raise HTTPException(status_code=404, detail="unknown page")
        runtime.set_pinned_page(page_id)
        return PinPageResponse(pinned_page_id=runtime.state.pinned_page_id)

    @app.post("/api/reload", response_model=ReloadResponse)
    async def api_reload() -> ReloadResponse:
        if runtime.state.running:
            await runtime.stop()
        await runtime.start()
        return ReloadResponse()

    return app
