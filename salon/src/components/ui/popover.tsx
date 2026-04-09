import * as React from "react";
import { cn } from "@/lib/utils/cn";

interface PopoverContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const PopoverContext = React.createContext<PopoverContextType | undefined>(
  undefined,
);

export function Popover({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <PopoverContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative inline-block">{children}</div>
    </PopoverContext.Provider>
  );
}

export function PopoverTrigger({
  children,
  asChild,
}: {
  children: React.ReactNode;
  asChild?: boolean;
}) {
  const context = React.useContext(PopoverContext);
  if (!context) throw new Error("PopoverTrigger must be used within Popover");

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<any>, {
      onClick: () => context.setIsOpen(!context.isOpen),
    });
  }

  return (
    <div
      onClick={() => context.setIsOpen(!context.isOpen)}
      className="cursor-pointer"
    >
      {children}
    </div>
  );
}

export function PopoverContent({
  children,
  align = "center",
  className,
}: {
  children: React.ReactNode;
  align?: "start" | "center" | "end";
  className?: string;
}) {
  const context = React.useContext(PopoverContext);
  if (!context) throw new Error("PopoverContent must be used within Popover");

  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        context!.setIsOpen(false);
      }
    }

    if (context!.isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [context]);

  if (!context!.isOpen) return null;

  const alignmentClasses = {
    start: "left-0",
    center: "left-1/2 -translate-x-1/2",
    end: "right-0",
  };

  return (
    <div
      ref={ref}
      className={cn(
        "absolute z-50 mt-2 rounded-[var(--radius-md)] border-2 border-[var(--border)] bg-[var(--popover)] shadow-[var(--shadow-lg)] animate-in fade-in-0 zoom-in-95",
        alignmentClasses[align],
        className,
      )}
    >
      {children}
    </div>
  );
}
