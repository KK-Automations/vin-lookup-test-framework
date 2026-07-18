"""CarAPI provider (https://carapi.app), free tier with JWT auth.

The JWT is cached per provider instance and refreshed from its exp claim;
a 401 triggers exactly one re-auth attempt.
"""

import base64
import json
import time

import requests

from app.domain.records import VehicleRecord
from app.providers.base import ProviderError, VinProvider

AUTH_URL = "https://carapi.app/api/auth/login"
DECODE_URL = "https://carapi.app/api/vin/{vin}"


def _jwt_exp(token: str) -> float:
    """Read the exp claim without verification; 0 when unreadable."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return float(json.loads(base64.urlsafe_b64decode(payload)).get("exp", 0))
    except Exception:
        return 0.0


class CarApiProvider(VinProvider):
    name = "carapi"
    display_name = "CarAPI"
    needs_key = True
    timeout_s = 8.0
    # CarAPI blends vPIC-derived data with its own; treated as dependent.
    counts_as_independent = False

    def __init__(self, settings) -> None:
        super().__init__(settings)
        self._token: str | None = None
        self._token_exp: float = 0.0

    def available(self) -> bool:
        return bool(self.settings.carapi_token and self.settings.carapi_secret)

    def _authenticate(self) -> str:
        try:
            response = requests.post(
                AUTH_URL,
                json={
                    "api_token": self.settings.carapi_token,
                    "api_secret": self.settings.carapi_secret,
                },
                timeout=self.timeout_s,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ProviderError(f"CarAPI auth failed: {exc}") from exc

        # The login endpoint returns the JWT as plain text; older behavior
        # wrapped it in JSON under "token". Accept both.
        token = response.text.strip()
        if token.startswith("{"):
            token = (response.json() or {}).get("token", "")
        if not token:
            raise ProviderError("CarAPI auth returned no token")
        self._token = token
        self._token_exp = _jwt_exp(token)
        return token

    def _token_valid(self) -> bool:
        return bool(self._token) and (
            self._token_exp == 0.0 or self._token_exp - time.time() > 60
        )

    def fetch(self, vin: str) -> dict:
        if not self._token_valid():
            self._authenticate()
        raw = self._get(vin)
        if raw is None:  # one re-auth on 401
            self._authenticate()
            raw = self._get(vin)
            if raw is None:
                raise ProviderError("CarAPI rejected credentials twice")
        return raw

    def _get(self, vin: str) -> dict | None:
        try:
            response = requests.get(
                DECODE_URL.format(vin=vin),
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=self.timeout_s,
            )
            if response.status_code == 401:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise ProviderError(f"CarAPI request failed: {exc}") from exc
        except ValueError as exc:
            raise ProviderError("CarAPI returned invalid JSON") from exc

    @staticmethod
    def _usable(value):
        """Drop free-tier paywall placeholders like '*** (NOTE: ...)'."""
        if isinstance(value, str) and ("***" in value or "NOTE:" in value):
            return None
        return value

    def to_record(self, raw: dict) -> VehicleRecord:
        record = VehicleRecord()

        def put(field: str, value, raw_key: str):
            record.set(field, self._usable(value), str(raw.get(raw_key)), self.name)

        put("make", raw.get("make"), "make")
        put("model", raw.get("model"), "model")
        year = self._usable(raw.get("year"))
        if isinstance(year, str) and year.isdigit():
            year = int(year)
        record.set("year", year if isinstance(year, int) else None,
                   str(raw.get("year")), self.name)
        put("trim", raw.get("trim"), "trim")

        specs = raw.get("specs") or {}

        def put_spec(field: str, key: str):
            value = self._usable(specs.get(key)) or self._usable(raw.get(key))
            record.set(field, value, str(specs.get(key)), self.name)

        put_spec("body_class", "body_class")
        doors = self._usable(specs.get("doors"))
        record.set("doors", doors if isinstance(doors, int) else None,
                   str(specs.get("doors")), self.name)
        put_spec("fuel_type", "fuel_type")
        put_spec("drive_type", "drive_type")
        put_spec("transmission", "transmission")
        return record
