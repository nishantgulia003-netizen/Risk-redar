from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Area, Shelter
from app.schemas.contracts import RouteResponse
from app.services.routing import compute_safe_route, recompute_route_from_position
from app.services.safety_status import resolve_target
router = APIRouter(tags=["routes"])

def _location_record(db: Session, location_id: str):
    """Resolve area/shelter identifiers without losing destination type."""
    if ":" not in location_id and "-" in location_id:
        possible_prefix, possible_id = location_id.rsplit("-", 1)
        if possible_prefix.casefold() in {"area", "shelter"}:
            location_id = f"{possible_prefix}:{possible_id}"
    prefix, separator, raw_id = location_id.partition(":")
    if separator:
        model = Area if prefix.casefold() == "area" else Shelter if prefix.casefold() == "shelter" else None
        if model is None or not raw_id.isdigit():
            return None
        return db.get(model, int(raw_id))
    if location_id.isdigit():
        record = db.get(Area, int(location_id)) or db.get(Shelter, int(location_id))
        return record
    area = db.scalar(select(Area).where(Area.name.ilike(location_id)))
    if area:
        return area
    shelter = db.scalar(select(Shelter).where(Shelter.name.ilike(location_id)))
    return shelter

@router.get("/routes", response_model=RouteResponse)
def route(from_id: str = Query(min_length=1, max_length=200), to_id: str = Query(min_length=1, max_length=200), db: Session = Depends(get_db)):
    origin, destination = _location_record(db, from_id), _location_record(db, to_id)
    if origin is None or destination is None:
        raise HTTPException(status_code=404, detail="Origin or destination not found; use area:<id> or shelter:<id>")
    if isinstance(destination, Shelter) and resolve_target(db, "shelter", destination.id).status == "unsafe":
        raise HTTPException(status_code=409, detail="Destination shelter is currently unsafe")
    try:
        result = compute_safe_route(db, origin.geometry, destination.geometry)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"distance_km": result.distance_km, "eta_minutes": result.eta_minutes, "passes_hazard_zone": result.passes_hazard_zone, "geometry": {"type": "LineString", "coordinates": result.coordinates}}

@router.get("/routes/live", response_model=RouteResponse)
def live_route(lat: float = Query(ge=-90, le=90), lng: float = Query(ge=-180, le=180), shelter_id: int = Query(gt=0), db: Session = Depends(get_db)):
    shelter = db.get(Shelter, shelter_id)
    if shelter is None:
        raise HTTPException(status_code=404, detail="Shelter not found")
    if resolve_target(db, "shelter", shelter_id).status == "unsafe":
        raise HTTPException(status_code=409, detail="Destination shelter is currently unsafe")
    try:
        result = recompute_route_from_position(db, lat, lng, shelter_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"distance_km": result.distance_km, "eta_minutes": result.eta_minutes, "passes_hazard_zone": result.passes_hazard_zone, "geometry": {"type": "LineString", "coordinates": result.coordinates}}
