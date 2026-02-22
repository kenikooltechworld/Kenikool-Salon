/**
 * Radio Component
 * Theme-aware radio button with label
 */

import * as React from "react";
import { cn } from "@/lib/utils/cn";

export interface RadioProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  error?: boolean;
}

const Radio = React.forwardRef<HTMLInputElement, RadioProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className="flex items-center gap-2">
        <div className="relative">
          <input
            type="radio"
            id={radioId}
            ref={ref}
            className={cn(
              "peer h-5 w-5 shrink-0 appearance-none rounded-full border-2 border-[var(--input)] bg-[var(--background)] transition-all duration-200",
              "checked:border-[var(--primary)] checked:border-[6px]",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              error && "border-[var(--error)]",
              className
            )}
            {...props}
          />
        </div>
        {label && (
          <label
            htmlFor={radioId}
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

Radio.displayName = "Radio";

export { Radio };
