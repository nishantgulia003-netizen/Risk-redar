import React from "react";

export interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  badge,
  action,
  className = "",
}) => {
  return (
    <div className={`mb-3 flex items-center justify-between gap-3 ${className}`}>
      <div>
        <div className="flex items-center gap-2">
          <h2 className="text-base sm:text-lg font-bold tracking-tight text-white">{title}</h2>
          {badge}
        </div>
        {subtitle && <p className="text-xs text-muted-text mt-0.5">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};
