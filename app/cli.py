from __future__ import annotations

import asyncio
import signal
from pathlib import Path

import click
import uvicorn

from app.core.config import load_config
from app.core.logging import configure_logging
from app.core.settings import load_secrets
from app.runtime import DashboardRuntime
from app.web.server import create_web_app


def common_runtime_options(func):
    func = click.option("--config", "config_path", default=None, help="Path to YAML configuration")(func)
    func = click.option("--env-file", "env_file", default=None, help="Path to .env file")(func)
    func = click.option("--log-level", default=None)(func)
    return func


def initialize_context(ctx: click.Context, config_path: str | None, env_file: str | None, log_level: str | None) -> None:
    existing = ctx.ensure_object(dict)
    resolved_config = config_path or existing.get("config_path") or "config.yaml"
    resolved_env = env_file or existing.get("env_file") or ".env"
    resolved_log_level = log_level or existing.get("log_level") or "INFO"
    configure_logging(resolved_log_level)
    existing["config_path"] = resolved_config
    existing["env_file"] = resolved_env
    existing["log_level"] = resolved_log_level
    existing["config"] = load_config(resolved_config)
    existing["secrets"] = load_secrets(Path(resolved_env))


@click.group()
@click.option("--config", "config_path", default="config.yaml", show_default=True, help="Path to YAML configuration")
@click.option("--env-file", "env_file", default=".env", show_default=True, help="Path to .env file")
@click.option("--log-level", default="INFO", show_default=True)
@click.pass_context
def cli(ctx: click.Context, config_path: str, env_file: str, log_level: str) -> None:
    initialize_context(ctx, config_path, env_file, log_level)


@cli.command("run")
@common_runtime_options
@click.pass_context
def run_dashboard(ctx: click.Context, config_path: str | None, env_file: str | None, log_level: str | None) -> None:
    """Run the dashboard runtime loop without web server."""
    initialize_context(ctx, config_path, env_file, log_level)
    runtime = DashboardRuntime(ctx.obj["config"])

    async def _runner() -> None:
        await runtime.start()
        stop_event = asyncio.Event()

        def _stop(*_: object) -> None:
            stop_event.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _stop)
        await stop_event.wait()
        await runtime.stop()

    asyncio.run(_runner())


@cli.command("serve")
@common_runtime_options
@click.option("--host", default=None, help="Bind host override")
@click.option("--port", default=None, type=int, help="Bind port override")
@click.pass_context
def serve_dashboard(
    ctx: click.Context,
    config_path: str | None,
    env_file: str | None,
    log_level: str | None,
    host: str | None,
    port: int | None,
) -> None:
    """Run FastAPI web server and dashboard runtime."""
    initialize_context(ctx, config_path, env_file, log_level)
    runtime = DashboardRuntime(ctx.obj["config"])
    app = create_web_app(runtime)
    bind_host = host or ctx.obj["config"].api.host
    bind_port = port or ctx.obj["config"].api.port
    uvicorn.run(app, host=bind_host, port=bind_port)


if __name__ == "__main__":
    cli()
