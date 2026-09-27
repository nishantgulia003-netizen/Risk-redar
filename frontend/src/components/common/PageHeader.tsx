import React from "react";

export interface PageHeaderProps {
  title: string;
  eyebrow?: string;
  description?: string;
  actions?: React.ReactNode;
  statusBadge?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  eyebrow = "Emergency Intelligence",
  description,
  actions,
  statusBadge,
  className = "",
}) => {
  return (
    <header className={`mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between ${className}`}>
      <div>
        {eyebrow && (
          <div className="flex items-center gap-2">
            <span className="hud-label text-[11px] font-semibold uppercase tracking-wider text-muted-text">
              {eyebrow}
            </span>
            {statusBadge}
          </div>
        )}
        <h1 className="mt-1 text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
          {title}
        </h1>
        {description && (
          <p className="mt-1 max-w-2xl text-sm text-muted-text leading-relaxed">
            {description}
          </p>
        )}
      </div>

      {actions && (
        <div className="flex flex-wrap items-center gap-2.5 pt-1 sm:pt-0">
          {actions}
        </div>
      )}
    </header>
  );
};
