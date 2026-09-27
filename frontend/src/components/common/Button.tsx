import React from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      loading = false,
      icon,
      iconPosition = "left",
      className = "",
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    let variantStyles = "";
    if (variant === "primary") {
      variantStyles =
        "bg-primary-red hover:bg-bright-red text-white font-bold shadow-radar hover:shadow-red-glow";
    } else if (variant === "secondary") {
      variantStyles =
        "glass-surface hover:bg-white/10 text-white font-semibold border-white/15";
    } else if (variant === "outline") {
      variantStyles =
        "bg-transparent border border-white/20 hover:border-white/40 text-white hover:bg-white/5 font-semibold";
    } else if (variant === "ghost") {
      variantStyles =
        "bg-transparent hover:bg-white/5 text-muted-text hover:text-white font-semibold";
    } else if (variant === "danger") {
      variantStyles =
        "bg-primary-red/15 hover:bg-primary-red/25 border border-primary-red/50 text-bright-red font-bold";
    }

    let sizeStyles = "px-4 py-2 text-xs sm:text-sm";
    if (size === "sm") {
      sizeStyles = "px-3 py-1.5 text-xs";
    } else if (size === "lg") {
      sizeStyles = "px-6 py-3 text-base";
    }

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`focus-ring inline-flex items-center justify-center gap-2 rounded-full transition-all duration-200 active:translate-y-0 hover:-translate-y-0.5 disabled:opacity-50 disabled:pointer-events-none ${variantStyles} ${sizeStyles} ${className}`}
        {...props}
      >
        {loading && <Loader2 size={16} className="animate-spin text-current" aria-hidden="true" />}
        {!loading && icon && iconPosition === "left" && icon}
        <span>{children}</span>
        {!loading && icon && iconPosition === "right" && icon}
      </button>
    );
  }
);

Button.displayName = "Button";
