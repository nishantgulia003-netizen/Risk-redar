import React from "react";

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  eyebrow?: string;
  actions?: React.ReactNode;
}

export const GlassPanel = React.forwardRef<HTMLDivElement, GlassPanelProps>(
  ({ title, eyebrow, actions, className = "", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`glass-surface-elevated rounded-xl p-5 md:p-6 text-white ${className}`}
        {...props}
      >
        {(title || eyebrow || actions) && (
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
            <div>
              {eyebrow && (
                <span className="hud-label block text-[10px] uppercase tracking-wider text-muted-text">
                  {eyebrow}
                </span>
              )}
              {title && <h2 className="text-lg font-bold text-white tracking-tight">{title}</h2>}
            </div>
            {actions && <div className="flex items-center gap-2">{actions}</div>}
          </div>
        )}
        {children}
      </div>
    );
  }
);

GlassPanel.displayName = "GlassPanel";
