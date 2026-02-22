/**
 * PrerequisiteChecker Component
 * Validates prerequisite completion before booking
 * Validates: Requirements 7.1, 7.2
 */
import React from "react";
import { useCheckPrerequisites } from "../../lib/api/hooks/usePrerequisites";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";

interface PrerequisiteCheckerProps {
  serviceId: string;
  onProceed?: () => void;
  onBookPrerequisite?: (prerequisiteId: string) => void;
}

/**
 * Component for validating prerequisite completion before booking
 */
export const PrerequisiteChecker: React.FC<PrerequisiteCheckerProps> = ({
  serviceId,
  onProceed,
  onBookPrerequisite,
}) => {
  const { data, isLoading, error } = useCheckPrerequisites(serviceId);

  if (isLoading) {
    return (
      <Card className="p-4">
        <div className="text-center text-sm text-muted-foreground">
          Checking prerequisites...
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-4 border-destructive bg-destructive/10">
        <div className="text-sm text-destructive">
          Failed to check prerequisites
        </div>
      </Card>
    );
  }

  if (!data) {
    return null;
  }

  // All prerequisites met
  if (data.all_prerequisites_met) {
    return (
      <Card className="p-4 border-green-200 bg-green-50">
        <div className="flex items-center gap-3 mb-3">
          <CheckCircleIcon size={20} className="text-green-600" />
          <div>
            <div className="font-medium text-green-900">
              All prerequisites completed
            </div>
            <div className="text-sm text-green-700">
              You're eligible to book this service
            </div>
          </div>
        </div>
        {onProceed && (
          <Button onClick={onProceed} className="w-full mt-3">
            Proceed to Booking
          </Button>
        )}
      </Card>
    );
  }

  // Prerequisites not met
  return (
    <Card className="p-4 border-accent bg-accent/10 space-y-4">
      {/* Header */}
      <div className="flex items-start gap-3">
        <AlertCircleIcon
          size={20}
          className="text-accent mt-0.5 flex-shrink-0"
        />
        <div>
          <div className="font-semibold text-foreground">
            Prerequisites Required
          </div>
          <div className="text-sm text-muted-foreground">
            You must complete the following services before booking this one
          </div>
        </div>
      </div>

      {/* Missing Prerequisites */}
      {data.missing_prerequisites.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-foreground">
            Required Services:
          </div>
          {data.missing_prerequisites.map((prereq) => (
            <Card
              key={prereq.id}
              className="p-3 flex items-start justify-between"
            >
              <div className="flex-1">
                <div className="font-medium text-foreground">
                  {prereq.service_name}
                </div>
                <div className="text-sm text-muted-foreground">
                  {prereq.description}
                </div>
              </div>
              {onBookPrerequisite && (
                <Button
                  onClick={() => onBookPrerequisite(prereq.service_id)}
                  size="sm"
                  className="ml-3 shrink-0"
                >
                  Book
                </Button>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Completed Prerequisites */}
      {data.completed_prerequisites.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-foreground">
            Completed Services:
          </div>
          {data.completed_prerequisites.map((prereq) => (
            <Card key={prereq.id} className="p-3 flex items-center gap-2">
              <CheckCircleIcon size={16} className="text-green-600" />
              <div className="flex-1">
                <div className="font-medium text-foreground">
                  {prereq.service_name}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Info */}
      <div className="text-xs text-muted-foreground">
        Complete all required services to proceed with this booking
      </div>
    </Card>
  );
};

export default PrerequisiteChecker;
