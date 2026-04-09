/**
 * Progress Component
 * Professional progress bar with percentage display and animations
 * Theme-aware with CSS variables
 */

// the staff email is not showing them the ur they should click  to login or to take them to login page

import { cn } from "@/lib/utils/cn";

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
  showPercentage?: boolean;
  size?: "sm" | "md" | "lg";
  variant?: "default" | "success" | "warning" | "error";
}

function Progress({
  className,
  value = 0,
  max = 100,
  showPercentage = true,
  size = "md",
  variant = "default",
  ...props
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizeClasses = {
    sm: "h-1.5",
    md: "h-2.5",
    lg: "h-3.5",
  };

  const variantClasses = {
    default: "bg-primary",
    success: "bg-success",
    warning: "bg-warning",
    error: "bg-destructive",
  };

  return (
    <div className="w-full space-y-1.5">
      <div
        className={cn(
          "relative w-full overflow-hidden rounded-full bg-muted",
          sizeClasses[size],
          className,
        )}
        {...props}
      >
        <div
          className={cn(
            "h-full transition-all duration-300 ease-in-out rounded-full",
            variantClasses[variant],
          )}
          style={{
            width: `${percentage}%`,
            animation:
              percentage > 0 && percentage < 100
                ? "pulse-subtle 2s ease-in-out infinite"
                : "none",
          }}
        />
      </div>
      {showPercentage && (
        <div className="flex justify-between items-center text-xs text-muted-foreground">
          <span className="font-medium">{Math.round(percentage)}%</span>
          <span>Uploading...</span>
        </div>
      )}
    </div>
  );
}

Progress.displayName = "Progress";

export { Progress };
