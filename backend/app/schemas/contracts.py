from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

class RiskProperties(BaseModel):
    area_id: str
    risk_score: float = Field(ge=0, le=100)
    hazard: str
    population: int = Field(ge=0)
    vulnerability: float = Field(ge=0, le=1)
    priority: Literal["IMMEDIATE", "HIGH", "MODERATE", "SAFE"]
    breakdown: dict[str, float]

class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]]

class RiskFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONPolygon
    properties: RiskProperties

class RiskZoneCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[RiskFeature]

class PopulationResponse(BaseModel):
    area_id: str
    population: int
    elderly_pct: float
    children_pct: float

class Shelter(BaseModel):
    shelter_id: str
    name: str
    capacity: int
    lat: float
    lon: float
    medical_facility: bool
    water_available: bool

class RecommendedShelter(BaseModel):
    shelter_id: str
    suitability_score: float
    justification: str

class GeoJSONLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]]

class RouteResponse(BaseModel):
    distance_km: float
    eta_minutes: int
    passes_hazard_zone: bool
    geometry: GeoJSONLineString

class RelocationPlanItem(BaseModel):
    area_id: str
    priority: str
    assigned_shelter_id: str | None
    route_id: str | None
    unassigned_reason: str | None = None

class SimulationRequest(BaseModel):
    hazard: Literal["flood", "rainfall", "landslide"]
    increase_pct: float = Field(ge=0, le=1_000)

class RiskZonesSummary(BaseModel):
    total_areas: int
    high_priority_areas: int
    immediate_areas: int
    average_risk_score: float

class ShelterCapacityUtilization(BaseModel):
    shelter_id: str
    capacity: int
    allocated: int
    remaining_capacity: int
    utilization_pct: float
    over_capacity: bool

class SimulationState(BaseModel):
    risk_zones: RiskZonesSummary
    relocation_plan: list[RelocationPlanItem]
    shelter_capacity_utilization: list[ShelterCapacityUtilization]

class PopulationAtImmediateRisk(BaseModel):
    before: int
    after: int

class SimulationDelta(BaseModel):
    areas_upgraded_to_immediate: list[str]
    total_population_at_immediate_risk: PopulationAtImmediateRisk
    shelters_now_over_capacity: list[str]

class SimulationResponse(BaseModel):
    hazard: str
    increase_pct: float
    before: SimulationState
    after: SimulationState
    delta: SimulationDelta

class AskAIRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1_000)

class AskAIResponse(BaseModel):
    answer: str
    sources: dict[str, Any]

class SafetyReportCreate(BaseModel):
    target_type: Literal["road_segment", "shelter", "area"]
    target_id: int | None = Field(default=None, gt=0)
    source_type: Literal["police", "rescue_team", "news", "user"]
    status: Literal["unsafe", "safe", "blocked", "clear"]
    description: str | None = Field(default=None, max_length=5_000)
    reporter_id: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def user_report_needs_coordinates(self):
        if self.source_type == "user" and (self.latitude is None or self.longitude is None):
            raise ValueError("User reports require latitude and longitude for corroboration")
        return self

class SafetyReportResponse(SafetyReportCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}

class SafetyStatusResponse(BaseModel):
    target_type: Literal["road_segment", "shelter", "area"]
    target_id: int
    status: Literal["safe", "unsafe", "unconfirmed"]
    confidence: float = Field(ge=0, le=1)
    contributing_report_count: int = Field(ge=0)
