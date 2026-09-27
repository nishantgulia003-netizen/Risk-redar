# Product Requirement Document (PRD): RiskRadar Command Center Frontend

**Project Name:** RiskRadar  
**Event:** Smart India Hackathon (SIH 2026)  
**Problem Statement ID:** 26191  
**Problem Statement Title:** Intelligent Identification of Hazard-Based Red Zones, Carrying Capacity Assessment, and Immediate Relocation Needs for Vulnerable Habitations  
**Target Platform:** Responsive Web Application (Optimized for Desktop / Command Center displays, 1080p to 4K, with tablet adaptability)  
**Document Status:** Final Specification v1.0  

---

## 1. Executive Summary & Vision

RiskRadar is an intelligent disaster-management decision-support system designed for District Emergency Operation Centers (DEOC), NDRF/SDRF incident commanders, and municipal relief coordinators. 

The frontend transforms complex spatial data, risk metrics, shelter capacities, and evacuation routes into an **actionable, real-time emergency command dashboard**. Instead of static hazard maps, authorities receive instant triage prioritization, clear shelter assignment vectors, what-if surge simulation, and an anti-hallucinating AI operational copilot.

---

## 2. Target User Personas

1. **Incident Commander / District Magistrate (DM):**
   * *Goal:* High-level executive situational awareness, red-zone identification, approving district-wide evacuation orders, and allocating macro relief resources.
   * *Needs:* High-contrast risk heatmaps, immediate casualty/exposure estimates, and clear decision matrices.

2. **Evacuation & Logistics Operations Lead (NDRF / SDRF):**
   * *Goal:* Deploying rescue convoys along safe routes and tracking transit feasibility.
   * *Needs:* Route directions, hazard bypass validation, travel time estimates, and road blockage warnings.

3. **Shelter & Relief Camp Manager:**
   * *Goal:* Managing camp carrying capacity, medical triage, water sanitation, and avoiding dangerous overcrowding.
   * *Needs:* Real-time shelter utilization gauges, capacity deficit warnings, and incoming population rosters.

---

## 3. Technology Stack & Design System

### 3.1 Tech Stack
* **Framework:** React 18+ with TypeScript
* **Build Tool:** Vite
* **Styling & Components:** Tailwind CSS + Radix UI / shadcn/ui primitives + Lucide React icons
* **GIS / Mapping Engine:** Leaflet.js (`react-leaflet`) with CartoDB Dark Matter / OpenStreetMap vector tile providers
* **Charts & Visualizations:** Recharts (for risk score breakdowns and shelter occupancy gauges)
* **Data Fetching & State:** TanStack Query v5 (React Query) for caching and background synchronization, Zustand for local UI states
* **HTTP Client:** Axios with centralized error interception

### 3.2 Design System & Command Center Theme
* **Theme:** Emergency Command Dark Mode (`bg-slate-950`, `bg-slate-900`, `border-slate-800`).
* **Tactical Color Coding (Aligned with Backend & NDMA Standards):**
  * **Critical / Immediate Risk (≥ 80):** Deep Crimson (`#EF4444` / `bg-red-500/20 text-red-400 border-red-500`)
  * **High Risk (60 – 79):** Amber Orange (`#F97316` / `bg-orange-500/20 text-orange-400 border-orange-500`)
  * **Moderate Risk (40 – 59):** Warning Gold (`#EAB308` / `bg-yellow-500/20 text-yellow-400 border-yellow-500`)
  * **Safe / Monitored (< 40):** Emerald Green (`#10B981` / `bg-emerald-500/20 text-emerald-400 border-emerald-500`)
  * **Shelter Markers:** Cyan Blue (`#06B6D4`)
  * **Evacuation Routes:** Neon Indigo (`#6366F1`) / Hazard Alert Route (`#DC2626` dashed)
* **Typography:** `Inter` or `Geist Sans` for UI, `JetBrains Mono` for coordinates, IDs, and tabular figures.

---

## 4. UI Layout & Architecture

The application adopts a **3-Pane Command Center Layout** with a collapsible sidebar and floating contextual drawers:

