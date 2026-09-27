"""Explainable shelter suitability ranking for a single affected area."""
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Mapping

from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Area, Shelter
from app.services.safety_status import unsafe_target_ids

DEFAULT_SITE_WEIGHTS = {
    "distance": 30.0,
    "capacity": 30.0,
    "medical_facility": 15.0,
    "water_available": 15.0,
    "road_accessible": 10.0,
}


@dataclass(frozen=True)
class RankedShelter:
    shelter: Shelter
    suitability_score: float
    justification: str


def _distance_km(first, second) -> float:
    """Great-circle distance for WGS84 point/centroid coordinates."""
    lon1, lat1, lon2, lat2 = map(radians, (first.x, first.y, second.x, second.y))
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(a))


def rank_shelters(session: Session, area: Area, remaining_capacity: Mapping[int, int] | None = None, weights: Mapping[str, float] | None = None) -> list[RankedShelter]:
    """Rank all shelters using live capacity; population is the conservative affected-population proxy."""
    ranking_weights = dict(DEFAULT_SITE_WEIGHTS)
    if weights:
        unknown = set(weights) - set(DEFAULT_SITE_WEIGHTS)
        if unknown:
            raise ValueError(f"Unknown site-ranking weights: {sorted(unknown)}")
        ranking_weights.update(weights)
    if round(sum(ranking_weights.values()), 8) != 100:
        raise ValueError("Site-ranking weights must sum to 100")
    unsafe_shelters = unsafe_target_ids(session, "shelter")
    shelters = [shelter for shelter in session.scalars(select(Shelter)) if shelter.id not in unsafe_shelters]
    if not shelters:
        return []
    area_center = to_shape(area.geometry).centroid
    distances = {shelter.id: _distance_km(area_center, to_shape(shelter.geometry)) for shelter in shelters}
    farthest_km = max(distances.values())
    affected_population = max(1, area.population)
    rankings: list[RankedShelter] = []
    for shelter in shelters:
        available = remaining_capacity.get(shelter.id, shelter.capacity) if remaining_capacity else shelter.capacity
        distance_factor = 1.0 if farthest_km == 0 else 1 - distances[shelter.id] / farthest_km
        factors = {"distance": distance_factor, "capacity": min(1.0, max(0, available) / affected_population), "medical_facility": float(shelter.medical_facility), "water_available": float(shelter.water_available), "road_accessible": float(shelter.road_accessible)}
        score = round(sum(factors[name] * ranking_weights[name] for name in ranking_weights), 2)
        capacity_statement = f"sufficient remaining capacity ({available:,}) for the {affected_population:,} affected residents" if available >= affected_population else f"only {available:,} remaining places for {affected_population:,} affected residents"
        amenities = []
        amenities.append("on-site medical facilities" if shelter.medical_facility else "no on-site medical facility")
        amenities.append("water available" if shelter.water_available else "no confirmed water supply")
        access = "road-accessible" if shelter.road_accessible else "not road-accessible"
        justification = f"{capacity_statement}; it is {distances[shelter.id]:.1f} km from the area, {access}, with {amenities[0]} and {amenities[1]}."
        rankings.append(RankedShelter(shelter=shelter, suitability_score=score, justification=justification))
    return sorted(rankings, key=lambda item: item.suitability_score, reverse=True)
