import { useCallback } from "react";
import { useToast } from "@/components/ui/toast";
import { RefreshButton } from "@/components/ui/refresh-button";

interface UsePageRefreshOptions {
  onRefresh?: () => Promise<void> | void;
  pageName?: string;
}

export function usePageRefresh(options?: UsePageRefreshOptions) {
  const { showToast } = useToast();

  const handleRefresh = useCallback(async () => {
    if (options?.onRefresh) {
      await options.onRefresh();
    }
    showToast({
      title: "Refreshed",
      description: `${options?.pageName || "Page"} updated successfully`,
    });
  }, [options?.onRefresh, options?.pageName, showToast]);

  return { handleRefresh };
}
