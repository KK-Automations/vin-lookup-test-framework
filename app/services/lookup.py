"""Lookup orchestrator: validate, check cache, fan out, build consensus."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from app.cache.repository import VinCacheRepository
from app.consensus.engine import ConsensusEngine, ConsensusReport
from app.domain.suggestions import Suggestion, suggest_corrections
from app.domain.vin import ParsedVIN, parse_vin, structural_summary
from app.providers import active_providers
from app.providers.base import ProviderError, ProviderResult, VinProvider

logger = logging.getLogger(__name__)


@dataclass
class LookupResult:
    parsed: ParsedVIN
    structural: dict
    provider_results: list[ProviderResult]
    consensus: ConsensusReport | None
    suggestions: list[Suggestion]

    @property
    def from_cache(self) -> bool:
        return bool(self.provider_results) and all(
            r.from_cache for r in self.provider_results if r.ok
        )


class LookupService:
    def __init__(self, settings, providers: list[VinProvider] | None = None,
                 repository: VinCacheRepository | None = None) -> None:
        self.settings = settings
        self.providers = providers if providers is not None else active_providers(settings)
        self.repository = repository or VinCacheRepository(
            settings.vin_db_path,
            response_ttl_days=settings.provider_response_ttl_days,
        )

    def lookup(self, raw_vin: str, force_refresh: bool = False) -> LookupResult:
        parsed = parse_vin(raw_vin)

        if not parsed.ok:
            return LookupResult(
                parsed=parsed,
                structural={},
                provider_results=[],
                consensus=None,
                suggestions=suggest_corrections(raw_vin),
            )

        vin = parsed.normalized
        cached = {} if force_refresh else self.repository.fresh_responses(vin)

        results: list[ProviderResult] = []
        to_fetch: list[VinProvider] = []
        for provider in self.providers:
            hit = cached.get(provider.name)
            if hit is not None and hit.raw is not None:
                try:
                    results.append(ProviderResult(
                        provider=provider.name,
                        display_name=provider.display_name,
                        ok=True, record=provider.to_record(hit.raw),
                        raw=hit.raw, error=None,
                        latency_ms=hit.latency_ms, from_cache=True,
                    ))
                    continue
                except Exception:
                    logger.warning("Cached payload for %s unusable; refetching",
                                   provider.name)
            to_fetch.append(provider)

        fetched = self._fan_out(vin, to_fetch)
        results.extend(fetched)

        for result in fetched:
            self.repository.save_response(
                vin, result.provider,
                "ok" if result.ok else "error",
                result.latency_ms, result.raw,
            )

        engine = ConsensusEngine(independence={
            p.name: p.counts_as_independent for p in self.providers
        })
        consensus = engine.evaluate(results)

        def field_value(name):
            fc = consensus.fields.get(name)
            return fc.value if fc and fc.value is not None else None

        self.repository.record_lookup(
            vin,
            make=field_value("make"),
            model=field_value("model"),
            year=field_value("year"),
            confidence=consensus.confidence,
            bucket=consensus.confidence_bucket,
        )

        return LookupResult(
            parsed=parsed,
            structural=structural_summary(parsed),
            provider_results=results,
            consensus=consensus,
            suggestions=suggest_corrections(raw_vin) if not parsed.check_digit_ok else [],
        )

    def _fan_out(self, vin: str, providers: list[VinProvider]) -> list[ProviderResult]:
        if not providers:
            return []
        with ThreadPoolExecutor(max_workers=len(providers)) as executor:
            futures = {
                executor.submit(self._run_provider, provider, vin): provider
                for provider in providers
            }
            results = []
            for future, provider in futures.items():
                try:
                    results.append(future.result(timeout=provider.timeout_s + 2))
                except Exception as exc:  # timeout or unexpected bug stays isolated
                    logger.warning("Provider %s failed: %s", provider.name, exc)
                    results.append(ProviderResult(
                        provider=provider.name,
                        display_name=provider.display_name,
                        ok=False, record=None, raw=None,
                        error=str(exc), latency_ms=0,
                    ))
            return results

    @staticmethod
    def _run_provider(provider: VinProvider, vin: str) -> ProviderResult:
        started = time.monotonic()
        try:
            raw = provider.fetch(vin)
            record = provider.to_record(raw)
            return ProviderResult(
                provider=provider.name,
                display_name=provider.display_name,
                ok=True, record=record, raw=raw, error=None,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
        except ProviderError as exc:
            return ProviderResult(
                provider=provider.name,
                display_name=provider.display_name,
                ok=False, record=None, raw=None, error=str(exc),
                latency_ms=int((time.monotonic() - started) * 1000),
            )