```
+--------------------------------------------------------------------------------------------------+
| Top Navigation Bar: District Status, Threat Level, Quick Stats, Simulation Badge, System Clock   |
+------------------------------+------------------------------------+------------------------------+
| Left Panel (320px)           | Center Viewport (Flexible)         | Right Panel (380px)          |
|                              |                                    |                              |
| - District Quick Triage      | - Fullscreen GIS Map (Leaflet)     | - Tab 1: Relocation Plan     |
| - Risk Level Filters         |   * GeoJSON Hazard Polygons        | - Tab 2: Shelter Readiness   |
| - Habitation Directory       |   * Shelter Pins & Occupancy Rings | - Tab 3: "What-If" Studio    |
| - Layer Toggles              |   * Evacuation Route Vectors       | - Tab 4: Ask RiskRadar (AI)  |
|                              | - Floating Map Controls            |                              |
|                              | - Bottom Hazard Timeline Bar       |                              |
+------------------------------+------------------------------------+------------------------------+
| Status Footer: PostGIS Engine Status, Latency Indicator, Active Disaster Scenario, Help Modal     |
+--------------------------------------------------------------------------------------------------+
```

---

## 5. Core Functional Modules & Backend API Mapping

### Module 1: Top Navigation & Operational Summary Bar
* **Features:**
  * District indicator (e.g., "Dakshina Kannada / Demo Sector Alpha").
  * Real-time metrics counters:
    * Total Population at Risk (Sum of exposed habitations).
    * Total Habitations in IMMEDIATE State.
    * Total Operational Shelters & District-wide Free Capacity.
  * Live status pill (e.g., `ACTIVE EMERGENCY` vs `MONITORING`).
  * Demo Mode Switch: Button to trigger mock surge scenarios during the presentation.

---

### Module 2: Interactive GIS Red-Zone Map (Center Viewport)
* **Backend Endpoint:** `GET /risk-zones` (Returns GeoJSON `FeatureCollection` with polygon geometries and properties)
* **Requirements:**
  1. **Dynamic Polygon Shading:** Render area boundaries shaded according to their `risk_score` and `priority` (`SAFE`, `MODERATE`, `HIGH`, `IMMEDIATE`).
  2. **Interactive Hover & Click:**
     * *Hover:* Highlight polygon boundary and display tooltip with: `Area Name`, `Risk Score`, `Primary Hazard`.
     * *Click:* Open detailed Habitation Inspection Modal/Drawer.
  3. **Shelter Markers Layer:**
     * **Backend Endpoint:** `GET /shelters`
     * Display icon markers at shelter coordinates (`lat`, `lon`).
     * Circular radial badge indicating capacity and amenities badges (🩺 Medical, 💧 Water, 🚗 Road-Accessible).
  4. **Evacuation Route Overlay:**
     * **Backend Endpoint:** `GET /routes?from_id={area_id}&to_id={shelter_id}`
     * Highlight safe path (`LineString`). If `passes_hazard_zone: true`, pulse in caution red with animated dashed border.
  5. **GIS Layer Controls (Top-right floating widget):**
     * Toggle: [x] Risk Zones [x] Shelters [x] Evacuation Routes [ ] Hazard Heatmap [ ] Satellite Basemap.

---

### Module 3: Habitation Detail & Risk Breakdown Drawer
* **Backend Endpoint:** `GET /risk/{location}` and `GET /population/{location}`
* **Requirements:**
  1. Header with area ID, name, and priority badge.
  2. **Formula Factor Breakdown Bar (Recharts stacked bar):**
     * Hazard Intensity Contribution (0–40 pts)
     * Population Exposure Contribution (0–25 pts)
     * Demographic Vulnerability (Elderly + Children) (0–20 pts)
     * Historical Disaster Risk (0–15 pts)
  3. **Demographic Cards:**
     * Total Population
     * Senior Citizen percentage (`elderly_pct`)
     * Children percentage (`children_pct`)
  4. Quick CTA: "Calculate Evacuation Route to Best Shelter".

---

### Module 4: Relocation Priority & Capacity Matrix (Right Panel - Tab 1)
* **Backend Endpoint:** `GET /relocation-plan`
* **Requirements:**
  1. **Prioritized Evacuation List:** Habitations pre-sorted by severity (Immediate first, then High, Moderate).
  2. **Assignment Cards:**
     * Source Area -> Assigned Destination Shelter.
     * Route ID link (`route-area-X-shelter-Y`) that, when clicked, automatically focuses and highlights the route on the Leaflet map.
  3. **Unassigned Alert Banners:**
     * If `assigned_shelter_id == null`, render a stark red alert card displaying `unassigned_reason` (e.g., *"No shelter has enough remaining capacity"* or *"No safe road route connects this area"*).
     * Provide a manual override button allowing the commander to route to secondary shelters.

---

### Module 5: Shelter Capacity & Readiness Board (Right Panel - Tab 2)
* **Backend Endpoints:** `GET /shelters` and `GET /shelters/recommended?area_id={id}`
* **Requirements:**
  1. **Occupancy Progress Bars:**
     * Total Capacity vs. Allocated Evacuees.
     * Color shifts: Green (< 70%), Yellow (70–95%), Red (≥ 95% or Overloaded).
  2. **Shelter Recommendation Engine:**
     * Dropdown to select any affected area.
     * Displays ranked candidate shelters with suitability score (0–100) and explainable justification text generated by the backend.

