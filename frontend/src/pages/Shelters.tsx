import React, { useEffect, useState } from "react";
import { Building2, Droplet, Stethoscope, Users, RefreshCw } from "lucide-react";
import { getShelters, type Shelter } from "../lib/api";
import {
  PageHeader,
  GlassCard,
  MetricCard,
  StatusBadge,
  LoadingState,
  ErrorState,
  Button,
} from "../components/common";

export default function Shelters() {
  const [shelters, setShelters] = useState<Shelter[]>();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    setError(undefined);
    getShelters()
      .then((data) => setShelters(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const totalCapacity = shelters?.reduce((sum, s) => sum + s.capacity, 0) ?? 0;
  const medicalCount = shelters?.filter((s) => s.medical_facility).length ?? 0;
  const waterCount = shelters?.filter((s) => s.water_available).length ?? 0;

  if (error) {
    return <ErrorState error={error} retry={load} />;
  }

  if (loading || !shelters) {
    return <LoadingState label="Auditing regional emergency shelters network..." />;
  }

  return (
    <div className="space-y-6 reveal">
      <PageHeader
        title="Shelter Infrastructure"
        eyebrow="Relocation Readiness"
        description="Active safe zones, emergency shelters, and medical relief camps equipped for displaced habitations."
        actions={
          <Button variant="secondary" size="sm" onClick={load} icon={<RefreshCw size={14} />}>
            Sync Network
          </Button>
        }
      />

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MetricCard
          label="Total Shelter Capacity"
          value={totalCapacity.toLocaleString()}
          sublabel="Available beds & supplies"
          icon={<Users size={18} />}
        />
        <MetricCard
          label="Medical Stations"
          value={`${medicalCount} / ${shelters.length}`}
          sublabel="Triage units operational"
          icon={<Stethoscope size={18} />}
        />
        <MetricCard
          label="Potable Water Reserves"
          value={`${waterCount} / ${shelters.length}`}
          sublabel="Sanitation confirmed"
          icon={<Droplet size={18} />}
        />
      </div>

      {/* Shelters Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {shelters.map((shelter) => (
          <GlassCard key={shelter.shelter_id} variant="interactive" className="space-y-3">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h2 className="text-base font-bold text-white">{shelter.name}</h2>
                <span className="text-[11px] font-mono text-muted-text">
                  ID: #{shelter.shelter_id}
                </span>
              </div>
              <StatusBadge status={shelter.safety_status ?? "SAFE"} size="sm" />
            </div>

            <div className="border-t border-white/5 pt-2">
              <div className="flex items-baseline justify-between">
                <span className="text-xs text-muted-text">Safe Capacity</span>
                <span className="text-xl font-extrabold text-white font-sans">
                  {shelter.capacity.toLocaleString()}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 pt-2 border-t border-white/5 text-[11px]">
              <span
                className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 ${
                  shelter.medical_facility
                    ? "bg-[#35D07F]/10 text-[#35D07F] border border-[#35D07F]/20"
                    : "bg-white/5 text-muted-text line-through"
                }`}
              >
                <Stethoscope size={12} />
                Medical
              </span>
              <span
                className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 ${
                  shelter.water_available
                    ? "bg-[#35D07F]/10 text-[#35D07F] border border-[#35D07F]/20"
                    : "bg-white/5 text-muted-text line-through"
                }`}
              >
                <Droplet size={12} />
                Water
              </span>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
}
