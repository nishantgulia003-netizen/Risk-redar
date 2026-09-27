import type { RiskPriority, OperationalStatus } from "../types/api";

export type StatusInput = RiskPriority | OperationalStatus | string;

export const displayPriority = (priority: StatusInput): string => {
  if (!priority) return "Unknown";
  const normalized = priority.toUpperCase();
  switch (normalized) {
    case "IMMEDIATE":
      return "Critical";
    case "CRITICAL":
      return "Critical";
    case "HIGH":
      return "High";
    case "MODERATE":
      return "Moderate";
    case "SAFE":
      return "Safe";
    default:
      return priority.charAt(0).toUpperCase() + priority.slice(1).toLowerCase();
  }
};

/**
 * Tactical badge styling for backend-assigned risk priorities and statuses.
 * Respects strict color system:
 * SAFE = #35D07F
 * MODERATE = #FFB547
 * HIGH = #FF7A45
 * CRITICAL / IMMEDIATE = #EF2E4B
 */
export const priorityClass: Record<RiskPriority, string> = {
  SAFE: "bg-[#35D07F]/15 text-[#35D07F] border border-[#35D07F]/30",
  MODERATE: "bg-[#FFB547]/15 text-[#FFB547] border border-[#FFB547]/30",
  HIGH: "bg-[#FF7A45]/15 text-[#FF7A45] border border-[#FF7A45]/30",
  IMMEDIATE: "bg-[#EF2E4B]/20 text-[#FF4964] border border-[#EF2E4B]/40 shadow-[0_0_12px_rgba(239,46,75,0.25)]",
};

export const getStatusStyle = (status: StatusInput): {
  bg: string;
  text: string;
  border: string;
  dot: string;
} => {
  const normalized = (status || "").toUpperCase();
  switch (normalized) {
    case "CRITICAL":
    case "IMMEDIATE":
    case "UNSAFE":
    case "BLOCKED":
      return {
        bg: "bg-[#EF2E4B]/20",
        text: "text-[#FF4964]",
        border: "border-[#EF2E4B]/40",
        dot: "bg-[#EF2E4B]",
      };
    case "HIGH":
      return {
        bg: "bg-[#FF7A45]/15",
        text: "text-[#FF7A45]",
        border: "border-[#FF7A45]/35",
        dot: "bg-[#FF7A45]",
      };
    case "MODERATE":
    case "UNCONFIRMED":
      return {
        bg: "bg-[#FFB547]/15",
        text: "text-[#FFB547]",
        border: "border-[#FFB547]/35",
        dot: "bg-[#FFB547]",
      };
    case "SAFE":
    case "CLEAR":
      return {
        bg: "bg-[#35D07F]/15",
        text: "text-[#35D07F]",
        border: "border-[#35D07F]/35",
        dot: "bg-[#35D07F]",
      };
    default:
      return {
        bg: "bg-white/10",
        text: "text-muted-text",
        border: "border-white/15",
        dot: "bg-muted-text",
      };
  }
};
