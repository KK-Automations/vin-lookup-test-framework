"""Provider interface and result types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from app.domain.records import VehicleRecord


class ProviderError(Exception):
    """Raised by providers for any fetch or mapping failure."""


@dataclass
class ProviderResult:
    provider: str
    display_name: str
    ok: bool
    record: VehicleRecord | None
    raw: dict | None
    error: str | None
    latency_ms: int
    from_cache: bool = False


class VinProvider(ABC):
    name: ClassVar[str]
    display_name: ClassVar[str]
    needs_key: ClassVar[bool] = False
    timeout_s: ClassVar[float] = 6.0
    # False when the provider re-serves data derived from NHTSA vPIC, so
    # agreement with vPIC should not count as independent confirmation.
    counts_as_independent: ClassVar[bool] = True

    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def available(self) -> bool:
        return not self.needs_key

    @abstractmethod
    def fetch(self, vin: str) -> dict:
        """Fetch the raw provider payload. Raises ProviderError on failure."""

    @abstractmethod
    def to_record(self, raw: dict) -> VehicleRecord:
        """Map a raw payload to the normalized VehicleRecord."""
