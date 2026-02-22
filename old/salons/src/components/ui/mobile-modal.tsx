/**
 * Mobile-Optimized Modal Component
 * Uses bottom sheet on mobile, regular modal on desktop
 */
import * as React from "react";
import { cn } from "@/lib/utils/cn";
import { XIcon } from "@/components/icons";
import { useIsMobile, useBottomSheet } from "@/lib/hooks/useTouchGestures";

interface MobileModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  size?: "sm" | "md" | "lg" | "xl" | "full";
}

export function MobileModal({
  open,
  onClose,
  children,
  title,
  size = "md",
}: MobileModalProps) {
  const isMobile = useIsMobile();
  const {
    isDragging,
    dragY,
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
  } = useBottomSheet(open);

  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [open]);

  if (!open) return null;

  if (isMobile) {
    // Bottom sheet for mobile
    return (
      <div className="fixed inset-0 z-50 flex items-end justify-center">
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />
        <div
          className={cn(
            "relative bg-card text-card-foreground rounded-t-[24px] shadow-xl border-t-2 border-border w-full max-h-[90vh] overflow-y-auto transition-transform",
            isDragging ? "" : "transition-transform duration-300"
          )}
          style={{
            transform: `translateY(${dragY}px)`,
          }}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd(onClose)}
        >
          {/* Drag handle */}
          <div className="flex justify-center pt-3 pb-2">
            <div className="w-12 h-1 bg-muted-foreground/30 rounded-full" />
          </div>

          {/* Header */}
          {title && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-border">
              <h2 className="text-xl font-semibold">{title}</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-md hover:bg-muted transition-colors"
                aria-label="Close"
              >
                <XIcon size={20} />
              </button>
            </div>
          )}

          {/* Content */}
          <div className="p-6">{children}</div>
        </div>
      </div>
    );
  }

  // Regular modal for desktop
  const sizeClasses = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    full: "max-w-full mx-4",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div
        className={cn(
          "relative bg-card text-card-foreground rounded-xl shadow-xl border-2 border-border max-h-[90vh] overflow-y-auto w-full",
          sizeClasses[size]
        )}
      >
        {title && (
          <div className="flex items-center justify-between p-6 pb-4">
            <h2 className="text-2xl font-semibold">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-md hover:bg-muted transition-colors"
              aria-label="Close"
            >
              <XIcon size={20} />
            </button>
          </div>
        )}
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  );
}
