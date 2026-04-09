/**
 * Alert Component
 * Theme-aware alert/notification component
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";
import {
  CheckIcon,
  XIcon,
  AlertTriangleIcon,
  InfoIcon,
} from "@/components/icons";

const alertVariants = cva(
  "relative w-full rounded-[var(--radius-lg)] border-2 p-4 flex items-start gap-3",
  {
    variants: {
      variant: {
        default:
          "bg-[var(--background)] border-[var(--border)] text-[var(--foreground)]",
        success:
          "bg-[var(--success)]/10 border-[var(--success)] text-[var(--success)] [&>svg]:text-[var(--success)]",
        warning:
          "bg-[var(--warning)]/10 border-[var(--warning)] text-[var(--warning)] [&>svg]:text-[var(--warning)]",
        error:
          "bg-[var(--error)]/10 border-[var(--error)] text-[var(--error)] [&>svg]:text-[var(--error)]",
        destructive:
          "bg-[var(--error)]/10 border-[var(--error)] text-[var(--error)] [&>svg]:text-[var(--error)]",
        info: "bg-[var(--info)]/10 border-[var(--info)] text-[var(--info)] [&>svg]:text-[var(--info)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

const alertIcons = {
  success: CheckIcon,
  warning: AlertTriangleIcon,
  error: XIcon,
  destructive: XIcon,
  info: InfoIcon,
  default: InfoIcon,
};

export interface AlertProps
  extends
    React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  showIcon?: boolean;
  onClose?: () => void;
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      className,
      variant = "default",
      showIcon = true,
      onClose,
      children,
      ...props
    },
    ref,
  ) => {
    const Icon = alertIcons[variant || "default"];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(alertVariants({ variant }), className)}
        {...props}
      >
        {showIcon && <Icon size={20} className="shrink-0 mt-0.5" />}
        <div className="flex-1">{children}</div>
        {onClose && (
          <button
            onClick={onClose}
            className="shrink-0 rounded-[var(--radius-sm)] p-1 hover:bg-black/10 transition-colors"
            aria-label="Close alert"
          >
            <XIcon size={16} />
          </button>
        )}
      </div>
    );
  },
);
Alert.displayName = "Alert";

const AlertTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 font-semibold leading-none tracking-tight", className)}
    {...props}
  />
));
AlertTitle.displayName = "AlertTitle";

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("text-sm opacity-90", className)} {...props} />
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertTitle, AlertDescription };
