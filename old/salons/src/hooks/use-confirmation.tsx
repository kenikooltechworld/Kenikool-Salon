import { useState, useCallback } from "react";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";

interface ConfirmationOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "info";
}

export function useConfirmation() {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<ConfirmationOptions>({
    message: "",
  });
  const [resolveCallback, setResolveCallback] = useState<
    ((value: boolean) => void) | null
  >(null);

  const confirm = useCallback((opts: ConfirmationOptions): Promise<boolean> => {
    setOptions(opts);
    setIsOpen(true);

    return new Promise((resolve) => {
      setResolveCallback(() => resolve);
    });
  }, []);

  const handleConfirm = useCallback(() => {
    if (resolveCallback) {
      resolveCallback(true);
    }
    setIsOpen(false);
    setResolveCallback(null);
  }, [resolveCallback]);

  const handleCancel = useCallback(() => {
    if (resolveCallback) {
      resolveCallback(false);
    }
    setIsOpen(false);
    setResolveCallback(null);
  }, [resolveCallback]);

  const ConfirmationDialog = useCallback(
    () => (
      <ConfirmationModal
        isOpen={isOpen}
        onClose={handleCancel}
        onConfirm={handleConfirm}
        title={options.title || "Confirm"}
        description={options.message}
        confirmText={options.confirmText}
        cancelText={options.cancelText}
        variant={options.variant === "danger" ? "destructive" : "default"}
      />
    ),
    [isOpen, options, handleCancel, handleConfirm],
  );

  return { confirm, ConfirmationDialog };
}
