"""Application settings loaded from the environment.

Every provider credential is optional: a missing key means the provider is
skipped at startup, never a crash.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    carapi_token: str | None = None
    carapi_secret: str | None = None
    autodev_api_key: str | None = None
    vin_db_path: str = "data/vin_cache.sqlite3"
    provider_timeout_s: float = 6.0
    provider_response_ttl_days: int = 30
    catalog_ttl_days: int = 7
    testing: bool = False
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            carapi_token=os.getenv("CARAPI_API_TOKEN") or None,
            carapi_secret=os.getenv("CARAPI_API_SECRET") or None,
            autodev_api_key=os.getenv("AUTODEV_API_KEY") or None,
            vin_db_path=os.getenv("VIN_DB_PATH", "data/vin_cache.sqlite3"),
            provider_timeout_s=float(os.getenv("PROVIDER_TIMEOUT_S", "6.0")),
        )
