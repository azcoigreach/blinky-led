from __future__ import annotations

from pathlib import Path

import yaml

from app.core.config import DashboardConfig, load_config


class ConfigStore:
    """Manages validated config persistence with atomic writes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> DashboardConfig:
        return load_config(self.path)

    def save(self, config: DashboardConfig) -> None:
        payload = config.model_dump(mode="python", exclude_none=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as fp:
            yaml.safe_dump(payload, fp, sort_keys=False, allow_unicode=False)
        temp_path.replace(self.path)
