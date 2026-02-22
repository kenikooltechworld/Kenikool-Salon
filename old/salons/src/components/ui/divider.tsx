import * as React from "react";
import { cn } from "@/lib/utils/cn";

interface DividerProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical";
  label?: string;
}

const Divider = React.forwardRef<HTMLDivElement, DividerProps>(
  ({ className, orientation = "horizontal", label, ...props }, ref) => {
    if (label && orientation === "horizontal") {
      return (
        <div
          ref={ref}
          className={cn("flex items-center gap-4 my-4", className)}
          {...props}
        >
          <div className="flex-1 h-px bg-[var(--border)]" />
          <span className="text-sm text-[var(--muted-foreground)]">
            {label}
          </span>
          <div className="flex-1 h-px bg-[var(--border)]" />
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(
          orientation === "horizontal"
            ? "h-px w-full bg-[var(--border)] my-4"
            : "w-px h-full bg-[var(--border)] mx-4",
          className
        )}
        {...props}
      />
    );
  }
);

Divider.displayName = "Divider";

export { Divider };
