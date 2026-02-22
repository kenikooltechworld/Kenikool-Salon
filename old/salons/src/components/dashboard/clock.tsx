import { useState, useEffect } from "react";
import { ClockIcon } from "@/components/icons";

export function Clock() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="flex items-center gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-[var(--muted)] rounded-[var(--radius-md)]">
      <ClockIcon
        size={16}
        className="text-[var(--muted-foreground)] sm:block"
      />
      <div className="flex flex-col">
        <span className="text-xs sm:text-sm font-semibold text-[var(--foreground)] leading-tight">
          {formatTime(time)}
        </span>
        <span className="text-[10px] sm:text-xs text-[var(--muted-foreground)] leading-tight hidden sm:block">
          {formatDate(time)}
        </span>
      </div>
    </div>
  );
}
