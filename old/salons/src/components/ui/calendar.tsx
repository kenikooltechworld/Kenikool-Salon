import * as React from "react";
import { ChevronLeft, ChevronRight } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

export interface CalendarProps {
  mode?: "single" | "multiple" | "range";
  selected?: Date | Date[] | { from: Date; to?: Date };
  onSelect?: (
    date: Date | Date[] | { from: Date; to?: Date } | undefined
  ) => void;
  disabled?: (date: Date) => boolean;
  className?: string;
  initialFocus?: boolean;
}

export function Calendar({
  mode = "single",
  selected,
  onSelect,
  disabled,
  className = "",
}: CalendarProps) {
  const [currentMonth, setCurrentMonth] = React.useState(new Date());

  const daysInMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth() + 1,
    0
  ).getDate();

  const firstDayOfMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth(),
    1
  ).getDay();

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const previousMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1)
    );
  };

  const nextMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1)
    );
  };

  const isSelected = (day: number) => {
    const date = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth(),
      day
    );

    if (mode === "single" && selected instanceof Date) {
      return (
        date.getDate() === selected.getDate() &&
        date.getMonth() === selected.getMonth() &&
        date.getFullYear() === selected.getFullYear()
      );
    }

    if (mode === "multiple" && Array.isArray(selected)) {
      return selected.some(
        (d) =>
          d.getDate() === date.getDate() &&
          d.getMonth() === date.getMonth() &&
          d.getFullYear() === date.getFullYear()
      );
    }

    return false;
  };

  const isDisabled = (day: number) => {
    if (!disabled) return false;
    const date = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth(),
      day
    );
    return disabled(date);
  };

  const handleDayClick = (day: number) => {
    const date = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth(),
      day
    );

    if (isDisabled(day)) return;

    if (mode === "single") {
      onSelect?.(date);
    } else if (mode === "multiple") {
      const currentSelected = Array.isArray(selected) ? selected : [];
      const isAlreadySelected = currentSelected.some(
        (d) =>
          d.getDate() === date.getDate() &&
          d.getMonth() === date.getMonth() &&
          d.getFullYear() === date.getFullYear()
      );

      if (isAlreadySelected) {
        onSelect?.(
          currentSelected.filter(
            (d) =>
              !(
                d.getDate() === date.getDate() &&
                d.getMonth() === date.getMonth() &&
                d.getFullYear() === date.getFullYear()
              )
          )
        );
      } else {
        onSelect?.([...currentSelected, date]);
      }
    }
  };

  const renderDays = () => {
    const days = [];
    const totalCells = Math.ceil((firstDayOfMonth + daysInMonth) / 7) * 7;

    for (let i = 0; i < totalCells; i++) {
      const day = i - firstDayOfMonth + 1;

      if (i < firstDayOfMonth || day > daysInMonth) {
        days.push(
          <div key={i} className="p-2 text-center">
            <span className="text-transparent">0</span>
          </div>
        );
      } else {
        const selected = isSelected(day);
        const disabled = isDisabled(day);

        days.push(
          <button
            key={i}
            type="button"
            onClick={() => handleDayClick(day)}
            disabled={disabled}
            className={cn(
              "p-2 text-center rounded-[var(--radius-md)] transition-all duration-200",
              selected
                ? "bg-[var(--primary)] text-[var(--primary-foreground)] font-semibold shadow-[var(--shadow-sm)]"
                : "hover:bg-[var(--accent)] text-[var(--foreground)]",
              disabled && "opacity-50 cursor-not-allowed",
              !disabled && "cursor-pointer"
            )}
          >
            {day}
          </button>
        );
      }
    }

    return days;
  };

  return (
    <div className={cn("p-3", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={previousMonth}
          className="h-7 w-7 p-0"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <div className="font-semibold text-[var(--foreground)]">
          {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </div>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={nextMonth}
          className="h-7 w-7 p-0"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Day names */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map((name) => (
          <div
            key={name}
            className="text-center text-sm font-medium text-[var(--muted-foreground)] p-2"
          >
            {name}
          </div>
        ))}
      </div>

      {/* Days */}
      <div className="grid grid-cols-7 gap-1">{renderDays()}</div>
    </div>
  );
}
