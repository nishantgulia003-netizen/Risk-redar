import React from "react";
import { GlassCard } from "./GlassCard";

export interface LoadingStateProps {
  label?: string;
  rows?: number;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  label = "Loading operational telemetry...",
  rows = 3,
  className = "",
}) => {
  return (
    <GlassCard
      className={`space-y-4 p-6 ${className}`}
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <div className="flex items-center gap-3">
        <div className="h-3 w-3 rounded-full bg-primary-red animate-ping" />
        <span className="text-sm font-semibold text-muted-text">{label}</span>
      </div>

      <div className="space-y-3 pt-2">
        {Array.from({ length: rows }).map((_, idx) => (
          <div
            key={idx}
            className="skeleton-shimmer h-12 w-full rounded-xl border border-white/5"
            style={{ animationDelay: `${idx * 150}ms` }}
          />
        ))}
      </div>
    </GlassCard>
  );
};