---

### Module 6: "What-If" Disaster Simulation Studio (Right Panel - Tab 3)
* **Backend Endpoint:** `POST /simulate`
* **Payload:** `{ "hazard": "flood" | "rainfall" | "landslide", "increase_pct": number }`
* **Requirements:**
  1. **Simulation Controls:**
     * Hazard Selector: Flood, Heavy Rainfall, Landslide.
     * Surge Slider: `0%` to `200%` increase (step 5%).
     * Action: "Run Scenario Projection" (with loading spinner).
  2. **Impact Delta Comparison Card:**
     * **Immediate Risk Escalations:** List of habitations newly pushed into `IMMEDIATE` status.
     * **Displaced Population Surge:** Metric showing `before.immediate_population` -> `after.immediate_population` with percentage delta indicator (e.g. `+4,200 (+35%)`).
     * **Capacity Strained Shelters:** Highlight shelters that breached safety thresholds under this surge.
  3. **Side-by-Side Toggle:** Button on the map to toggle "Pre-Disaster Baseline" vs "Simulated Surge" layers.

---

### Module 7: "Ask RiskRadar" Grounded AI Incident Copilot (Right Panel - Tab 4)
* **Backend Endpoint:** `POST /ask-ai`
* **Payload:** `{ "question": string }`
* **Requirements:**
  1. **Conversational Chat Interface:**
     * Clean chat stream styled as tactical situational briefings.
     * Loading state with typing pulse: *"Consulting PostGIS spatial registry..."*
  2. **Instant Prompt Pills (One-click queries):**
     * *"Which zone should we evacuate first?"*
     * *"What is the safest route from Area 3 to Shelter 1?"*
     * *"Simulate a 50% flood increase and report capacity bottlenecks."*
  3. **Anti-Hallucination Source Audit:**
     * Expandable accordion below every answer: `"Verified Sources & Metrics"` showing the raw JSON returned in `sources` from the backend.

---

### Module 8: Authority Intervention & Quick Admin Tools (Mocking / Future-Ready)
* **Purpose:** Allows judges to see interactive control.
* **Features:**
  * Toggle Road Blockage button: Click any road segment to simulate a landslide block, immediately triggering route recalculation.
  * Adjust Shelter Capacity: Quick slider to adjust available beds during an influx.

---

## 6. Frontend Directory Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── icons/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance with baseURL from .env (VITE_API_URL)
│   │   ├── riskApi.ts             # Calls /risk-zones and /risk/{location}
│   │   ├── sheltersApi.ts         # Calls /shelters and /shelters/recommended
│   │   ├── routesApi.ts           # Calls /routes
│   │   ├── relocationApi.ts       # Calls /relocation-plan
│   │   ├── simulationApi.ts       # Calls /simulate
│   │   └── aiApi.ts               # Calls /ask-ai
│   ├── components/
│   │   ├── common/
│   │   │   ├── Badge.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── MetricCard.tsx
│   │   ├── map/
│   │   │   ├── RiskRadarMap.tsx   # Core Leaflet map instance
│   │   │   ├── RiskPolygonLayer.tsx
│   │   │   ├── ShelterMarkerLayer.tsx
│   │   │   ├── RouteLineLayer.tsx
│   │   │   └── MapLegend.tsx
│   │   ├── triage/
│   │   │   ├── HabitationList.tsx
│   │   │   └── RiskScoreChart.tsx
│   │   ├── relocation/
│   │   │   ├── RelocationTable.tsx
│   │   │   └── EvacuationCard.tsx
│   │   ├── shelters/
│   │   │   ├── ShelterCapacityCard.tsx
│   │   │   └── ShelterRankList.tsx
│   │   ├── simulation/
│   │   │   ├── SimulationControl.tsx
│   │   │   └── DeltaComparisonCard.tsx
│   │   ├── ai/
│   │   │   ├── AskAIChat.tsx
│   │   │   └── PromptPills.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── hooks/
│   │   ├── useRiskData.ts
│   │   ├── useShelters.ts
│   │   ├── useRelocationPlan.ts
│   │   └── useSimulation.ts
│   ├── store/
│   │   └── useDashboardStore.ts   # Selected area, active route, filter state
│   ├── types/
│   │   └── api.ts                 # TypeScript interfaces matching contracts.py
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

---

## 7. TypeScript Contracts (Mirroring Backend Schemas)

