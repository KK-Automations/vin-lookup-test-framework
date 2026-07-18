"""Make, model, and year explorer backed by NHTSA vPIC catalog endpoints."""

import logging

import requests

from app.cache.repository import CatalogCacheRepository

logger = logging.getLogger(__name__)

MODELS_URL = (
    "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/"
    "make/{make}/modelyear/{year}?format=json"
)

# Curated ordering for the explorer select; vPIC's full make list has
# thousands of entries, most of which are low-volume manufacturers.
POPULAR_MAKES = [
    "Acura", "Alfa Romeo", "Audi", "BMW", "Buick", "Cadillac", "Chevrolet",
    "Chrysler", "Dodge", "Fiat", "Ford", "Genesis", "GMC", "Honda",
    "Hyundai", "Infiniti", "Jaguar", "Jeep", "Kia", "Land Rover", "Lexus",
    "Lincoln", "Lucid", "Maserati", "Mazda", "Mercedes-Benz", "Mini",
    "Mitsubishi", "Nissan", "Polestar", "Porsche", "Ram", "Rivian",
    "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo",
]

MIN_YEAR = 1981  # 17 character VINs standardized in 1981


class ExplorerService:
    def __init__(self, settings, catalog: CatalogCacheRepository | None = None,
                 max_year: int | None = None) -> None:
        self.settings = settings
        self.catalog = catalog or CatalogCacheRepository(
            settings.vin_db_path, ttl_days=settings.catalog_ttl_days,
        )
        if max_year is None:
            from datetime import date
            max_year = date.today().year + 1
        self.max_year = max_year

    def years(self) -> list[int]:
        return list(range(self.max_year, MIN_YEAR - 1, -1))

    def makes(self) -> list[str]:
        return POPULAR_MAKES

    def models(self, make: str, year: int) -> list[str]:
        make = make.strip()
        key = f"models:{make.casefold()}:{year}"
        cached = self.catalog.get(key)
        if cached is not None:
            return cached

        try:
            response = requests.get(
                MODELS_URL.format(make=requests.utils.quote(make), year=year),
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("vPIC models fetch failed for %s %s: %s", make, year, exc)
            return []

        models = sorted({
            row.get("Model_Name", "").strip()
            for row in payload.get("Results") or []
            if row.get("Model_Name")
        })
        self.catalog.put(key, models)
        return models
