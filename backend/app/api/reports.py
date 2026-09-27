from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Area, RoadSegment, SafetyReport, Shelter
from app.schemas.contracts import RiskMeterLeaderboardItem, RiskMeterResponse, SafetyReportCreate, SafetyReportResponse, SafetyStatusResponse
from app.services.safety_status import get_risk_meter, resolve_target

router = APIRouter(tags=["safety reports"])
_TARGET_MODELS = {"road_segment": RoadSegment, "shelter": Shelter, "area": Area}


@router.post("/reports", response_model=SafetyReportResponse, status_code=201)
def create_report(payload: SafetyReportCreate, db: Session = Depends(get_db)):
    # Production must authenticate/verify police, rescue_team and news sources;
    # this demo accepts them honestly as requested until ingestion auth exists.
    if payload.target_id is not None and db.get(_TARGET_MODELS[payload.target_type], payload.target_id) is None:
        raise HTTPException(status_code=404, detail="Report target not found")
    report = SafetyReport(**payload.model_dump())
    db.add(report); db.commit(); db.refresh(report)
    return report


@router.get("/safety-status", response_model=SafetyStatusResponse)
def safety_status(target_type: str = Query(pattern="^(road_segment|shelter|area)$"), target_id: int = Query(gt=0), db: Session = Depends(get_db)):
    if db.get(_TARGET_MODELS[target_type], target_id) is None:
        raise HTTPException(status_code=404, detail="Target not found")
    resolved = resolve_target(db, target_type, target_id)
    return {"target_type": target_type, "target_id": target_id, **resolved.__dict__}


@router.get("/safety-status/summary", response_model=list[SafetyStatusResponse])
def safety_status_summary(db: Session = Depends(get_db)):
    pairs = db.execute(select(SafetyReport.target_type, SafetyReport.target_id).where(SafetyReport.target_id.is_not(None)).distinct()).all()
    result = []
    for target_type, target_id in pairs:
        resolved = resolve_target(db, target_type, target_id)
        if resolved.status != "safe": result.append({"target_type": target_type, "target_id": target_id, **resolved.__dict__})
    return result


@router.get("/safety-meter", response_model=RiskMeterResponse)
def safety_meter(target_type: str = Query(pattern="^(road_segment|shelter|area)$"), target_id: int = Query(gt=0), db: Session = Depends(get_db)):
    if db.get(_TARGET_MODELS[target_type], target_id) is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return get_risk_meter(db, target_type, target_id).__dict__


@router.get("/safety-meter/leaderboard", response_model=list[RiskMeterLeaderboardItem])
def safety_meter_leaderboard(target_type: str = Query(pattern="^(road_segment|shelter|area)$"), db: Session = Depends(get_db)):
    model = _TARGET_MODELS[target_type]
    rows = []
    for target in db.scalars(select(model)):
        meter = get_risk_meter(db, target_type, target.id)
        target_name = f"Road segment {target.id}" if target_type == "road_segment" else target.name
        rows.append({"target_id": target.id, "target_name": target_name, **meter.__dict__})
    return sorted(rows, key=lambda row: row["score"], reverse=True)
