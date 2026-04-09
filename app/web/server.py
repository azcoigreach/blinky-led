from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.runtime import DashboardRuntime
from app.services.config_store import ConfigStore
from app.core.config import DashboardConfig
from app.web.schemas import (
    BrightnessRequest,
    BrightnessResponse,
    ConfigApplyRequest,
    ConfigMutationResponse,
    ConfigResponse,
    ConfigValidateRequest,
    ConfigValidateResponse,
    OverrideRequest,
    OverrideResponse,
    PageReorderRequest,
    PageUpsertRequest,
    PagesResponse,
    PinPageRequest,
    PinPageResponse,
    ProviderUpsertRequest,
    ReloadResponse,
    ScheduleResponse,
    StatusResponse,
    WidgetUpsertRequest,
    WidgetsResponse,
)


def create_web_app(runtime: DashboardRuntime, config_path: str | Path = "config.yaml") -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if not runtime.state.running:
            await runtime.start()
        yield
        if runtime.state.running:
            await runtime.stop()

    app = FastAPI(title="Blinky LED Dashboard", version="3.0.3", lifespan=lifespan)
    base = Path(__file__).parent
    templates = Jinja2Templates(directory=str(base / "templates"))
    config_store = ConfigStore(config_path)
    app.mount("/static", StaticFiles(directory=str(base / "static")), name="static")

    def require_widget(widget_id: str, config: DashboardConfig) -> None:
        if widget_id not in config.widgets:
            raise HTTPException(status_code=404, detail="unknown widget")

    def require_provider_family(family: str) -> None:
        valid = {"stocks", "markets", "futures", "crypto"}
        if family not in valid:
            raise HTTPException(status_code=404, detail="unknown provider family")

    def require_page(page_id: str, config: DashboardConfig) -> int:
        for idx, page in enumerate(config.pages):
            if page.page_id == page_id:
                return idx
        raise HTTPException(status_code=404, detail="unknown page")

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
            meta=runtime.widget_runtime_meta(),
        )

    @app.get("/api/pages", response_model=PagesResponse)
    async def api_pages() -> PagesResponse:
        return PagesResponse(pages=runtime.pages)

    @app.get("/api/config", response_model=ConfigResponse)
    async def api_config() -> ConfigResponse:
        return ConfigResponse(config=runtime.config)

    @app.post("/api/config/validate", response_model=ConfigValidateResponse)
    async def api_config_validate(payload: ConfigValidateRequest) -> ConfigValidateResponse:
        try:
            DashboardConfig.model_validate(payload.config)
        except Exception as exc:  # noqa: BLE001
            return ConfigValidateResponse(ok=False, message=str(exc))
        return ConfigValidateResponse(ok=True, message="config is valid")

    @app.post("/api/config/widgets/{widget_id}", response_model=ConfigMutationResponse)
    async def api_upsert_widget(widget_id: str, payload: WidgetUpsertRequest) -> ConfigMutationResponse:
        config = config_store.load()
        config.widgets[widget_id] = payload.widget
        config_store.save(config)
        return ConfigMutationResponse(message=f"widget '{widget_id}' saved")

    @app.delete("/api/config/widgets/{widget_id}", response_model=ConfigMutationResponse)
    async def api_delete_widget(widget_id: str) -> ConfigMutationResponse:
        config = config_store.load()
        require_widget(widget_id, config)
        if any(widget_id in page.widgets for page in config.pages):
            raise HTTPException(status_code=409, detail="widget is assigned to one or more pages")
        del config.widgets[widget_id]
        config_store.save(config)
        return ConfigMutationResponse(message=f"widget '{widget_id}' deleted")

    @app.post("/api/config/providers/{family}", response_model=ConfigMutationResponse)
    async def api_upsert_provider_family(family: str, payload: ProviderUpsertRequest) -> ConfigMutationResponse:
        require_provider_family(family)
        config = config_store.load()
        setattr(config.providers, family, payload.provider)
        config_store.save(config)
        return ConfigMutationResponse(message=f"provider family '{family}' saved")

    @app.post("/api/config/pages", response_model=ConfigMutationResponse)
    async def api_upsert_page(payload: PageUpsertRequest) -> ConfigMutationResponse:
        config = config_store.load()
        page = payload.page
        matched = False
        for idx, existing in enumerate(config.pages):
            if existing.page_id == page.page_id:
                config.pages[idx] = page
                matched = True
                break
        if not matched:
            config.pages.append(page)
        config_store.save(config)
        return ConfigMutationResponse(message=f"page '{page.page_id}' saved")

    @app.post("/api/config/pages/reorder", response_model=ConfigMutationResponse)
    async def api_reorder_pages(payload: PageReorderRequest) -> ConfigMutationResponse:
        config = config_store.load()
        current_ids = [page.page_id for page in config.pages]
        if sorted(payload.page_ids) != sorted(current_ids):
            raise HTTPException(status_code=422, detail="page_ids must match existing pages")
        page_map = {page.page_id: page for page in config.pages}
        config.pages = [page_map[page_id] for page_id in payload.page_ids]
        config_store.save(config)
        return ConfigMutationResponse(message="pages reordered")

    @app.delete("/api/config/pages/{page_id}", response_model=ConfigMutationResponse)
    async def api_delete_page(page_id: str) -> ConfigMutationResponse:
        config = config_store.load()
        index = require_page(page_id, config)
        if len(config.pages) <= 1:
            raise HTTPException(status_code=409, detail="cannot delete the last configured page")
        del config.pages[index]
        config_store.save(config)
        return ConfigMutationResponse(message=f"page '{page_id}' deleted")

    @app.post("/api/config/apply", response_model=ConfigMutationResponse)
    async def api_apply_config(payload: ConfigApplyRequest) -> ConfigMutationResponse:
        config = config_store.load()
        runtime.config = config
        if payload.reload_runtime:
            await runtime.apply_config(config)
            return ConfigMutationResponse(message="config applied and runtime reloaded")
        return ConfigMutationResponse(message="config stored (runtime not reloaded)")

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
