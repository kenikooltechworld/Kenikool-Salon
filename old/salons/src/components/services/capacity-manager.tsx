import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckIcon, AlertTriangleIcon, UsersIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface CapacityManagerProps {
  serviceId: string;
  initialCapacity?: number;
}

export function CapacityManager({
  serviceId,
  initialCapacity = 0,
}: CapacityManagerProps) {
  const [maxConcurrent, setMaxConcurrent] = useState(initialCapacity);
  const [showSuccess, setShowSuccess] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    setMaxConcurrent(initialCapacity);
  }, [initialCapacity]);

  const saveMutation = useMutation({
    mutationFn: async (capacity: number) => {
      const response = await apiClient.put(
        `/api/services/${serviceId}/capacity`,
        { max_concurrent_bookings: capacity }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["service-details", serviceId],
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    },
  });

  // Fetch current capacity utilization
  const { data: capacityData } = useQuery({
    queryKey: ["service-capacity", serviceId],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/services/${serviceId}/capacity`
      );
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const handleSave = () => {
    saveMutation.mutate(maxConcurrent);
  };

  const isUnlimited = maxConcurrent === 0;
  const utilizationPercentage = capacityData?.utilization_percentage || 0;
  const availableSlots = capacityData?.available_slots || 0;

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Capacity Management
          </h3>
          <p className="text-sm text-muted-foreground">
            Control how many concurrent bookings are allowed for this service
          </p>
        </div>

        {showSuccess && (
          <Alert variant="success">
            <CheckIcon size={20} />
            <div>
              <h4 className="font-semibold">Success</h4>
              <p className="text-sm">Capacity settings updated successfully</p>
            </div>
          </Alert>
        )}

        {saveMutation.isError && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h4 className="font-semibold">Error</h4>
              <p className="text-sm">
                {saveMutation.error instanceof Error
                  ? saveMutation.error.message
                  : "Failed to update capacity"}
              </p>
            </div>
          </Alert>
        )}

        {/* Capacity Setting */}
        <div>
          <Label htmlFor="max_concurrent">Maximum Concurrent Bookings</Label>
          <Input
            id="max_concurrent"
            type="number"
            min="0"
            value={maxConcurrent}
            onChange={(e) => setMaxConcurrent(parseInt(e.target.value) || 0)}
          />
          <p className="text-xs text-muted-foreground mt-1">
            Maximum number of bookings allowed at the same time (0 = unlimited)
          </p>
        </div>

        {/* Current Utilization */}
        {!isUnlimited && capacityData && (
          <div className="bg-muted/50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-foreground">
                Current Utilization
              </h4>
              <div className="flex items-center gap-2">
                <UsersIcon size={16} className="text-muted-foreground" />
                <span className="text-sm font-medium text-foreground">
                  {availableSlots} / {maxConcurrent} available
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  utilizationPercentage >= 90
                    ? "bg-red-500"
                    : utilizationPercentage >= 70
                    ? "bg-yellow-500"
                    : "bg-green-500"
                }`}
                style={{ width: `${utilizationPercentage}%` }}
              />
            </div>

            <p className="text-xs text-muted-foreground mt-2">
              {utilizationPercentage.toFixed(1)}% capacity used
            </p>
          </div>
        )}

        {isUnlimited && (
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-blue-900 dark:text-blue-100">
              <strong>Unlimited Capacity:</strong> This service has no booking
              limits. Any number of concurrent bookings are allowed.
            </p>
          </div>
        )}

        {/* Capacity Warnings */}
        {!isUnlimited && maxConcurrent < 5 && maxConcurrent > 0 && (
          <Alert variant="warning">
            <AlertTriangleIcon size={20} />
            <div>
              <h4 className="font-semibold">Low Capacity Warning</h4>
              <p className="text-sm">
                Setting a low capacity limit may result in frequent "fully
                booked" situations. Consider increasing the limit or using
                booking rules instead.
              </p>
            </div>
          </Alert>
        )}

        {/* Capacity Info */}
        <div className="bg-muted/50 p-4 rounded-lg">
          <h4 className="font-medium text-foreground mb-2">How it works</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>
              • Capacity limits apply to bookings at the exact same date/time
            </li>
            <li>• When capacity is reached, new bookings will be prevented</li>
            <li>
              • Clients can be added to a waitlist when service is fully booked
            </li>
            <li>• Set to 0 for unlimited concurrent bookings</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="flex-1"
          >
            {saveMutation.isPending ? (
              <>
                <Spinner size="sm" />
                Saving...
              </>
            ) : (
              "Save Capacity Settings"
            )}
          </Button>
          <Button
            variant="outline"
            onClick={() => setMaxConcurrent(initialCapacity)}
          >
            Reset
          </Button>
        </div>
      </div>
    </Card>
  );
}
