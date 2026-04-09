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
          "border-[var(--input)] bg-[var(--background)] text-[var(--foreground)] hover:border-[var(--primary)]",
        ed: "border-transparent bg-[var(--muted)] text-[var(--foreground)] hover:bg-[var(--muted)]",
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
  },
);

export interface SelectProps
  extends
    Omit<React.SelectHTMLAttributes<HTMLSelectElement>, "size">,
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
    ref,
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
            error && "border-(--error) focus-visible:ring-(--error)",
            success && "border-(--success) focus-visible:ring-(--success)",
            className,
          )}
          ref={ref}
          onChange={handleChange}
          {...props}
        >
          {children}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
          <ChevronDownIcon size={16} className="text-(--muted-foreground)" />
        </span>
      </div>
    );
  },
);

Select.displayName = "Select";

// Compound component pattern for compatibility with shadcn-style usage
interface SelectTriggerProps extends Omit<SelectProps, "children"> {
  children?: React.ReactNode;
}

// Context to pass select props to children
const SelectContext = React.createContext<{
  value?: string | number | readonly string[];
  onValueChange?: (value: string) => void;
  disabled?: boolean;
} | null>(null);

export const SelectTrigger = React.forwardRef<
  HTMLSelectElement,
  SelectTriggerProps
>(({ className, children, ...props }, ref) => {
  // Extract SelectItems from SelectContent
  const selectItems = React.Children.toArray(children)
    .filter((child) => {
      if (React.isValidElement(child)) {
        return child.type === SelectContent;
      }
      return false;
    })
    .flatMap((selectContent) => {
      if (React.isValidElement(selectContent) && selectContent.props.children) {
        return React.Children.toArray(selectContent.props.children);
      }
      return [];
    });

  return (
    <SelectContext.Provider
      value={{
        value: props.value,
        onValueChange: props.onValueChange,
        disabled: props.disabled,
      }}
    >
      <div className="relative w-full">
        <select
          ref={ref}
          className={cn(
            selectVariants({
              variant: props.variant,
              selectSize: props.selectSize,
            }),
            "appearance-none pr-10 w-full",
            props.error && "border-(--error) focus-visible:ring-(--error)",
            props.success &&
              "border-(--success) focus-visible:ring-(--success)",
            className,
          )}
          onChange={(e) => {
            props.onChange?.(e);
            props.onValueChange?.(e.target.value);
          }}
          value={props.value}
          disabled={props.disabled}
        >
          {selectItems}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
          <ChevronDownIcon size={16} className="text-(--muted-foreground)" />
        </span>
      </div>
    </SelectContext.Provider>
  );
});
SelectTrigger.displayName = "SelectTrigger";

export const SelectValue = ({
  children,
  placeholder,
}: {
  children?: React.ReactNode;
  placeholder?: string;
}) => <>{children || placeholder}</>;

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
