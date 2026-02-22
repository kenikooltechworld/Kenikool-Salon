import { useEffect } from "react";
import { registerServiceWorker } from "@/lib/offline/register-sw";
import { syncEngine } from "@/lib/offline/sync-engine";

export function ServiceWorkerInitializer() {
  useEffect(() => {
    // Register service worker
    registerServiceWorker();

    // Listen for sync requests from service worker
    const handleSyncRequest = () => {
      syncEngine.sync();
    };

    window.addEventListener("offline-sync-requested", handleSyncRequest);

    return () => {
      window.removeEventListener("offline-sync-requested", handleSyncRequest);
    };
  }, []);

  return null;
}
