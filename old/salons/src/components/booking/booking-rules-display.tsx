import React from "react";
import { AlertCircle, Clock, Users } from "lucide-react";

interface BookingRule {
  minAdvanceBooking?: number; // minutes
  bufferTime?: number; // minutes
  maxCapacity?: number;
  capacityRemaining?: number;
}

interface BookingRulesDisplayProps {
  rules: BookingRule;
  showCapacity?: boolean;
}

export const BookingRulesDisplay: React.FC<BookingRulesDisplayProps> = ({
  rules,
  showCapacity = true,
}) => {
  const formatMinutes = (minutes: number): string => {
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-blue-50 p-4">
      <h3 className="font-medium text-gray-900 flex items-center gap-2">
        <AlertCircle className="h-4 w-4 text-blue-600" />
        Booking Rules
      </h3>

      <div className="space-y-2">
        {/* Minimum Advance Booking */}
        {rules.minAdvanceBooking && (
          <div className="flex items-start gap-3 text-sm">
            <Clock className="h-4 w-4 text-gray-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Advance Booking</p>
              <p className="text-gray-600">
                Book at least {formatMinutes(rules.minAdvanceBooking)} in
                advance
              </p>
            </div>
          </div>
        )}

        {/* Buffer Time */}
        {rules.bufferTime && (
          <div className="flex items-start gap-3 text-sm">
            <Clock className="h-4 w-4 text-gray-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Buffer Time</p>
              <p className="text-gray-600">
                {formatMinutes(rules.bufferTime)} buffer between appointments
              </p>
            </div>
          </div>
        )}

        {/* Capacity */}
        {showCapacity && rules.maxCapacity && (
          <div className="flex items-start gap-3 text-sm">
            <Users className="h-4 w-4 text-gray-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Capacity</p>
              <p className="text-gray-600">
                {rules.capacityRemaining || 0} of {rules.maxCapacity} spots
                available
              </p>
              {rules.capacityRemaining === 0 && (
                <p className="text-red-600 font-medium mt-1">
                  This service is fully booked
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
