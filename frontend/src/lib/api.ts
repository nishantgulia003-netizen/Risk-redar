import type {
  AskAIRequest,
  AskAIResponse,
  DispatchStatusRequest,
  DispatchStatusResponse,
  HazardType,
  HealthResponse,
  PendingResponderReport,
  PopulationResponse,
  RecommendedShelter,
  RelocationPlanItem,
  ResponderOverviewResponse,
  ResponderReportVerification,
  RiskFeature,
  RiskMeterLeaderboardItem,
  RiskMeterResponse,
  RiskPriority,
  RiskProperties,
  RiskZoneCollection,
  RouteResponse,
  SafetyReportCreate,
  SafetyReportResponse,
  SafetyStatusResponse,
  Shelter,
  SimulationRequest,
  SimulationResponse,
} from "../types/api";

// Re-export contracts for seamless component imports
export * from "../types/api";

// Backward-compatible type aliases for existing pages
export type Priority = RiskPriority;
export type Risk = RiskProperties;
export type Feature = RiskFeature;
export type Plan = RelocationPlanItem;
export type Route = RouteResponse;
export type AskAI = AskAIResponse;

// Centralized API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status?: number;
  details?: unknown;

  constructor(message: string, status?: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...options?.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });
    
    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      let errorDetails: unknown = null;
      try {
        const errorJson = await response.json();
        errorDetails = errorJson;
        if (typeof errorJson?.detail === "string") {
          errorMessage = errorJson.detail;
        } else if (Array.isArray(errorJson?.detail) && errorJson.detail[0]?.msg) {
          errorMessage = errorJson.detail[0].msg;
        }
      } catch {
        // Response was not JSON
      }
      throw new ApiError(errorMessage, response.status, errorDetails);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    const message = error instanceof Error ? error.message : "Network error. Please verify backend connection.";
    throw new ApiError(message);
  }
}

// -------------------------------------------------------------
// Core Disaster Intelligence Endpoints
// -------------------------------------------------------------

export const getHealth = () => request<HealthResponse>("/health");

export const getRiskZones = () => request<RiskZoneCollection>("/risk-zones");

export const getRiskByLocation = (location: string) =>
  request<RiskProperties>(`/risk/${encodeURIComponent(location)}`);

export const getPopulationByLocation = (location: string) =>
  request<PopulationResponse>(`/population/${encodeURIComponent(location)}`);

export const getShelters = () => request<Shelter[]>("/shelters");

export const getRecommendedShelters = (areaId: number) =>
  request<RecommendedShelter[]>(`/shelters/recommended?area_id=${encodeURIComponent(areaId)}`);

export const getRelocationPlan = () => request<RelocationPlanItem[]>("/relocation-plan");

export const getSafeRoute = (fromId: string, toId: string) =>
  request<RouteResponse>(`/routes?from_id=${encodeURIComponent(fromId)}&to_id=${encodeURIComponent(toId)}`);

export const postSimulate = (hazard: HazardType, increase_pct: number) =>
  request<SimulationResponse>("/simulate", {
    method: "POST",
    body: JSON.stringify({ hazard, increase_pct } satisfies SimulationRequest),
  });

export const postAskAI = (question: string) =>
  request<AskAIResponse>("/ask-ai", {
    method: "POST",
    body: JSON.stringify({ question } satisfies AskAIRequest),
  });

// -------------------------------------------------------------
// Safety Reports & Status Endpoints
// -------------------------------------------------------------

export const postSafetyReport = (payload: SafetyReportCreate) =>
  request<SafetyReportResponse>("/reports", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getSafetyStatus = (targetType: "road_segment" | "shelter" | "area", targetId: number) =>
  request<SafetyStatusResponse>(`/safety-status?target_type=${targetType}&target_id=${targetId}`);

export const getSafetyStatusSummary = () =>
  request<SafetyStatusResponse[]>("/safety-status/summary");

export const getSafetyMeter = (targetType: "road_segment" | "shelter" | "area", targetId: number) =>
  request<RiskMeterResponse>(`/safety-meter?target_type=${targetType}&target_id=${targetId}`);

export const getSafetyMeterLeaderboard = (targetType: "road_segment" | "shelter" | "area") =>
  request<RiskMeterLeaderboardItem[]>(`/safety-meter/leaderboard?target_type=${targetType}`);

// -------------------------------------------------------------
// Responder Operations Endpoints
// -------------------------------------------------------------

export const getResponderOverview = () =>
  request<ResponderOverviewResponse>("/responder/overview");

export const getPendingResponderReports = () =>
  request<PendingResponderReport[]>("/responder/reports/pending");

export const postVerifyResponderReport = (
  reportId: number,
  decision: "confirm" | "dismiss",
  responderName: string
) =>
  request<ResponderReportVerification>(`/responder/reports/${reportId}/verify`, {
    method: "POST",
    body: JSON.stringify({ decision, responder_name: responderName }),
  });

export const putDispatchStatus = (
  areaId: number,
  status: DispatchStatusRequest["status"]
) =>
  request<DispatchStatusResponse>(`/responder/areas/${areaId}/dispatch-status`, {
    method: "PUT",
    body: JSON.stringify({ status } satisfies DispatchStatusRequest),
  });
