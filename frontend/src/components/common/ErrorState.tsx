import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

export interface ErrorStateProps {
  title?: string;
  error: string;
  retry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Telemetry Signal Disrupted",
  error,
  retry,
  className = "",
}) => {
  return (
    <div
      role="alert"
      className={`glass-surface border-primary-red/50 bg-primary-red/10 rounded-glass p-6 text-white shadow-[0_0_30px_rgba(239,46,75,0.2)] ${className}`}
    >
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-red/25 text-bright-red border border-primary-red/40">
          <AlertTriangle size={22} aria-hidden="true" />
        </div>

        <div className="flex-1">
          <h2 className="text-base font-bold text-white">{title}</h2>
          <p className="mt-1 text-sm text-[#FF7A45] font-mono leading-relaxed break-words">
            {error}
          </p>

          {retry && (
            <div className="mt-4">
              <Button
                variant="primary"
                size="sm"
                onClick={retry}
                icon={<RefreshCw size={14} />}
              >
                Reconnect & Retry
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
