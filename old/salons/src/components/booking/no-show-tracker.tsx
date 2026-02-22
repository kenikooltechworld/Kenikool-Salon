import React from "react";
import { AlertTriangle } from "lucide-react";

interface NoShowRecord {
  date: string;
  service: string;
  stylist: string;
}

interface NoShowTrackerProps {
  noShowCount: number;
  noShowRecords?: NoShowRecord[];
  noShowPercentage?: number;
}

export const NoShowTracker: React.FC<NoShowTrackerProps> = ({
  noShowCount,
  noShowRecords = [],
  noShowPercentage = 0,
}) => {
  const riskLevel =
    noShowCount >= 3 ? "high" : noShowCount >= 2 ? "medium" : "low";
  const riskColor =
    riskLevel === "high" ? "red" : riskLevel === "medium" ? "yellow" : "green";

  return (
    <div
      className={`space-y-3 rounded-lg border-2 bg-${riskColor}-50 border-${riskColor}-200 p-4`}
    >
      <div className="flex items-start gap-2">
        {riskLevel !== "low" && (
          <AlertTriangle
            className={`h-5 w-5 text-${riskColor}-600 flex-shrink-0 mt-0.5`}
          />
        )}
        <div className="flex-1">
          <h3 className={`font-medium text-${riskColor}-900`}>
            No-Show History
          </h3>
          <p className={`text-sm text-${riskColor}-800 mt-1`}>
            {noShowCount} no-show{noShowCount !== 1 ? "s" : ""} on record
            {noShowPercentage > 0 && ` (${noShowPercentage.toFixed(1)}%)`}
          </p>
        </div>
      </div>

      {riskLevel !== "low" && (
        <div
          className={`text-sm text-${riskColor}-900 bg-${riskColor}-100 rounded p-2`}
        >
          {riskLevel === "high"
            ? "This customer has a high no-show rate. Consider requiring advance payment."
            : "This customer has had multiple no-shows. Monitor future bookings."}
        </div>
      )}

      {noShowRecords.length > 0 && (
        <div className="space-y-2 border-t border-gray-200 pt-2">
          <p className="text-xs font-medium text-gray-900">Recent no-shows:</p>
          <div className="space-y-1">
            {noShowRecords.slice(0, 3).map((record, idx) => (
              <div key={idx} className="text-xs text-gray-700">
                <span className="font-medium">{record.date}</span> -{" "}
                {record.service} with {record.stylist}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
