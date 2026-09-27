import React from "react";
import { Info } from "lucide-react";
import { GlassCard } from "./GlassCard";

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className = "",
}) => {
  return (
    <GlassCard
      variant="subtle"
      className={`flex flex-col items-center justify-center p-8 text-center ${className}`}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/5 text-muted-text border border-white/10 mb-3">
        {icon || <Info size={24} aria-hidden="true" />}
      </div>
      <h2 className="text-base font-bold text-white tracking-tight">{title}</h2>
      <p className="mt-1 max-w-md text-xs sm:text-sm text-muted-text leading-relaxed">
        {description}
      </p>
      {action && <div className="mt-4">{action}</div>}
    </GlassCard>
  );
};
