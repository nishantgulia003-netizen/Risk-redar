from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Area
from app.schemas.contracts import PopulationResponse
router = APIRouter(tags=["population"])
@router.get("/population/{location}", response_model=PopulationResponse)
def population(location: str = Path(min_length=1, max_length=200), db: Session = Depends(get_db)):
    filters = [Area.name.ilike(location)]
    if location.isdigit():
        filters.append(Area.id == int(location))
    area = db.scalar(select(Area).where(or_(*filters)))
    if area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"area_id": str(area.id), "population": area.population, "elderly_pct": area.elderly_pct, "children_pct": area.children_pct}
