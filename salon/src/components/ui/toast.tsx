/**
 * Toast Component
 * Theme-aware toast notifications
 */

import * as React from "react";
import { cn } from "@/lib/utils/cn";
import {
  XIcon,
  CheckIcon,
  AlertTriangleIcon,
  InfoIcon,
} from "@/components/icons";

type ToastVariant = "default" | "success" | "warning" | "error" | "info";

interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: ToastVariant;
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
  showToast: (toast: Omit<Toast, "id">) => void;
}

const ToastContext = React.createContext<ToastContextType | undefined>(
  undefined,
);

export const useToast = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
};

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const removeToast = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = React.useCallback(
    (toast: Omit<Toast, "id">) => {
      const id = Math.random().toString(36).substr(2, 9);
      const newToast = { ...toast, id };
      setToasts((prev) => [...prev, newToast]);

      if (toast.duration !== 0) {
        setTimeout(() => {
          removeToast(id);
        }, toast.duration || 5000);
      }
    },
    [removeToast],
  );

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, showToast: addToast }}
    >
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
};

const toastIcons = {
  success: CheckIcon,
  warning: AlertTriangleIcon,
  error: XIcon,
  info: InfoIcon,
  default: InfoIcon,
};

const toastStyles = {
  default:
    "bg-[var(--card)] border-[var(--border)] text-[var(--card-foreground)]",
  success:
    "bg-[var(--success)] border-[var(--success)] text-[var(--success-foreground)]",
  warning:
    "bg-[var(--warning)] border-[var(--warning)] text-[var(--warning-foreground)]",
  error:
    "bg-[var(--destructive)] border-[var(--destructive)] text-[var(--destructive-foreground)]",
  info: "bg-[var(--card)] border-[var(--border)] text-[var(--card-foreground)]",
};

const ToastContainer = ({
  toasts,
  removeToast,
}: {
  toasts: Toast[];
  removeToast: (id: string) => void;
}) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {toasts.map((toast) => {
        const Icon = toastIcons[toast.variant || "default"];
        return (
          <div
            key={toast.id}
            className={cn(
              "flex items-start gap-3 p-4 rounded-lg border-2 shadow-lg animate-in slide-in-from-right",
              toastStyles[toast.variant || "default"],
            )}
          >
            <Icon size={20} className="shrink-0 mt-0.5" />
            <div className="flex-1">
              {toast.title && (
                <div className="font-semibold mb-1">{toast.title}</div>
              )}
              {toast.description && (
                <div className="text-sm opacity-90">{toast.description}</div>
              )}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="shrink-0 rounded-sm p-1 hover:bg-black/10 transition-colors"
              aria-label="Close toast"
            >
              <XIcon size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
};
