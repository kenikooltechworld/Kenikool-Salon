/**
 * PrerequisiteDisplay Component
 * Shows prerequisite services with descriptions and completion status
 * Validates: Requirements 7.4, 7.5
 */
import React from "react";
import { CheckCircle, Circle, BookOpen } from "lucide-react";
import { useServicePrerequisites } from "../../lib/api/hooks/usePrerequisites";

interface PrerequisiteDisplayProps {
  serviceId: string;
  completedServiceIds?: string[];
  onQuickBook?: (serviceId: string) => void;
  compact?: boolean;
}

/**
 * Component for displaying prerequisite services
 */
export const PrerequisiteDisplay: React.FC<PrerequisiteDisplayProps> = ({
  serviceId,
  completedServiceIds = [],
  onQuickBook,
  compact = false,
}) => {
  const {
    data: prerequisites,
    isLoading,
    error,
  } = useServicePrerequisites(serviceId);

  if (isLoading) {
    return <div className="text-center text-sm text-gray-500">Loading...</div>;
  }

  if (error || !prerequisites || prerequisites.length === 0) {
    return null;
  }

  if (compact) {
    return (
      <div className="space-y-2">
        <div className="text-sm font-medium text-gray-700">
          Prerequisites ({prerequisites.length})
        </div>
        <div className="space-y-1">
          {prerequisites.map((prereq) => {
            const isCompleted = completedServiceIds.includes(prereq.service_id);
            return (
              <div
                key={prereq.id}
                className="flex items-center gap-2 text-sm text-gray-600"
              >
                {isCompleted ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <Circle className="h-4 w-4 text-gray-400" />
                )}
                <span>{prereq.service_name}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 rounded-lg border border-blue-200 bg-blue-50 p-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <BookOpen className="h-5 w-5 text-blue-600" />
        <h3 className="font-semibold text-blue-900">
          Prerequisite Services ({prerequisites.length})
        </h3>
      </div>

      {/* Prerequisites List */}
      <div className="space-y-2">
        {prerequisites.map((prereq) => {
          const isCompleted = completedServiceIds.includes(prereq.service_id);

          return (
            <div
              key={prereq.id}
              className="flex items-start justify-between rounded-lg bg-white p-3"
            >
              <div className="flex items-start gap-3">
                {isCompleted ? (
                  <CheckCircle className="h-5 w-5 flex-shrink-0 text-green-600" />
                ) : (
                  <Circle className="h-5 w-5 flex-shrink-0 text-gray-400" />
                )}
                <div>
                  <div
                    className={`font-medium ${
                      isCompleted ? "text-green-900" : "text-gray-900"
                    }`}
                  >
                    {prereq.service_name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {prereq.description}
                  </div>
                  {isCompleted && (
                    <div className="mt-1 text-xs text-green-700">
                      ✓ Completed
                    </div>
                  )}
                </div>
              </div>

              {!isCompleted && onQuickBook && (
                <button
                  onClick={() => onQuickBook(prereq.service_id)}
                  className="ml-2 flex-shrink-0 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Book Now
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Info */}
      <div className="text-xs text-blue-700">
        Complete all prerequisites to unlock dependent services
      </div>
    </div>
  );
};

export default PrerequisiteDisplay;
