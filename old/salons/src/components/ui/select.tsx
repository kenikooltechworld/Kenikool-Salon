/**
 * Select Component
 * Theme-aware dropdown select
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";
import { ChevronDownIcon } from "@/components/icons";

const selectVariants = cva(
  "flex w-full items-center justify-between rounded-[var(--radius-md)] border-2 bg-transparent px-3 py-2 text-sm transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "border-[var(--input)] bg-[var(--background)] text-[var(--foreground)] hover:border-[var(--primary)]", ed:
          "border-transparent bg-[var(--muted)] text-[var(--foreground)] hover:bg-[var(--muted)]",
      },
      selectSize: {
        sm: "h-9 text-sm",
        md: "h-10 text-base",
        lg: "h-11 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      selectSize: "md",
    },
  }
);

export interface SelectProps
  extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, "size">,
    VariantProps<typeof selectVariants> {
  error?: boolean;
  success?: boolean;
  onValueChange?: (value: string) => void;
}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      variant,
      selectSize,
      error,
      success,
      children,
      onValueChange,
      onChange,
      ...props
    },
    ref
  ) => {
    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange?.(e);
      onValueChange?.(e.target.value);
    };

    return (
      <div className="relative">
        <select
          className={cn(
            selectVariants({ variant, selectSize }),
            "appearance-none pr-10",
            error && "border-[var(--error)] focus-visible:ring-[var(--error)]",
            success &&
              "border-[var(--success)] focus-visible:ring-[var(--success)]",
            className
          )}
          ref={ref}
          onChange={handleChange}
          {...props}
        >
          {children}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
          <ChevronDownIcon
            size={16}
            className="text-[var(--muted-foreground)]"
          />
        </div>
      </div>
    );
  }
);

Select.displayName = "Select";

// Compatibility exports for compound component pattern
export const SelectTrigger = Select;
export const SelectValue = ({ children }: { children?: React.ReactNode }) => (
  <>{children}</>
);
export const SelectContent = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectItem = React.forwardRef<
  HTMLOptionElement,
  React.OptionHTMLAttributes<HTMLOptionElement>
>(({ children, ...props }, ref) => (
  <option ref={ref} {...props}>
    {children}
  </option>
));
SelectItem.displayName = "SelectItem";

export { Select, selectVariants };
