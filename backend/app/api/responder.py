"""Responder workflow endpoints.

TODO(production): The verification and dispatch-status endpoints MUST require
authenticated responder/admin authorization before production deployment.
"""

from geoalchemy2.shape import to_shape
from fastapi import APIRouter, Depends, HTTPException
from shapely.geometry import mapping
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import engine, get_db
from app.models import Area, RoadSegment, SafetyReport, Shelter
from app.schemas.contracts import (
    DispatchStatusRequest,
    DispatchStatusResponse,
    PendingResponderReport,
    ResponderOverviewResponse,
    ResponderReportVerification,
    ResponderVerifyRequest,
)
from app.services.relocation_service import build_relocation_plan
from app.services.risk_service import load_risk_zone_features
from app.services.safety_status import decayed_weight, resolve_target
from app.services.site_ranking import _distance_km

router = APIRouter(prefix="/responder", tags=["responder"])
_TARGET_MODELS = {"road_segment": RoadSegment, "shelter": Shelter, "area": Area}


def _target_name(db: Session, report: SafetyReport) -> str | None:
    if report.target_id is None:
        return None
    target = db.get(_TARGET_MODELS[report.target_type], report.target_id)
    if target is None:
        return None
    if report.target_type == "road_segment":
        return f"Road segment {target.id}"
    return target.name


def _serialize_report(db: Session, report: SafetyReport) -> dict:
    return {
        "id": report.id,
        "target_type": report.target_type,
        "target_id": report.target_id,
        "target_name": _target_name(db, report),
        "source_type": report.source_type,
        "status": report.status,
        "description": report.description,
        "reporter_id": report.reporter_id,
        "latitude": report.latitude,
        "longitude": report.longitude,
        "created_at": report.created_at,
        "effective_trust_weight": round(decayed_weight(report), 4),
        "is_verified": report.is_verified,
        "verification_decision": report.verification_decision,
        "verified_by": report.verified_by,
    }


@router.get("/overview", response_model=ResponderOverviewResponse)
def responder_overview(db: Session = Depends(get_db)):
    """Return all responder dashboard data in one consistent request."""
    features = load_risk_zone_features(engine)
    risks = {int(feature["properties"]["area_id"]): feature["properties"] for feature in features}
    plan = build_relocation_plan(db, list(risks.values()))
    utilization = {int(item["shelter_id"]): item for item in plan.utilization}
    shelters = list(db.scalars(select(Shelter)))
    shelter_rows: list[dict] = []
    safe_shelters: list[Shelter] = []
    for shelter in shelters:
        capacity = utilization.get(shelter.id, {"allocated": 0, "remaining_capacity": shelter.capacity})
        occupancy = capacity["allocated"]
        status = resolve_target(db, "shelter", shelter.id).status
        if status != "unsafe":
            safe_shelters.append(shelter)
        shelter_rows.append({
            "id": shelter.id,
            "name": shelter.name,
            "geometry": mapping(to_shape(shelter.geometry)),
            "capacity": shelter.capacity,
            "current_occupancy": occupancy,
            "occupancy_pct": round(occupancy / shelter.capacity * 100, 2) if shelter.capacity else 0.0,
            "safety_status": status,
        })
    areas: list[dict] = []
    for area in db.scalars(select(Area)):
        risk = risks.get(area.id)
        if risk is None:
            continue
        area_shape = to_shape(area.geometry)
        nearest = min(safe_shelters, key=lambda shelter: _distance_km(area_shape.centroid, to_shape(shelter.geometry)), default=None)
        nearest_summary = None
        if nearest is not None:
            capacity = utilization.get(nearest.id, {"allocated": 0, "remaining_capacity": nearest.capacity})
            nearest_summary = {
                "shelter_id": nearest.id,
                "shelter_name": nearest.name,
                "capacity": nearest.capacity,
                "current_occupancy": capacity["allocated"],
                "remaining_capacity": capacity["remaining_capacity"],
            }
        areas.append({
            "id": area.id,
            "name": area.name,
            "geometry": mapping(area_shape),
            "centroid": mapping(area_shape.centroid),
            "population": area.population,
            "risk_score": risk["risk_score"],
            "risk_priority": risk["priority"],
            "dispatch_status": area.dispatch_status,
            "nearest_shelter": nearest_summary,
        })
    return {"areas": areas, "shelters": shelter_rows}


@router.get("/pending-reports", response_model=list[PendingResponderReport])
def pending_reports(db: Session = Depends(get_db)):
    reports = db.scalars(
        select(SafetyReport)
        .where(SafetyReport.is_verified.is_(False))
        .order_by(SafetyReport.created_at.desc())
    )
    return [_serialize_report(db, report) for report in reports]


@router.post("/reports/{report_id}/verify", response_model=ResponderReportVerification)
def verify_report(report_id: int, payload: ResponderVerifyRequest, db: Session = Depends(get_db)):
    report = db.get(SafetyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Safety report not found")
    report.is_verified = True
    report.verified_by = payload.responder_name
    report.verification_decision = payload.decision
    db.commit()
    db.refresh(report)
    return _serialize_report(db, report)


@router.patch("/areas/{area_id}/dispatch-status", response_model=DispatchStatusResponse)
def update_dispatch_status(area_id: int, payload: DispatchStatusRequest, db: Session = Depends(get_db)):
    area = db.get(Area, area_id)
    if area is None:
        raise HTTPException(status_code=404, detail="Area not found")
    area.dispatch_status = payload.status
    db.commit()
    db.refresh(area)
    return {"id": area.id, "name": area.name, "dispatch_status": area.dispatch_status}
