"""Frontend-facing response contract checks without requiring a database reset."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.api import health, relocation, reports, risk, routes, shelters, simulate
from app.schemas.contracts import (
    HealthResponse,
    RelocationPlanItem,
    RiskMeterLeaderboardItem,
    RiskMeterResponse,
    RiskProperties,
    RiskZoneCollection,
    RouteResponse,
    SafetyReportResponse,
    SafetyStatusResponse,
    Shelter,
    SimulationResponse,
)
from app.models import Shelter as ShelterModel


def test_health_contract():
    assert HealthResponse.model_validate(health.health()).status == "ok"


def test_risk_zone_contract_preserves_engine_breakdown(monkeypatch):
    feature = {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [[[77.5, 12.9], [77.6, 12.9], [77.5, 12.9]]]},
        "properties": {"area_id": "1", "risk_score": 80.0, "hazard": "flood", "population": 100, "vulnerability": 0.3, "priority": "IMMEDIATE", "breakdown": {"hazard_intensity": 40.0}},
    }
    monkeypatch.setattr(risk, "load_risk_zone_features", lambda _: [feature])
    response = risk.risk_zones()
    assert RiskZoneCollection.model_validate(response).features[0].properties.breakdown["hazard_intensity"] == 40.0


def test_shelter_contract_uses_geojson_and_preserves_legacy_coordinates():
    payload = {
        "shelter_id": "1", "name": "Camp", "capacity": 100, "lat": 12.9, "lon": 77.5,
        "geometry": {"type": "Point", "coordinates": [77.5, 12.9]},
        "medical_facility": True, "water_available": True, "safety_status": "safe",
    }
    shelter = Shelter.model_validate(payload)
    assert shelter.geometry.coordinates == [77.5, 12.9]
    assert (shelter.lat, shelter.lon) == (12.9, 77.5)


def test_shelters_endpoint_returns_geojson_and_safety_status(monkeypatch):
    model = ShelterModel(
        id=1, name="Camp", geometry=from_shape(Point(77.5, 12.9), srid=4326), capacity=100,
        medical_facility=True, water_available=True, road_accessible=True,
    )
    db = SimpleNamespace(scalars=lambda _statement: [model])
    monkeypatch.setattr(shelters, "resolve_target", lambda *_: SimpleNamespace(status="safe"))
    response = shelters.shelters(db)
    assert Shelter.model_validate(response[0]).geometry.coordinates == [77.5, 12.9]


def test_recommended_shelter_contract():
    from app.schemas.contracts import RecommendedShelter
    assert RecommendedShelter.model_validate({"shelter_id": "1", "suitability_score": 91.5, "justification": "Safe and nearby."}).shelter_id == "1"


def test_normal_and_live_route_contracts_are_identical():
    payload = {"distance_km": 2.4, "eta_minutes": 4, "passes_hazard_zone": False, "geometry": {"type": "LineString", "coordinates": [[77.5, 12.9], [77.6, 13.0]]}}
    assert RouteResponse.model_validate(payload) == RouteResponse.model_validate(payload)


def test_live_route_rejects_an_unsafe_shelter_destination(monkeypatch):
    db = SimpleNamespace(get=lambda _model, _identifier: object())
    monkeypatch.setattr(routes, "resolve_target", lambda *_: SimpleNamespace(status="unsafe"))
    with pytest.raises(HTTPException) as error:
        routes.live_route(12.9, 77.5, 1, db)
    assert error.value.status_code == 409


def test_report_and_safety_contracts_include_serializable_fields():
    report = SafetyReportResponse.model_validate({
        "id": 1, "target_type": "area", "target_id": 1, "source_type": "user", "status": "unsafe",
        "description": None, "reporter_id": "device", "latitude": 12.9, "longitude": 77.5,
        "created_at": "2026-09-27T12:00:00Z",
    })
    status = SafetyStatusResponse.model_validate({"target_type": "area", "target_id": 1, "status": "unconfirmed", "confidence": 0.15, "contributing_report_count": 1})
    assert report.created_at.isoformat().endswith("+00:00")
    assert status.status == "unconfirmed"


def test_relocation_and_simulation_contracts_allow_explicit_nulls():
    plan = RelocationPlanItem.model_validate({"area_id": "1", "priority": "HIGH", "assigned_shelter_id": None, "route_id": None, "unassigned_reason": "No capacity"})
    simulation = SimulationResponse.model_validate({
        "hazard": "flood", "increase_pct": 25, "before": {"risk_zones": {"total_areas": 1, "high_priority_areas": 0, "immediate_areas": 0, "average_risk_score": 10}, "relocation_plan": [], "shelter_capacity_utilization": []},
        "after": {"risk_zones": {"total_areas": 1, "high_priority_areas": 1, "immediate_areas": 0, "average_risk_score": 50}, "relocation_plan": [], "shelter_capacity_utilization": []},
        "delta": {"areas_upgraded_to_immediate": [], "total_population_at_immediate_risk": {"before": 0, "after": 0}, "shelters_now_over_capacity": []},
    })
    assert plan.assigned_shelter_id is None
    assert simulation.after.risk_zones.average_risk_score == 50


def test_safety_meter_contracts_are_consistent_and_sortable():
    first = RiskMeterLeaderboardItem.model_validate({"target_id": 1, "target_name": "Area 1", "score": 75, "band": "critical", "report_count": 1, "last_report_at": None})
    second = RiskMeterResponse.model_validate({"score": 0, "band": "low", "report_count": 0, "last_report_at": None})
    assert first.score > second.score
