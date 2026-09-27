import React from "react";
import { getStatusStyle, displayPriority, type StatusInput } from "../../lib/ui";

export interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: StatusInput;
  size?: "sm" | "md";
  showDot?: boolean;
  pulse?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = "md",
  showDot = true,
  pulse,
  className = "",
  ...props
}) => {
  const style = getStatusStyle(status);
  const label = displayPriority(status);
  const normalized = (status || "").toUpperCase();
  const isCritical = normalized === "CRITICAL" || normalized === "IMMEDIATE" || normalized === "UNSAFE" || normalized === "BLOCKED";
  const shouldPulse = pulse ?? isCritical;

  const sizeClasses =
    size === "sm"
      ? "px-2 py-0.5 text-[10px] font-semibold tracking-wide"
      : "px-3 py-1 text-xs font-bold tracking-wider";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border backdrop-blur-md ${style.bg} ${style.border} ${style.text} ${sizeClasses} ${className}`}
      role="status"
      aria-label={`Status: ${label}`}
      {...props}
    >
      {showDot && (
        <span
          className={`h-1.5 w-1.5 rounded-full ${style.dot} ${shouldPulse ? "animate-pulse" : ""}`}
          aria-hidden="true"
        />
      )}
      <span>{label}</span>
    </span>
  );
};
