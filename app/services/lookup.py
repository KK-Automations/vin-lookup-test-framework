"""Lookup orchestrator: validate, fan out to providers, build consensus."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

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
    from_cache: bool = False


class LookupService:
    def __init__(self, settings, providers: list[VinProvider] | None = None) -> None:
        self.settings = settings
        self.providers = providers if providers is not None else active_providers(settings)

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

        results = self._fan_out(parsed.normalized)
        engine = ConsensusEngine(independence={
            p.name: p.counts_as_independent for p in self.providers
        })
        return LookupResult(
            parsed=parsed,
            structural=structural_summary(parsed),
            provider_results=results,
            consensus=engine.evaluate(results),
            suggestions=suggest_corrections(raw_vin) if not parsed.check_digit_ok else [],
        )

    def _fan_out(self, vin: str) -> list[ProviderResult]:
        if not self.providers:
            return []
        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            futures = {
                executor.submit(self._run_provider, provider, vin): provider
                for provider in self.providers
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
