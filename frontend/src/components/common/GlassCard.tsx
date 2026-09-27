import React from "react";

export interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "subtle" | "interactive" | "critical";
  glow?: boolean;
}

export const GlassCard = React.forwardRef<HTMLDivElement, GlassCardProps>(
  ({ variant = "default", glow = false, className = "", children, ...props }, ref) => {
    let variantStyles = "glass-surface";

    if (variant === "elevated") {
      variantStyles = "glass-surface-elevated";
    } else if (variant === "subtle") {
      variantStyles = "glass-surface-subtle";
    } else if (variant === "interactive") {
      variantStyles =
        "glass-surface hover:bg-white/[0.08] hover:border-white/20 hover:-translate-y-0.5 transition duration-200 cursor-pointer active:translate-y-0";
    } else if (variant === "critical") {
      variantStyles =
        "glass-surface border-primary-red/40 bg-primary-red/[0.08] shadow-[0_0_24px_rgba(239,46,75,0.2)]";
    }

    const glowStyles = glow ? "shadow-red-glow border-primary-red/35" : "";

    return (
      <div
        ref={ref}
        className={`rounded-glass p-5 text-white ${variantStyles} ${glowStyles} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

GlassCard.displayName = "GlassCard";
