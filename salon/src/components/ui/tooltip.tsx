import * as React from "react";
import { cn } from "@/lib/utils/cn";
import { useDropdownPosition } from "@/hooks/useDropdownPosition";

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  position?: "top" | "bottom" | "left" | "right";
}

export function Tooltip({ children, content, position = "top" }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false);
  const triggerRef = React.useRef<HTMLDivElement>(null);
  const contentRef = React.useRef<HTMLDivElement>(null);

  const alignMap: Record<string, "left" | "center" | "right"> = {
    top: "center",
    bottom: "center",
    left: "left",
    right: "right",
  };

  const { style } = useDropdownPosition(triggerRef, contentRef, {
    align: alignMap[position] || "center",
    offset: position === "top" || position === "left" ? -8 : 8,
  });

  const baseStyle: React.CSSProperties = {
    ...style,
    ...(position === "top" ? { bottom: "auto" } : {}),
    ...(position === "bottom" ? { top: "auto" } : {}),
    ...(position === "left" ? { right: "auto" } : {}),
    ...(position === "right" ? { left: "auto" } : {}),
  };

  return (
    <div className="relative inline-block">
      <div
        ref={triggerRef}
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
      >
        {children}
      </div>
      {isVisible && (
        <div
          ref={contentRef}
          className={cn(
            "px-3 py-2 text-sm text-[var(--popover-foreground)] bg-[var(--popover)] border-2 border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] whitespace-nowrap animate-in fade-in-0 zoom-in-95",
            "max-w-[calc(100vw-1rem)]"
          )}
          style={baseStyle}
        >
          {content}
        </div>
      )}
    </div>
  );
}
