from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.runtime import DashboardRuntime


class MessagePayload(dict):
    message: str


def create_web_app(runtime: DashboardRuntime) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if not runtime.state.running:
            await runtime.start()
        yield
        if runtime.state.running:
            await runtime.stop()

    app = FastAPI(title="Blinky LED Dashboard", version="3.0.1", lifespan=lifespan)
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

    @app.get("/api/status")
    async def api_status() -> dict:
        return runtime.status()

    @app.get("/api/widgets")
    async def api_widgets() -> dict:
        return {
            "data": {k: v.model_dump(mode="json") for k, v in runtime.state.widget_data.items()},
            "status": {k: v.model_dump(mode="json") for k, v in runtime.state.widget_status.items()},
        }

    @app.get("/api/pages")
    async def api_pages() -> list[dict]:
        return [p.model_dump() for p in runtime.pages]

    @app.get("/api/config")
    async def api_config() -> dict:
        return runtime.config.model_dump(mode="json")

    @app.get("/api/preview")
    async def api_preview() -> Response:
        return Response(content=runtime.preview_png(), media_type="image/png")

    @app.post("/api/override")
    async def api_override(payload: dict) -> dict:
        message = payload.get("message")
        runtime.set_override(message)
        return {"ok": True, "message": message}

    @app.post("/api/brightness")
    async def api_brightness(payload: dict) -> dict:
        try:
            brightness = int(payload.get("brightness", runtime.state.brightness))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="brightness must be integer") from exc
        runtime.set_brightness(brightness)
        return {"ok": True, "brightness": runtime.state.brightness}

    @app.get("/api/schedule")
    async def api_schedule() -> dict:
        return runtime.config.schedule.model_dump(mode="json")

    @app.post("/api/pin-page")
    async def api_pin_page(payload: dict) -> dict:
        page_id = payload.get("page_id")
        if page_id and page_id not in {p.page_id for p in runtime.pages}:
            raise HTTPException(status_code=404, detail="unknown page")
        runtime.set_pinned_page(page_id)
        return {"ok": True, "pinned_page_id": runtime.state.pinned_page_id}

    @app.post("/api/reload")
    async def api_reload() -> dict:
        if runtime.state.running:
            await runtime.stop()
        await runtime.start()
        return {"ok": True}

    return app
