from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Area, Shelter as ShelterModel
from app.schemas.contracts import RecommendedShelter, Shelter
from app.services.site_ranking import rank_shelters
router = APIRouter(tags=["shelters"])
@router.get("/shelters", response_model=list[Shelter])
def shelters(db: Session = Depends(get_db)):
    result = []
    for shelter in db.scalars(select(ShelterModel)):
        point = to_shape(shelter.geometry)
        result.append({"shelter_id": str(shelter.id), "name": shelter.name, "capacity": shelter.capacity, "lat": point.y, "lon": point.x, "medical_facility": shelter.medical_facility, "water_available": shelter.water_available})
    return result
@router.get("/shelters/recommended", response_model=list[RecommendedShelter])
def recommended_shelters(area_id: int = Query(gt=0), db: Session = Depends(get_db)):
    area = db.get(Area, area_id)
    if area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return [{"shelter_id": str(item.shelter.id), "suitability_score": item.suitability_score, "justification": item.justification} for item in rank_shelters(db, area)]
