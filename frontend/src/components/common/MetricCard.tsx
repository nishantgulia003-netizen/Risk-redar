import React from "react";
import { GlassCard } from "./GlassCard";
import { StatusBadge } from "./StatusBadge";
import type { StatusInput } from "../../lib/ui";

export interface MetricCardProps {
  label: string;
  value: string | number;
  sublabel?: string;
  icon?: React.ReactNode;
  status?: StatusInput;
  critical?: boolean;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  sublabel,
  icon,
  status,
  critical = false,
  className = "",
}) => {
  return (
    <GlassCard
      variant={critical ? "critical" : "default"}
      className={`relative overflow-hidden ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="hud-label text-xs font-medium text-muted-text">{label}</span>
        {icon && (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-muted-text border border-white/10">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span
          className={`text-3xl sm:text-4xl font-extrabold tracking-tight font-sans ${
            critical ? "text-primary-red" : "text-white"
          }`}
        >
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
      </div>

      {(sublabel || status) && (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-white/5 pt-2.5">
          {sublabel && (
            <span className="text-xs text-muted-text leading-tight">{sublabel}</span>
          )}
          {status && <StatusBadge status={status} size="sm" />}
        </div>
      )}
    </GlassCard>
  );
};
