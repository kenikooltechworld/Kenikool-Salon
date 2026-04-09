import { useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { useRealTimeAvailability } from "@/hooks/useRealTimeAvailability";
import {
  EyeIcon as Eye,
  WifiIcon as Wifi,
  WifiOffIcon as WifiOff,
} from "@/components/icons";

interface RealTimeAvailabilityIndicatorProps {
  serviceId: string;
  date: string; // YYYY-MM-DD format
  timeSlot: string; // HH:MM format
  staffId?: string;
  showViewerCount?: boolean;
  className?: string;
}

export default function RealTimeAvailabilityIndicator({
  serviceId,
  date,
  timeSlot,
  staffId,
  showViewerCount = true,
  className = "",
}: RealTimeAvailabilityIndicatorProps) {
  const { isConnected, trackSlotView, getSlotViewerCount } =
    useRealTimeAvailability({
      serviceId,
      date,
      enabled: true,
    });

  const viewerCount = getSlotViewerCount(timeSlot, staffId);

  // Track when user views this slot
  useEffect(() => {
    trackSlotView(timeSlot, staffId, "join");

    // Cleanup: track when user leaves
    return () => {
      trackSlotView(timeSlot, staffId, "leave");
    };
  }, [timeSlot, staffId, trackSlotView]);

  if (!showViewerCount && !isConnected) {
    return null;
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Connection status indicator */}
      <div className="flex items-center gap-1">
        {isConnected ? (
          <Wifi className="h-3 w-3 text-green-500" />
        ) : (
          <WifiOff className="h-3 w-3 text-gray-400" />
        )}
      </div>

      {/* Viewer count badge */}
      {showViewerCount && viewerCount > 0 && (
        <Badge
          variant="secondary"
          className="flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border-blue-200"
        >
          <Eye className="h-3 w-3" />
          <span>{viewerCount} viewing</span>
        </Badge>
      )}

      {/* Urgency indicator for high viewer count */}
      {viewerCount >= 3 && (
        <Badge variant="destructive" className="text-xs animate-pulse">
          High demand
        </Badge>
      )}
    </div>
  );
}
