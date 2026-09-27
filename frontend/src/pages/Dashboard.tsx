import { useEffect, useMemo, useState } from "react";
import { ArrowRight, ShieldAlert } from "lucide-react";
import { Link } from "react-router-dom";
import { getRelocationPlan, getRiskZones, getShelters, type Feature, type Plan, type Shelter } from "../lib/api";
import { displayPriority, priorityClass } from "../lib/ui";
import { ErrorState, Loading } from "../components/State";
import { RadarMap } from "../components/RadarMap";
import { GlassCard, MetricCard, PageHeader, SectionHeader } from "../components/common";

export default function Dashboard() {
  const [zones, setZones] = useState<Feature[]>();
  const [shelters, setShelters] = useState<Shelter[]>();
  const [plan, setPlan] = useState<Plan[]>();
  const [error, setError] = useState<string>();

  const load = () => {
    setError(undefined);
    Promise.all([getRiskZones(), getShelters(), getRelocationPlan()])
      .then(([z, s, p]) => {
        setZones(z.features);
        setShelters(s);
        setPlan(p);
      })
      .catch((e) => setError(e.message));
  };

  useEffect(load, []);

  const high = zones?.filter((z) => z.properties.priority !== "SAFE") ?? [];
  const capacity = shelters?.reduce((n, s) => n + s.capacity, 0) ?? 0;
  const allocated =
    plan && zones
      ? plan.reduce(
          (sum, item) =>
            sum + (zones.find((zone) => zone.properties.area_id === item.area_id)?.properties.population ?? 0),
          0
        )
      : 0;
  const utilization = capacity ? Math.min(100, Math.round((allocated / capacity) * 100)) : 0;
  const shown = useMemo(
    () => [...high].sort((a, b) => b.properties.risk_score - a.properties.risk_score).slice(0, 4),
    [zones]
  );

  if (error) return <ErrorState error={error} retry={load} />;
  if (!zones || !shelters || !plan) return <Loading />;

  return (
    <div className="reveal space-y-6">
      <PageHeader
        title="Active Radar"
        eyebrow="District Overview"
        description="Priority sectors, shelter capacity, and relocation assignments from the current RiskRadar dataset."
      />

      <div className="flex flex-wrap gap-2">
        <span className="pill border border-white/10 bg-white/5 px-3 py-2 hud-label text-muted-text">
          {high.length} priority zones
        </span>
        <span className="pill border border-white/10 bg-white/5 px-3 py-2 hud-label text-muted-text">
          {shelters.length} shelters online
        </span>
      </div>

      <RadarMap />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <GlassCard variant="critical" className="flex flex-col justify-between">
          <div>
            <p className="hud-label text-bright-red">Priority alert</p>
            <div className="my-2 text-4xl font-extrabold tracking-tight text-white">{high.length}</div>
            <p className="text-sm text-muted-text">Areas above Safe</p>
          </div>
          <Link
            to="/risk-zones"
            className="mt-4 flex items-center justify-between rounded-full bg-white px-3 py-2 text-xs font-bold text-primary-red"
          >
            Inspect sectors <ArrowRight size={15} />
          </Link>
        </GlassCard>

        <MetricCard
          label="Shelter capacity"
          value={capacity.toLocaleString()}
          sublabel="Total places in the network"
        />
      </div>

      <GlassCard className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="hud-label text-[#FFB547]">Shelter network</p>
          <h2 className="mt-1 text-lg font-bold text-white">{utilization}% allocated</h2>
          <p className="mt-1 text-sm text-muted-text">
            {allocated.toLocaleString()} of {capacity.toLocaleString()} places assigned by the relocation plan.
          </p>
        </div>
        <div className="grid h-20 w-20 shrink-0 place-items-center rounded-full border-8 border-primary-red text-sm font-bold font-mono text-primary-red">
          {utilization}%
        </div>
      </GlassCard>

      <section>
        <SectionHeader
          title="Monitored sectors"
          action={
            <Link to="/risk-zones" className="hud-label text-bright-red hover:text-white">
              View all
            </Link>
          }
        />
        <div className="space-y-2">
          {shown.map(({ properties: p }) => (
            <Link key={p.area_id} to="/risk-zones">
              <GlassCard variant="interactive" className="flex items-center justify-between p-3">
                <div>
                  <b className="text-white">Area {p.area_id}</b>
                  <p className="text-xs font-mono text-muted-text">
                    {p.hazard} · score {p.risk_score} · population {p.population.toLocaleString()}
                  </p>
                </div>
                <span className={`pill px-3 py-1 hud-label ${priorityClass[p.priority]}`}>
                  {displayPriority(p.priority)}
                </span>
              </GlassCard>
            </Link>
          ))}
        </div>
      </section>

      <Link
        to="/safe-evacuation-route"
        className="flex h-14 items-center justify-between rounded-full bg-primary-red px-5 font-bold text-white shadow-radar"
      >
        <span className="flex items-center gap-2">
          <ShieldAlert size={18} />
          Deploy Rapid Protocol
        </span>
        <ArrowRight />
      </Link>
    </div>
  );
}
