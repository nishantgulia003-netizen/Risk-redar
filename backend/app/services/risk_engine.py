"""Transparent, deterministic weighted-sum risk scoring for one area."""
from dataclasses import dataclass
from typing import Mapping

DEFAULT_WEIGHTS = {
    "hazard_intensity": 40.0,
    "population_exposure": 25.0,
    "vulnerability": 20.0,
    "historical_risk": 15.0,
}


@dataclass(frozen=True)
class RiskResult:
    score: float
    priority: str
    vulnerability: float
    breakdown: dict[str, float]


class RiskEngine:
    """Calculates risk on a 0–100 scale using explicit, configurable weights.

    Weights are percentage points and must sum to 100. Every contribution in
    ``breakdown`` is simply ``normalised component × its configured weight``.
    """

    def __init__(self, weights: Mapping[str, float] | None = None):
        self.weights = dict(DEFAULT_WEIGHTS)
        if weights:
            unknown = set(weights) - set(DEFAULT_WEIGHTS)
            if unknown:
                raise ValueError(f"Unknown risk weights: {sorted(unknown)}")
            self.weights.update(weights)
        if any(value < 0 for value in self.weights.values()):
            raise ValueError("Risk weights cannot be negative")
        if round(sum(self.weights.values()), 8) != 100:
            raise ValueError("Risk weights must sum to 100")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def score(
        self,
        *,
        hazard_intensity: float,
        population_density: float,
        elderly_pct: float,
        children_pct: float,
        historical_disaster_count: int,
        max_population_density: float,
        max_historical_disaster_count: int,
    ) -> RiskResult:
        """Score an area using district-wide density/history normalization maxima."""
        population_exposure = 0.0 if max_population_density <= 0 else self._clamp(population_density / max_population_density)
        historical_risk = 0.0 if max_historical_disaster_count <= 0 else self._clamp(historical_disaster_count / max_historical_disaster_count)
        vulnerability = self._clamp((elderly_pct + children_pct) / 100)
        components = {
            "hazard_intensity": self._clamp(hazard_intensity),
            "population_exposure": population_exposure,
            "vulnerability": vulnerability,
            "historical_risk": historical_risk,
        }
        breakdown = {name: round(components[name] * self.weights[name], 2) for name in self.weights}
        score = round(sum(breakdown.values()), 2)
        priority = "IMMEDIATE" if score >= 80 else "HIGH" if score >= 60 else "MODERATE" if score >= 40 else "SAFE"
        return RiskResult(score=score, priority=priority, vulnerability=round(vulnerability, 3), breakdown=breakdown)
