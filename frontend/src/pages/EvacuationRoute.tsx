import { useEffect, useState } from "react";
import { getRiskZones, getShelters, getSafeRoute, type Route } from "../lib/api";
import { ErrorState, Loading } from "../components/State";
import { RadarMap } from "../components/RadarMap";
import { GlassCard, MetricCard, PageHeader } from "../components/common";

export default function EvacuationRoute() {
  const [route, setRoute] = useState<Route>();
  const [error, setError] = useState<string>();

  const load = () => {
    setError(undefined);
    Promise.all([getRiskZones(), getShelters()])
      .then(async ([z, s]) => {
        const area = [...z.features].sort((a, b) => b.properties.risk_score - a.properties.risk_score)[0];
        if (!area || !s[0]) throw Error("No area or shelter data is available for routing.");
        setRoute(await getSafeRoute(`area:${area.properties.area_id}`, `shelter:${s[0].shelter_id}`));
      })
      .catch((e) => setError(e.message));
  };

  useEffect(load, []);

  if (error) return <ErrorState error={error} retry={load} />;
  if (!route) return <Loading label="Computing safest road vector" />;

  return (
    <section className="reveal space-y-6">
      <PageHeader
        title="Safe evacuation route"
        eyebrow="NetworkX safe path"
        description="Highest-risk area routed to the first available shelter, with hazard-zone crossings penalized."
      />

      <RadarMap route={route.geometry.coordinates} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard label="Distance" value={`${route.distance_km} km`} />
        <MetricCard label="ETA" value={`${route.eta_minutes} min`} />
        <MetricCard
          label="Hazard crossing"
          value={route.passes_hazard_zone ? "Yes" : "No"}
          critical={route.passes_hazard_zone}
          status={route.passes_hazard_zone ? "HIGH" : "SAFE"}
        />
      </div>

      <GlassCard variant="subtle">
        <p className="text-sm leading-relaxed text-muted-text">
          This route uses road segments from the live network and applies a strong penalty to hazard-zone crossings.
        </p>
      </GlassCard>
    </section>
  );
}
