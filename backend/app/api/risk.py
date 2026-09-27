from fastapi import APIRouter, HTTPException, Path
from app.db.session import engine
from app.schemas.contracts import RiskProperties, RiskZoneCollection
from app.services.risk_service import load_risk_for_location, load_risk_zone_features
router = APIRouter(tags=["risk"])
@router.get("/risk-zones", response_model=RiskZoneCollection)
def risk_zones():
    return {"type": "FeatureCollection", "features": load_risk_zone_features(engine)}
@router.get("/risk/{location}", response_model=RiskProperties)
def risk(location: str = Path(min_length=1, max_length=200)):
    result = load_risk_for_location(engine, location)
    if result is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return result
