"""Provider registry.

Providers are ordered; the registry filters to those whose credentials are
present so the app degrades gracefully instead of failing when a key is
absent.
"""

import logging

from app.providers.autodev import AutoDevProvider
from app.providers.base import VinProvider
from app.providers.carapi import CarApiProvider
from app.providers.local_structural import LocalStructuralProvider
from app.providers.nhtsa_vpic import NhtsaVpicProvider

logger = logging.getLogger(__name__)

ALL_PROVIDERS: list[type[VinProvider]] = [
    LocalStructuralProvider,
    NhtsaVpicProvider,
    CarApiProvider,
    AutoDevProvider,
]


def register(provider_cls: type[VinProvider]) -> None:
    if provider_cls not in ALL_PROVIDERS:
        ALL_PROVIDERS.append(provider_cls)


def provider_label(name: str) -> str:
    """Human readable name for an internal provider id."""
    for cls in ALL_PROVIDERS:
        if cls.name == name:
            return cls.display_name
    return name


def active_providers(settings) -> list[VinProvider]:
    active: list[VinProvider] = []
    for cls in ALL_PROVIDERS:
        provider = cls(settings)
        if provider.available():
            active.append(provider)
        else:
            logger.info("Provider %s skipped: no credentials configured", cls.name)
    return active
