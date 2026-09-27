/**
 * RiskRadar API Contracts & Schema Types.
 * Strictly aligned with FastAPI/Pydantic schemas in backend/app/schemas/contracts.py.
 */

export type RiskPriority = "IMMEDIATE" | "HIGH" | "MODERATE" | "SAFE";

export type OperationalStatus = "SAFE" | "MODERATE" | "HIGH" | "CRITICAL";

export type HazardType = "flood" | "rainfall" | "landslide";

export interface GeoJSONPolygon {
  type: "Polygon";
  coordinates: number[][][]; // [lon, lat]
}

export interface GeoJSONPoint {
  type: "Point";
  coordinates: [number, number]; // [lon, lat]
}

export interface GeoJSONLineString {
  type: "LineString";
  coordinates: [number, number][]; // [lon, lat]
}

export interface RiskProperties {
  area_id: string;
  risk_score: number;
  hazard: string;
  population: number;
  vulnerability: number;
  priority: RiskPriority;
  breakdown: Record<string, number>;
  _area_name?: string;
}

export interface RiskFeature {
  type: "Feature";
  geometry: GeoJSONPolygon;
  properties: RiskProperties;
}

export interface RiskZoneCollection {
  type: "FeatureCollection";
  features: RiskFeature[];
}

export interface PopulationResponse {
  area_id: string;
  population: number;
  elderly_pct: number;
  children_pct: number;
}

export interface Shelter {
  shelter_id: string;
  name: string;
  capacity: number;
  lat: number;
  lon: number;
  geometry?: GeoJSONPoint;
  medical_facility: boolean;
  water_available: boolean;
  safety_status?: "safe" | "unsafe" | "unconfirmed";
  allocated?: number;
  remaining_capacity?: number;
}

export interface RecommendedShelter {
  shelter_id: string;
  suitability_score: number;
  justification: string;
}

export interface RouteResponse {
  distance_km: number;
  eta_minutes: number;
  passes_hazard_zone: boolean;
  geometry: GeoJSONLineString;
}

export interface RelocationPlanItem {
  area_id: string;
  priority: RiskPriority | string;
  assigned_shelter_id: string | null;
  route_id: string | null;
  unassigned_reason?: string | null;
}

export interface SimulationRequest {
  hazard: HazardType;
  increase_pct: number;
}

export interface RiskZonesSummary {
  total_areas: number;
  high_priority_areas: number;
  immediate_areas: number;
  average_risk_score: number;
}

export interface ShelterCapacityUtilization {
  shelter_id: string;
  capacity: number;
  allocated: number;
  remaining_capacity: number;
  utilization_pct: number;
  over_capacity: boolean;
}

export interface SimulationState {
  risk_zones: RiskZonesSummary;
  relocation_plan: RelocationPlanItem[];
  shelter_capacity_utilization: ShelterCapacityUtilization[];
}

export interface PopulationAtImmediateRisk {
  before: number;
  after: number;
}

export interface SimulationDelta {
  areas_upgraded_to_immediate: string[];
  total_population_at_immediate_risk: PopulationAtImmediateRisk;
  shelters_now_over_capacity: string[];
}

export interface SimulationResponse {
  hazard: string;
  increase_pct: number;
  before: SimulationState;
  after: SimulationState;
  delta: SimulationDelta;
}

export interface AskAIRequest {
  question: string;
}

export interface AskAIResponse {
  answer: string;
  sources: Record<string, unknown>;
}

export interface SafetyReportCreate {
  target_type: "road_segment" | "shelter" | "area";
  target_id?: number | null;
  source_type: "police" | "rescue_team" | "news" | "user";
  status: "unsafe" | "safe" | "blocked" | "clear";
  description?: string | null;
  reporter_id?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface SafetyReportResponse extends SafetyReportCreate {
  id: number;
  created_at: string;
}

export interface SafetyStatusResponse {
  target_type: "road_segment" | "shelter" | "area";
  target_id: number;
  status: "safe" | "unsafe" | "unconfirmed";
  confidence: number;
  contributing_report_count: number;
}

export type RiskMeterBand = "low" | "rising" | "elevated" | "critical";

export interface RiskMeterResponse {
  score: number;
  band: RiskMeterBand;
  report_count: number;
  last_report_at: string | null;
}

export interface RiskMeterLeaderboardItem extends RiskMeterResponse {
  target_id: number;
  target_name: string;
}

export interface ResponderShelterSummary {
  shelter_id: number;
  shelter_name: string;
  capacity: number;
  current_occupancy: number;
  remaining_capacity: number;
}

export interface ResponderAreaOverview {
  id: number;
  name: string;
  geometry: Record<string, unknown>;
  centroid: Record<string, unknown>;
  population: number;
  risk_score: number;
  risk_priority: RiskPriority;
  dispatch_status: "none" | "dispatched" | "in_progress" | "resolved";
  nearest_shelter: ResponderShelterSummary | null;
}

export interface ResponderShelterOverview {
  id: number;
  name: string;
  geometry: Record<string, unknown>;
  capacity: number;
  current_occupancy: number;
  occupancy_pct: number;
  safety_status: "safe" | "unsafe" | "unconfirmed";
}

export interface ResponderOverviewResponse {
  areas: ResponderAreaOverview[];
  shelters: ResponderShelterOverview[];
}

export interface PendingResponderReport {
  id: number;
  target_type: "road_segment" | "shelter" | "area";
  target_id: number | null;
  target_name: string | null;
  source_type: "police" | "rescue_team" | "news" | "user";
  status: "unsafe" | "safe" | "blocked" | "clear";
  description: string | null;
  reporter_id: string | null;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
  effective_trust_weight: number;
  is_verified: boolean;
  verification_decision: "confirm" | "dismiss" | null;
}

export interface ResponderReportVerification extends PendingResponderReport {
  verified_by: string | null;
}

export interface DispatchStatusRequest {
  status: "none" | "dispatched" | "in_progress" | "resolved";
}

export interface DispatchStatusResponse {
  id: number;
  name: string;
  dispatch_status: "none" | "dispatched" | "in_progress" | "resolved";
}

export interface HealthResponse {
  status: "ok";
  service: "riskradar-api";
}
