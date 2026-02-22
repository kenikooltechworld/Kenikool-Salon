/**
 * Switch Component
 * Theme-aware toggle switch
 */

import * as React from "react";
import { cn } from "@/lib/utils/cn";

export interface SwitchProps
  extends Omit<
    React.InputHTMLAttributes<HTMLInputElement>,
    "type" | "onChange"
  > {
  label?: string;
  error?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, label, error, id, onCheckedChange, ...props }, ref) => {
    const switchId = id || `switch-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className="flex items-center gap-3">
        <div className="relative">
          <input
            type="checkbox"
            id={switchId}
            ref={ref}
            className={cn("peer sr-only", className)}
            onChange={(e) => onCheckedChange?.(e.target.checked)}
            {...props}
          />
          <label
            htmlFor={switchId}
            className={cn(
              "block h-6 w-11 cursor-pointer rounded-full border-2 transition-all duration-200",
              "border-[var(--input)] bg-[var(--muted)]",
              "peer-checked:bg-[var(--primary)] peer-checked:border-[var(--primary)]",
              "peer-focus-visible:ring-2 peer-focus-visible:ring-[var(--ring)] peer-focus-visible:ring-offset-2",
              "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
              error && "border-[var(--error)]"
            )}
          >
            <span
              className={cn(
                "block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200",
                "translate-x-0.5 translate-y-0.5",
                "peer-checked:translate-x-5"
              )}
            />
          </label>
        </div>
        {label && (
          <label
            htmlFor={switchId}
            className={cn(
              "text-sm font-medium leading-none cursor-pointer select-none",
              "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
              error && "text-[var(--error)]"
            )}
          >
            {label}
          </label>
        )}
      </div>
    );
  }
);

Switch.displayName = "Switch";

export { Switch };
