from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import engine, get_db
from app.schemas.contracts import RelocationPlanItem
from app.services.risk_service import load_risk_zone_features
from app.services.relocation_service import build_relocation_plan
router = APIRouter(tags=["relocation"])
@router.get("/relocation-plan", response_model=list[RelocationPlanItem])
def relocation_plan(db: Session = Depends(get_db)):
    risks = [feature["properties"] for feature in load_risk_zone_features(engine)]
    return build_relocation_plan(db, risks).plan
