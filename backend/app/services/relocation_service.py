"""Capacity-safe relocation planning shared by the API and simulations."""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Area, Shelter
from app.services.routing import compute_safe_route
from app.services.safety_status import unsafe_target_ids
from app.services.site_ranking import rank_shelters


@dataclass(frozen=True)
class RelocationPlanResult:
    plan: list[dict]
    utilization: list[dict]


def build_relocation_plan(session: Session, risk_properties: list[dict]) -> RelocationPlanResult:
    """Allocate in priority order using only an in-memory capacity ledger."""
    unsafe_shelters = unsafe_target_ids(session, "shelter")
    shelters = [shelter for shelter in session.query(Shelter).all() if shelter.id not in unsafe_shelters]
    remaining_capacity = {shelter.id: shelter.capacity for shelter in shelters}
    plan: list[dict] = []
    for risk in sorted((item for item in risk_properties if item["priority"] != "SAFE"), key=lambda item: item["risk_score"], reverse=True):
        area = session.get(Area, int(risk["area_id"]))
        if area is None:
            continue
        candidates = [item for item in rank_shelters(session, area, remaining_capacity) if remaining_capacity[item.shelter.id] >= area.population]
        if not candidates:
            plan.append({"area_id": str(area.id), "priority": risk["priority"], "assigned_shelter_id": None, "route_id": None, "unassigned_reason": "No shelter has enough remaining capacity for this area's population."})
            continue
        selected = candidates[0].shelter
        try:
            compute_safe_route(session, area.geometry, selected.geometry)
        except ValueError:
            plan.append({"area_id": str(area.id), "priority": risk["priority"], "assigned_shelter_id": None, "route_id": None, "unassigned_reason": "No safe road route connects this area to an eligible shelter."})
            continue
        remaining_capacity[selected.id] -= area.population
        plan.append({"area_id": str(area.id), "priority": risk["priority"], "assigned_shelter_id": str(selected.id), "route_id": f"route-area-{area.id}-shelter-{selected.id}", "unassigned_reason": None})
    utilization = [{"shelter_id": str(shelter.id), "capacity": shelter.capacity, "allocated": shelter.capacity - remaining_capacity[shelter.id], "remaining_capacity": remaining_capacity[shelter.id], "utilization_pct": round((shelter.capacity - remaining_capacity[shelter.id]) / shelter.capacity * 100, 2) if shelter.capacity > 0 else 0.0, "over_capacity": remaining_capacity[shelter.id] < 0} for shelter in shelters]
    return RelocationPlanResult(plan=plan, utilization=utilization)
