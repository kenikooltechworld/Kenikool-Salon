import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { WifiIcon, WifiOffIcon } from "@/components/icons";

/**
 * NetworkStatus component displays the current network connectivity status
 * Shows online/offline indicator with appropriate styling
 */
export function NetworkStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (isOnline) {
    return (
      <Badge
        variant="outline"
        className="bg-green-50 text-green-700 border-green-200"
      >
        <WifiIcon size={12} className="mr-1" />
        Online
      </Badge>
    );
  }

  return (
    <Badge
      variant="destructive"
      className="bg-red-50 text-red-700 border-red-200"
    >
      <WifiOffIcon size={12} className="mr-1" />
      Offline
    </Badge>
  );
}
