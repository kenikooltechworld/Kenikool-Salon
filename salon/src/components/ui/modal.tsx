/**
 * Modal Component
 * Theme-aware modal dialog with overlay
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";
import { XIcon, AlertTriangleIcon } from "@/components/icons";

const modalVariants = cva(
  "fixed inset-0 z-50 flex items-center justify-center p-4",
  {
    variants: {
      show: {
        true: "animate-in fade-in-0",
        false: "animate-out fade-out-0 pointer-events-none",
      },
    },
  },
);

const modalOverlayVariants = cva(
  "fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity",
  {
    variants: {
      show: {
        true: "opacity-100",
        false: "opacity-0",
      },
    },
  },
);

const modalContentVariants = cva(
  "relative bg-[var(--card)] text-[var(--card-foreground)] rounded-[var(--radius-xl)] shadow-[var(--shadow-xl)] border-2 border-[var(--border)] max-h-[90vh] overflow-y-auto transition-all",
  {
    variants: {
      size: {
        sm: "max-w-sm w-full",
        md: "max-w-md w-full",
        lg: "max-w-lg w-full",
        xl: "max-w-xl w-full",
        "2xl": "max-w-2xl w-full",
        full: "max-w-full w-full mx-4",
      },
      show: {
        true: "animate-in zoom-in-95 slide-in-from-bottom-4",
        false: "animate-out zoom-out-95 slide-out-to-bottom-4",
      },
    },
    defaultVariants: {
      size: "md",
    },
  },
);

export interface ModalProps extends VariantProps<typeof modalContentVariants> {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  closeOnOverlayClick?: boolean;
  showCloseButton?: boolean;
}

const Modal = ({
  open,
  onClose,
  children,
  size,
  closeOnOverlayClick = true,
  showCloseButton = true,
}: ModalProps) => {
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

  return (
    <div className={cn(modalVariants({ show: open }))}>
      <div
        className={cn(modalOverlayVariants({ show: open }))}
        onClick={closeOnOverlayClick ? onClose : undefined}
      />
      <div className={cn(modalContentVariants({ size, show: open }))}>
        {showCloseButton && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-[var(--radius-md)] hover:bg-[var(--muted)] transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
            aria-label="Close modal"
          >
            <XIcon size={20} />
          </button>
        )}
        {children}
      </div>
    </div>
  );
};

const ModalHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-2 p-6 pb-4", className)}
    {...props}
  />
));
ModalHeader.displayName = "ModalHeader";

const ModalTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & { showWarning?: boolean }
>(({ className, showWarning, ...props }, ref) => (
  <div className="flex items-center gap-3">
    {showWarning && (
      <AlertTriangleIcon size={24} className="text-warning shrink-0" />
    )}
    <h2
      ref={ref}
      className={cn(
        "text-2xl font-semibold leading-none tracking-tight text-foreground",
        className,
      )}
      {...props}
    />
  </div>
));
ModalTitle.displayName = "ModalTitle";

const ModalDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-[var(--muted-foreground)]", className)}
    {...props}
  />
));
ModalDescription.displayName = "ModalDescription";

const ModalBody = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("px-6 py-4", className)} {...props} />
));
ModalBody.displayName = "ModalBody";

const ModalFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center justify-end gap-3 p-6 pt-4", className)}
    {...props}
  />
));
ModalFooter.displayName = "ModalFooter";

export {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalBody,
  ModalFooter,
};
