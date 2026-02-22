import * as React from "react";
import { cn } from "@/lib/utils/cn";

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  position?: "top" | "bottom" | "left" | "right";
}

export function Tooltip({ children, content, position = "top" }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false);

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  };

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {isVisible && (
        <div
          className={cn(
            "absolute z-50 px-3 py-2 text-sm text-[var(--popover-foreground)] bg-[var(--popover)] border-2 border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] whitespace-nowrap animate-in fade-in-0 zoom-in-95",
            positionClasses[position]
          )}
        >
          {content}
        </div>
      )}
    </div>
  );
}
