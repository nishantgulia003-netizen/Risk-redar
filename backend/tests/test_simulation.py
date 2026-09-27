from app.services.risk_engine import RiskEngine
from app.services.simulation import increased_intensity_multiplier


def test_rainfall_increase_never_decreases_area_risk_score():
    engine = RiskEngine()
    common = {"population_density": 500, "elderly_pct": 12, "children_pct": 20, "historical_disaster_count": 3, "max_population_density": 1000, "max_historical_disaster_count": 5}
    rainfall_intensities = [0.0, 0.18, 0.55, 0.9]
    multiplier = increased_intensity_multiplier(50)
    before_scores = [engine.score(hazard_intensity=intensity, **common).score for intensity in rainfall_intensities]
    after_scores = [engine.score(hazard_intensity=intensity * multiplier, **common).score for intensity in rainfall_intensities]
    assert all(after >= before for before, after in zip(before_scores, after_scores))