```typescript
// src/types/api.ts

export type PriorityLevel = "IMMEDIATE" | "HIGH" | "MODERATE" | "SAFE";

export interface RiskProperties {
  area_id: string;
  risk_score: number;
  hazard: string;
  population: number;
  vulnerability: number;
  priority: PriorityLevel;
  breakdown: {
    hazard_intensity: number;
    population_exposure: number;
    vulnerability: number;
    historical_risk: number;
  };
}

export interface RiskFeature {
  type: "Feature";
  geometry: {
    type: "Polygon";
    coordinates: number[][][];
  };
  properties: RiskProperties;
}

export interface RiskZoneCollection {
  type: "FeatureCollection";
  features: RiskFeature[];
}

export interface Shelter {
  shelter_id: string;
  name: string;
  capacity: number;
  lat: number;
  lon: number;
  medical_facility: boolean;
  water_available: boolean;
}

export interface RouteResponse {
  distance_km: number;
  eta_minutes: number;
  passes_hazard_zone: boolean;
  geometry: {
    type: "LineString";
    coordinates: [number, number][]; // [lon, lat]
  };
}

export interface RelocationPlanItem {
  area_id: string;
  priority: string;
  assigned_shelter_id: string | null;
  route_id: string | null;
  unassigned_reason: string | null;
}

export interface SimulationRequest {
  hazard: "flood" | "rainfall" | "landslide";
  increase_pct: number;
}

export interface SimulationResponse {
  hazard: string;
  increase_pct: number;
  before: {
    risk_zones: {
      total_areas: number;
      high_priority_areas: number;
      immediate_areas: number;
      average_risk_score: number;
    };
    shelter_capacity_utilization: Array<{
      shelter_id: string;
      capacity: number;
      allocated: number;
      remaining_capacity: number;
      utilization_pct: number;
      over_capacity: boolean;
    }>;
  };
  after: {
    risk_zones: {
      total_areas: number;
      high_priority_areas: number;
      immediate_areas: number;
      average_risk_score: number;
    };
    shelter_capacity_utilization: Array<{
      shelter_id: string;
      capacity: number;
      allocated: number;
      remaining_capacity: number;
      utilization_pct: number;
      over_capacity: boolean;
    }>;
  };
  delta: {
    areas_upgraded_to_immediate: string[];
    total_population_at_immediate_risk: {
      before: number;
      after: number;
    };
    shelters_now_over_capacity: string[];
  };
}

export interface AskAIResponse {
  answer: string;
  sources: Record<string, any>;
}
```

---

## 8. Implementation Roadmap for the Team

| Phase | Milestone | Deliverables | Estimated Time |
|---|---|---|---|
| **Phase 1** | **Scaffolding & Architecture** | Vite + React + Tailwind + TypeScript setup; Axios client with `.env`; TanStack Query; Layout frames. | 3 Hours |
| **Phase 2** | **GIS Leaflet Map Integration** | Dark-themed Leaflet setup; Polygon rendering from `/risk-zones` with color scale; Shelter markers with tooltips. | 5 Hours |
| **Phase 3** | **Relocation & Routing Flow** | Relocation matrix table; Route rendering from `/routes`; clicking an evacuation item draws the route on the map. | 4 Hours |
| **Phase 4** | **What-If Simulation Studio** | Slider controls; `/simulate` endpoint hook; before-vs-after delta KPI cards; visual layer switching. | 4 Hours |
| **Phase 5** | **AI Copilot ("Ask RiskRadar")** | Floating chat UI; `/ask-ai` integration; prompt suggestions; verified source inspection accordion. | 3 Hours |
| **Phase 6** | **Polish & SIH Demo Walkthrough** | Sound effects for alerts; preset demo scenarios; mobile responsiveness check; judge presentation rehearsal. | 3 Hours |

---

## 9. Hackathon Demo Winning Tactics

1. **The 30-Second "Hook" Demo:**
   * Start with the map loaded on standard monitoring.
   * Open the **Simulation Studio**, crank "Flood Surge" to `+75%`, and hit **Project Disaster Surge**.
   * Watch the map polygons turn from Yellow/Orange to flashing Deep Crimson, metrics jump by thousands of displaced persons, and capacity gaps immediately highlight in red.
2. **The "Ask AI" Live Stunner:**
   * Click prompt pill: *"Which village should be evacuated first and why?"*
   * Show the judge that the response gives the exact numbers from the PostGIS database with zero hallucination.
3. **Show Evacuation Route Bypass:**
   * Select a high-risk area. Show the route bypassing flooded zones (penalized route) to deliver evacuees safely to an uncrowded shelter with medical amenities.
