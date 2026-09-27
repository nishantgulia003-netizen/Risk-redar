import React, { useEffect, useRef } from "react";
import { X } from "lucide-react";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  eyebrow?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  eyebrow = "Tactical Briefing",
  children,
  footer,
  maxWidth = "md",
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthClass = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
  }[maxWidth];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Liquid Backdrop Blur Overlay */}
      <div
        className="fixed inset-0 bg-black/75 backdrop-blur-md transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Liquid Glass Dialog Body */}
      <div
        ref={modalRef}
        className={`glass-surface-elevated relative w-full ${maxWidthClass} rounded-2xl border border-white/15 p-6 shadow-2xl transition-all reveal`}
      >
        <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-4">
          <div>
            {eyebrow && (
              <span className="hud-label block text-[10px] uppercase tracking-wider text-muted-text">
                {eyebrow}
              </span>
            )}
            <h2 id="modal-title" className="text-xl font-bold tracking-tight text-white mt-0.5">
              {title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="focus-ring rounded-full p-1.5 text-muted-text hover:bg-white/10 hover:text-white transition"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        <div className="py-4 text-sm text-slate-200 leading-relaxed max-h-[70vh] overflow-y-auto">
          {children}
        </div>

        {footer && (
          <div className="flex items-center justify-end gap-3 border-t border-white/10 pt-4">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
