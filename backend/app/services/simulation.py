"""Read-only what-if simulations over in-memory risk-zone projections."""
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.services.relocation_service import build_relocation_plan
from app.services.risk_service import load_risk_zone_features

SUPPORTED_HAZARDS = {"flood", "rainfall", "landslide"}


def increased_intensity_multiplier(increase_pct: float) -> float:
    """Convert a percentage increase into a detached scoring multiplier."""
    return 1 + increase_pct / 100


def _summary(properties: list[dict]) -> dict:
    count = len(properties)
    return {"total_areas": count, "high_priority_areas": sum(item["priority"] in {"HIGH", "IMMEDIATE"} for item in properties), "immediate_areas": sum(item["priority"] == "IMMEDIATE" for item in properties), "average_risk_score": round(sum(item["risk_score"] for item in properties) / count, 2) if count else 0.0}


def _state(session: Session, properties: list[dict]) -> dict:
    relocation = build_relocation_plan(session, properties)
    return {"risk_zones": _summary(properties), "relocation_plan": relocation.plan, "shelter_capacity_utilization": relocation.utilization}


def run_simulation(session: Session, engine: Engine, hazard: str, increase_pct: float) -> dict:
    """Calculate a before/after scenario without writing to HazardLayer or Shelter."""
    if hazard not in SUPPORTED_HAZARDS:
        raise ValueError(f"Unsupported hazard: {hazard}")
    before_properties = [feature["properties"] for feature in load_risk_zone_features(engine)]
    # Only the in-memory GeoPandas intensity column is scaled.  Database values
    # and the capacity ledger both remain untouched after this function returns.
    after_properties = [feature["properties"] for feature in load_risk_zone_features(engine, intensity_multipliers={hazard: increased_intensity_multiplier(increase_pct)})]
    before = _state(session, before_properties)
    after = _state(session, after_properties)
    before_by_area = {item["area_id"]: item for item in before_properties}
    upgraded = [item["area_id"] for item in after_properties if item["priority"] == "IMMEDIATE" and before_by_area[item["area_id"]]["priority"] != "IMMEDIATE"]
    before_immediate_population = sum(item["population"] for item in before_properties if item["priority"] == "IMMEDIATE")
    after_immediate_population = sum(item["population"] for item in after_properties if item["priority"] == "IMMEDIATE")
    over_capacity = [item["shelter_id"] for item in after["shelter_capacity_utilization"] if item["over_capacity"]]
    return {"hazard": hazard, "increase_pct": increase_pct, "before": before, "after": after, "delta": {"areas_upgraded_to_immediate": upgraded, "total_population_at_immediate_risk": {"before": before_immediate_population, "after": after_immediate_population}, "shelters_now_over_capacity": over_capacity}}
