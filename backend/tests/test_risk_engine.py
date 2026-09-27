from app.services.risk_engine import RiskEngine


def test_high_hazard_high_population_area_is_immediate():
    result = RiskEngine().score(hazard_intensity=1, population_density=1200, elderly_pct=25, children_pct=30, historical_disaster_count=8, max_population_density=1200, max_historical_disaster_count=8)
    assert result.score == 91
    assert result.priority == "IMMEDIATE"
    assert result.breakdown == {"hazard_intensity": 40.0, "population_exposure": 25.0, "vulnerability": 11.0, "historical_risk": 15.0}


def test_low_hazard_low_population_area_is_safe():
    result = RiskEngine().score(hazard_intensity=.05, population_density=10, elderly_pct=2, children_pct=3, historical_disaster_count=0, max_population_density=1000, max_historical_disaster_count=8)
    assert result.score < 40
    assert result.priority == "SAFE"


def test_weight_change_shifts_score_predictably():
    inputs = dict(hazard_intensity=1, population_density=0, elderly_pct=0, children_pct=0, historical_disaster_count=0, max_population_density=100, max_historical_disaster_count=10)
    default_score = RiskEngine().score(**inputs).score
    hazard_focused_score = RiskEngine({"hazard_intensity": 70, "population_exposure": 10, "vulnerability": 10, "historical_risk": 10}).score(**inputs).score
    assert default_score == 40
    assert hazard_focused_score == 70
    assert hazard_focused_score > default_score
