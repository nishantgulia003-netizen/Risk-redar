from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from geoalchemy2.shape import from_shape
from pydantic import ValidationError
from shapely.geometry import Point, Polygon

from app.api import responder
from app.models import Area, SafetyReport, Shelter
from app.schemas.contracts import DispatchStatusRequest, ResponderVerifyRequest
from app.services.safety_status import resolve_reports


NOW = datetime(2026, 9, 27, 12, 0, tzinfo=timezone.utc)


class Scalars:
    def __init__(self, rows):
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)


class Session:
    def __init__(self, *, areas=(), shelters=(), reports=()):
        self.areas, self.shelters, self.reports = list(areas), list(shelters), list(reports)
        self.committed = False

    def scalars(self, statement):
        sql = str(statement)
        if "safety_reports" in sql:
            return Scalars(sorted((report for report in self.reports if not report.is_verified), key=lambda report: report.created_at, reverse=True))
        if "shelters" in sql:
            return Scalars(self.shelters)
        return Scalars(self.areas)

    def get(self, model, identifier):
        rows = self.areas if model is Area else self.shelters if model is Shelter else self.reports
        return next((item for item in rows if item.id == identifier), None)

    def commit(self):
        self.committed = True

    def refresh(self, _item):
        pass


def area(identifier=1):
    return Area(id=identifier, name=f"Area {identifier}", geometry=from_shape(Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), srid=4326), population=100, elderly_pct=10, children_pct=20, historical_disaster_count=1, dispatch_status="none")


def shelter(identifier=1):
    return Shelter(id=identifier, name=f"Shelter {identifier}", geometry=from_shape(Point(0.5, 0.5), srid=4326), capacity=200, medical_facility=True, water_available=True, road_accessible=True)


def safety_report(identifier, *, created_at=NOW, verified=False):
    return SafetyReport(id=identifier, target_type="area", target_id=1, source_type="user", status="unsafe", reporter_id=f"device-{identifier}", latitude=12.9, longitude=77.5, created_at=created_at, is_verified=verified)


def test_overview_returns_areas_and_shelters_in_one_payload(monkeypatch):
    db = Session(areas=[area()], shelters=[shelter()])
    monkeypatch.setattr(responder, "load_risk_zone_features", lambda _: [{"properties": {"area_id": "1", "risk_score": 70.0, "priority": "HIGH"}}])
    monkeypatch.setattr(responder, "build_relocation_plan", lambda *_: type("Plan", (), {"utilization": [{"shelter_id": "1", "allocated": 25, "remaining_capacity": 175}]})())
    monkeypatch.setattr(responder, "resolve_target", lambda *_: type("Status", (), {"status": "safe"})())
    result = responder.responder_overview(db)
    assert result["areas"][0]["name"] == "Area 1"
    assert result["shelters"][0]["current_occupancy"] == 25


def test_pending_reports_returns_only_unverified_and_newest_first():
    old = safety_report(1, created_at=NOW - timedelta(minutes=5))
    new = safety_report(2)
    verified = safety_report(3, verified=True)
    result = responder.pending_reports(Session(reports=[old, verified, new]))
    assert [item["id"] for item in result] == [2, 1]


def test_confirm_and_dismiss_preserve_reports_and_update_fields():
    report = safety_report(1)
    db = Session(reports=[report])
    confirmed = responder.verify_report(1, ResponderVerifyRequest(decision="confirm", responder_name="Asha"), db)
    assert (confirmed["is_verified"], confirmed["verification_decision"], confirmed["verified_by"]) == (True, "confirm", "Asha")
    assert resolve_reports([report], latitude=12.9, longitude=77.5, now=NOW).status == "unsafe"
    dismissed_report = safety_report(2)
    db.reports.append(dismissed_report)
    dismissed = responder.verify_report(2, ResponderVerifyRequest(decision="dismiss", responder_name="Asha"), db)
    assert dismissed["verification_decision"] == "dismiss"
    assert dismissed_report in db.reports


def test_dispatch_status_validation_not_found_and_update():
    with pytest.raises(ValidationError):
        DispatchStatusRequest(status="invalid")
    with pytest.raises(HTTPException) as missing:
        responder.update_dispatch_status(99, DispatchStatusRequest(status="dispatched"), Session())
    assert missing.value.status_code == 404
    db = Session(areas=[area()])
    result = responder.update_dispatch_status(1, DispatchStatusRequest(status="in_progress"), db)
    assert result["dispatch_status"] == "in_progress"
    assert db.committed


def test_risk_meter_leaderboard_is_sorted_descending(monkeypatch):
    db = Session(areas=[area(1), area(2)])
    scores = {1: 15.0, 2: 80.0}
    from app.api import reports
    monkeypatch.setattr(reports, "get_risk_meter", lambda _db, _type, target_id: SimpleNamespace(score=scores[target_id], band="critical", report_count=1, last_report_at=NOW))
    result = reports.safety_meter_leaderboard("area", db)
    assert [item["target_id"] for item in result] == [2, 1]
