from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class SecretSettings(BaseModel):
    weather_api_key: str | None = Field(default=None, alias="WEATHER_API_KEY")
    news_api_key: str | None = Field(default=None, alias="NEWS_API_KEY")
    stocks_api_key: str | None = Field(default=None, alias="STOCKS_API_KEY")
    poll_api_key: str | None = Field(default=None, alias="POLL_API_KEY")


def load_secrets(env_path: Path) -> SecretSettings:
    if env_path.exists():
        load_dotenv(env_path)
    values = {
        "WEATHER_API_KEY": os.getenv("WEATHER_API_KEY"),
        "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
        "STOCKS_API_KEY": os.getenv("STOCKS_API_KEY"),
        "POLL_API_KEY": os.getenv("POLL_API_KEY"),
    }
    return SecretSettings.model_validate(values)
