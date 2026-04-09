import React from "react";
import { cn } from "@/lib/utils/cn";

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  error?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, description, error, className, id, ...props }, ref) => {
    const checkboxId =
      id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <input
            ref={ref}
            id={checkboxId}
            type="checkbox"
            className={cn(
              "w-4 h-4 sm:w-5 sm:h-5 rounded border-border cursor-pointer transition-transform hover:scale-110",
              error && "border-destructive",
              className,
            )}
            {...props}
          />
          {label && (
            <label
              htmlFor={checkboxId}
              className="text-sm font-medium text-foreground cursor-pointer"
            >
              {label}
            </label>
          )}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground ml-7">{description}</p>
        )}
        {error && <p className="text-xs text-destructive ml-7">{error}</p>}
      </div>
    );
  },
);

Checkbox.displayName = "Checkbox";
