/**
 * Toast Hook - Toast notification hook using Sonner
 */
import { toast as sonnerToast } from "sonner";

export const useToast = () => {
  return {
    toast: (
      message: string,
      type?: "success" | "error" | "info" | "warning"
    ) => {
      switch (type) {
        case "success":
          sonnerToast.success(message);
          break;
        case "error":
          sonnerToast.error(message);
          break;
        case "warning":
          sonnerToast.warning(message);
          break;
        case "info":
        default:
          sonnerToast.info(message);
          break;
      }
    },
  };
};
