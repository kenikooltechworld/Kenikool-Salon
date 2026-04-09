import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { RefreshCw, X } from "@/components/icons";

export default function PWAUpdatePrompt() {
  const [isVisible, setIsVisible] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const handleUpdateAvailable = () => {
      setIsVisible(true);
    };

    window.addEventListener("sw-update-available", handleUpdateAvailable);

    return () => {
      window.removeEventListener("sw-update-available", handleUpdateAvailable);
    };
  }, []);

  const handleUpdate = () => {
    setIsRefreshing(true);

    // Skip waiting and reload
    if ("serviceWorker" in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type: "SKIP_WAITING" });
    }

    // Reload after a short delay
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  const handleDismiss = () => {
    setIsVisible(false);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div
      className="fixed top-4 left-4 right-4 z-50 animate-slide-down"
      role="alert"
      aria-live="polite"
    >
      <Card className="mx-auto max-w-md shadow-lg border-2 border-green-500">
        <div className="p-4">
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <RefreshCw className="w-5 h-5 text-green-600" />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-semibold text-gray-900 mb-1">
                Update Available
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                A new version of the app is available. Refresh to get the latest
                features and improvements.
              </p>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleUpdate}
                  disabled={isRefreshing}
                  size="sm"
                  className="bg-green-600 hover:bg-green-700"
                >
                  <RefreshCw
                    className={`w-4 h-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
                  />
                  {isRefreshing ? "Updating..." : "Update Now"}
                </Button>
                <Button onClick={handleDismiss} variant="outline" size="sm">
                  Later
                </Button>
              </div>
            </div>

            {/* Close button */}
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss update prompt"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
