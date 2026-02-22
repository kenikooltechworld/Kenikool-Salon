import * as React from "react";
import { cn } from "@/lib/utils/cn";

export interface RadioGroupProps {
  value?: string;
  onValueChange?: (value: string) => void;
  defaultValue?: string;
  disabled?: boolean;
  className?: string;
  children: React.ReactNode;
}

export interface RadioGroupItemProps {
  value: string;
  id?: string;
  disabled?: boolean;
  className?: string;
  children?: React.ReactNode;
}

const RadioGroupContext = React.createContext<{
  value?: string;
  onValueChange?: (value: string) => void;
  disabled?: boolean;
}>({});

export function RadioGroup({
  value,
  onValueChange,
  defaultValue,
  disabled = false,
  className = "",
  children,
}: RadioGroupProps) {
  const [internalValue, setInternalValue] = React.useState(defaultValue || "");

  const currentValue = value !== undefined ? value : internalValue;

  const handleValueChange = (newValue: string) => {
    if (disabled) return;

    if (value === undefined) {
      setInternalValue(newValue);
    }
    onValueChange?.(newValue);
  };

  return (
    <RadioGroupContext.Provider
      value={{
        value: currentValue,
        onValueChange: handleValueChange,
        disabled,
      }}
    >
      <div className={cn("space-y-2", className)} role="radiogroup">
        {children}
      </div>
    </RadioGroupContext.Provider>
  );
}

export function RadioGroupItem({
  value,
  id,
  disabled: itemDisabled = false,
  className = "",
  children,
}: RadioGroupItemProps) {
  const context = React.useContext(RadioGroupContext);
  const isSelected = context.value === value;
  const isDisabled = context.disabled || itemDisabled;

  const handleClick = () => {
    if (!isDisabled) {
      context.onValueChange?.(value);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  };

  if (children) {
    // Full item with label
    return (
      <div
        className={cn(
          "flex items-center space-x-3 cursor-pointer p-3 rounded-[var(--radius-md)] transition-all duration-200",
          "hover:bg-[var(--muted)] border-2",
          isSelected
            ? "border-[var(--primary)] bg-[var(--primary)]/10"
            : "border-[var(--border)]",
          isDisabled && "opacity-50 cursor-not-allowed",
          className
        )}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="radio"
        aria-checked={isSelected}
        tabIndex={isDisabled ? -1 : 0}
      >
        <div
          className={cn(
            "h-5 w-5 rounded-full border-2 flex items-center justify-center transition-all duration-200",
            isSelected
              ? "border-[var(--primary)] bg-[var(--primary)]"
              : "border-[var(--input)]"
          )}
        >
          {isSelected && (
            <div className="h-2.5 w-2.5 rounded-full bg-[var(--primary-foreground)]" />
          )}
        </div>
        <div className="flex-1 text-[var(--foreground)]">{children}</div>
      </div>
    );
  }

  // Just the radio button
  return (
    <button
      type="button"
      role="radio"
      aria-checked={isSelected}
      id={id}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={isDisabled}
      className={cn(
        "inline-flex items-center justify-center",
        "h-4 w-4 rounded-full border-2 transition-all duration-200",
        isSelected
          ? "border-[var(--primary)] bg-[var(--primary)]"
          : "border-[var(--input)] bg-transparent",
        isDisabled && "opacity-50 cursor-not-allowed",
        !isDisabled && "cursor-pointer",
        "focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:ring-offset-2",
        className
      )}
    >
      {isSelected && (
        <div className="h-2 w-2 rounded-full bg-[var(--primary-foreground)]" />
      )}
    </button>
  );
}
