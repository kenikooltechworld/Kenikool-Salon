/**
 * PrerequisiteQuickBook Component
 * Allows quick booking of prerequisite services
 * Validates: Requirements 7.5
 */
import React from "react";
import { Zap, ArrowRight } from "lucide-react";

interface PrerequisiteQuickBookProps {
  prerequisiteServiceId: string;
  prerequisiteServiceName: string;
  onQuickBook: (serviceId: string) => void;
  loading?: boolean;
}

/**
 * Component for quick booking of prerequisite services
 */
export const PrerequisiteQuickBook: React.FC<PrerequisiteQuickBookProps> = ({
  prerequisiteServiceId,
  prerequisiteServiceName,
  onQuickBook,
  loading = false,
}) => {
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
      <div className="flex items-start gap-3">
        <Zap className="h-5 w-5 flex-shrink-0 text-amber-600" />
        <div className="flex-1">
          <div className="font-semibold text-amber-900">Quick Book</div>
          <div className="mt-1 text-sm text-amber-800">
            Book <span className="font-medium">{prerequisiteServiceName}</span>{" "}
            now to unlock dependent services
          </div>
          <button
            onClick={() => onQuickBook(prerequisiteServiceId)}
            disabled={loading}
            className="mt-3 flex items-center gap-2 rounded-lg bg-amber-600 px-4 py-2 font-medium text-white hover:bg-amber-700 disabled:opacity-50"
          >
            {loading ? "Booking..." : "Book Now"}
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrerequisiteQuickBook;
