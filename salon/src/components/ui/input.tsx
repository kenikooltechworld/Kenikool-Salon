/**
 * Input Component
 * Theme-aware input field with variants
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const inputVariants = cva(
  "flex w-full rounded-[var(--radius-md)] border-2 bg-transparent px-3 py-2 text-sm transition-all duration-200 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-[var(--muted-foreground)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "border-[var(--input)] bg-[var(--background)] text-[var(--foreground)] hover:border-[var(--primary)]", ed:
          "border-transparent bg-[var(--muted)] text-[var(--foreground)] hover:bg-[var(--muted)] focus-visible:bg-[var(--background)]",
        flushed:
          "rounded-none border-0 border-b-2 border-[var(--input)] px-0 focus-visible:border-[var(--primary)] focus-visible:ring-0",
      },
      inputSize: {
        sm: "h-9 text-sm",
        md: "h-10 text-base",
        lg: "h-11 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      inputSize: "md",
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size">,
    VariantProps<typeof inputVariants> {
  error?: boolean;
  success?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, inputSize, error, success, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          inputVariants({ variant, inputSize }),
          error && "border-[var(--error)] focus-visible:ring-[var(--error)]",
          success &&
            "border-[var(--success)] focus-visible:ring-[var(--success)]",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";

export { Input, inputVariants };
