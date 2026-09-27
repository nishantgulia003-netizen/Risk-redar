import { useEffect, useState } from "react";
import { getRiskZones, type Feature, type Priority } from "../lib/api";
import { displayPriority, priorityClass } from "../lib/ui";
import { ErrorState, Loading } from "../components/State";

export default function RiskZones() {
  const [zones, setZones] = useState<Feature[]>();
  const [error, setError] = useState<string>();
  const [filter, setFilter] = useState<Priority | "ALL">("ALL");

  const load = () => {
    setError(undefined);
    getRiskZones()
      .then((result) => setZones(result.features))
      .catch((reason) => setError(reason.message));
  };

  useEffect(load, []);

  if (error) return <ErrorState error={error} retry={load} />;
  if (!zones) return <Loading />;

  const rows = zones
    .filter((zone) => filter === "ALL" || zone.properties.priority === filter)
    .sort((a, b) => b.properties.risk_score - a.properties.risk_score);

  return (
    <section className="reveal space-y-4">
      <div>
        <p className="hud-label text-muted-text">Risk Intelligence Registry</p>
        <h1 className="mt-1 text-3xl font-extrabold tracking-tight text-white">
          Hazard-Based Risk Zones
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <select
          aria-label="Filter risk zones by priority"
          className="focus-ring w-full sm:w-64 rounded-full border border-white/15 bg-white/5 p-2.5 text-xs sm:text-sm font-semibold text-white shadow-sm backdrop-blur-md"
          value={filter}
          onChange={(event) => setFilter(event.target.value as Priority | "ALL")}
        >
          {["ALL", "SAFE", "MODERATE", "HIGH", "IMMEDIATE"].map((value) => (
            <option key={value} value={value} className="bg-background text-white">
              {value === "ALL" ? "All Priorities" : `${value} Priority`}
            </option>
          ))}
        </select>
        <span className="text-xs font-mono text-muted-text">
          {rows.length} sectors monitored
        </span>
      </div>

      <div className="space-y-3">
        {rows.map(({ properties: risk }, index) => (
          <article
            key={risk.area_id}
            className="hud-card risk-zone-card"
            style={{ animationDelay: `${index * 35}ms` }}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-extrabold text-white">Area {risk.area_id}</h2>
                <p className="mt-0.5 text-sm font-medium text-muted-text capitalize">
                  {risk.hazard} · {risk.population.toLocaleString()} residents
                </p>
              </div>
              <span
                className={`pill shrink-0 px-3 py-1 font-hud text-[10px] font-bold uppercase tracking-wider ${priorityClass[risk.priority]}`}
              >
                {displayPriority(risk.priority)}
              </span>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-x-7 gap-y-2 border-t border-white/10 pt-3 text-sm text-muted-text font-mono">
              <span>
                Risk Score <b className="ml-1 text-bright-red">{risk.risk_score}</b>
              </span>
              <span>
                Vulnerability <b className="ml-1 text-white">{risk.vulnerability}</b>
              </span>
              {Object.entries(risk.breakdown).map(([name, value]) => (
                <span key={name} className="capitalize">
                  {name.replace(/_/g, " ")}: <b className="text-white">{value}</b>
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
