/**
 * Checkbox Component
 * Theme-aware checkbox with label
 */

import * as React from "react";
import { cn } from "@/lib/utils/cn";
import { CheckIcon } from "@/components/icons";

export interface CheckboxProps
  extends Omit<
    React.InputHTMLAttributes<HTMLInputElement>,
    "type" | "onChange" | "onCheckedChange"
  > {
  label?: string;
  error?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  (
    { className, label, error, id, onCheckedChange, onChange, ...props },
    ref
  ) => {
    const generatedId = React.useId();
    const checkboxId = id || generatedId;

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onCheckedChange?.(e.target.checked);
      onChange?.(e);
    };

    return (
      <div className="flex items-center gap-2">
        <div className="relative">
          <input
            type="checkbox"
            id={checkboxId}
            ref={ref}
            className={cn(
              "peer h-5 w-5 shrink-0 appearance-none rounded-[var(--radius-sm)] border-2 border-[var(--input)] bg-[var(--background)] transition-all duration-200",
              "checked:bg-[var(--primary)] checked:border-[var(--primary)]",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              error && "border-[var(--error)]",
              className
            )}
            onChange={handleChange}
            {...props}
          />
          <CheckIcon
            size={14}
            className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[var(--primary-foreground)] opacity-0 peer-checked:opacity-100 transition-opacity"
          />
        </div>
        {label && (
          <label
            htmlFor={checkboxId}
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

Checkbox.displayName = "Checkbox";

export { Checkbox };
