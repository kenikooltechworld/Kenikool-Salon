import { useEffect, useState } from "react";
import { WifiOffIcon, RefreshIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Redirect back to home after a short delay
      setTimeout(() => {
        window.location.href = "/";
      }, 1000);
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    // Check initial state
    setIsOnline(navigator.onLine);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const handleRetry = () => {
    if (navigator.onLine) {
      window.location.href = "/";
    } else {
      showToast(
        "Still offline. Please check your internet connection.",
        "error",
      );
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center space-y-6">
        <div className="flex justify-center">
          <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center">
            <WifiOffIcon size={48} className="text-muted-foreground" />
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">You're Offline</h1>
          <p className="text-muted-foreground">
            It looks like you've lost your internet connection. Don't worry, you
            can still use some features of the app.
          </p>
        </div>

        {isOnline ? (
          <div className="p-4 bg-success/10 border border-success/20 rounded-lg">
            <p className="text-success font-medium">
              Connection restored! Redirecting...
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg text-left space-y-2">
              <h3 className="font-medium text-foreground">
                What you can do offline:
              </h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• View cached bookings and clients</li>
                <li>• Create new bookings (will sync later)</li>
                <li>• Update booking status</li>
                <li>• Add new clients</li>
                <li>• View services and inventory</li>
              </ul>
            </div>

            <Button onClick={handleRetry} fullWidth>
              <RefreshIcon size={16} />
              Try Again
            </Button>

            <Button
              variant="outline"
              onClick={() => (window.location.href = "/")}
              fullWidth
            >
              Continue Offline
            </Button>
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          Your changes will automatically sync when you're back online.
        </p>
      </div>
    </div>
  );
}
