/**
 * ConflictDetector Component
 * Validates bookings against existing appointments and suggests alternatives
 * Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
 */
import React, { useEffect } from "react";
import { AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { useCheckBookingConflict } from "@/lib/api/hooks/useBookings";

interface AlternativeSlot {
  time: string;
  capacity_remaining: number;
}

interface ConflictDetectorProps {
  stylistId: string;
  serviceId: string;
  startTime: string;
  endTime: string;
  onConflictDetected?: (conflict: boolean) => void;
  onAlternativesFound?: (alternatives: AlternativeSlot[]) => void;
}

/**
 * Component for detecting booking conflicts and suggesting alternatives
 */
export const ConflictDetector: React.FC<ConflictDetectorProps> = ({
  stylistId,
  serviceId,
  startTime,
  endTime,
  onConflictDetected,
  onAlternativesFound,
}) => {
  const conflictMutation = useCheckBookingConflict();

  useEffect(() => {
    if (!stylistId || !serviceId || !startTime || !endTime) {
      return;
    }

    conflictMutation.mutate({
      stylist_id: stylistId,
      service_id: serviceId,
      start_time: startTime,
      end_time: endTime,
    });
  }, [stylistId, serviceId, startTime, endTime]);

  useEffect(() => {
    if (conflictMutation.data) {
      onConflictDetected?.(conflictMutation.data.has_conflict);
      if (conflictMutation.data.alternative_slots) {
        onAlternativesFound?.(conflictMutation.data.alternative_slots);
      }
    }
  }, [conflictMutation.data, onConflictDetected, onAlternativesFound]);

  if (conflictMutation.isPending) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
        Checking availability...
      </div>
    );
  }

  if (conflictMutation.isError) {
    let errorMessage = "Unknown error";
    if (conflictMutation.error?.response?.data) {
      const data = conflictMutation.error.response.data;
      if (typeof data === "object" && "details" in data) {
        errorMessage = (data as any).details;
      } else if (typeof data === "string") {
        errorMessage = data;
      }
    } else if (conflictMutation.error?.message) {
      errorMessage = conflictMutation.error.message;
    }

    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-3">
        <div className="flex items-start gap-2">
          <AlertTriangle className="h-5 w-5 flex-shrink-0 text-red-600" />
          <div className="text-sm text-red-900">
            <p className="font-semibold">Error checking availability</p>
            <p>{errorMessage}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!conflictMutation.data) {
    return null;
  }

  const result = conflictMutation.data;

  if (result.has_conflict) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 flex-shrink-0 text-red-600" />
            <div>
              <h3 className="font-semibold text-red-900">
                Booking conflict detected
              </h3>
              {result.conflict_details && (
                <div className="mt-2 space-y-1 text-sm text-red-800">
                  <p>
                    <strong>Conflicting booking:</strong>{" "}
                    {result.conflict_details.conflicting_start_time} to{" "}
                    {result.conflict_details.conflicting_end_time}
                  </p>
                  <p>
                    <strong>Stylist:</strong>{" "}
                    {result.conflict_details.conflicting_stylist}
                  </p>
                  <p className="mt-2">
                    This time slot is already booked. Please select a different
                    time or stylist.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Alternative Slots */}
        {result.alternative_slots && result.alternative_slots.length > 0 && (
          <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
            <h4 className="mb-3 flex items-center gap-2 font-semibold text-blue-900">
              <Clock className="h-4 w-4" />
              Available alternatives
            </h4>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
              {result.alternative_slots.slice(0, 8).map((slot) => (
                <div
                  key={slot.time}
                  className="rounded border border-blue-300 bg-white p-2 text-center text-sm"
                >
                  <div className="font-medium text-blue-900">{slot.time}</div>
                  <div className="text-xs text-blue-700">
                    {slot.capacity_remaining} spots
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-900">
      <CheckCircle className="h-5 w-5 flex-shrink-0 text-green-600" />
      <span>This time slot is available</span>
    </div>
  );
};

export default ConflictDetector;
