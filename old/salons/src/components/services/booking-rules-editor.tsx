import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckIcon, AlertTriangleIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface BookingRules {
  buffer_time_before: number;
  buffer_time_after: number;
  max_bookings_per_day: number;
  advance_booking_min: number;
  advance_booking_max: number;
  cancellation_deadline: number;
  cancellation_penalty: number;
  allow_override: boolean;
}

interface BookingRulesEditorProps {
  serviceId: string;
  initialRules?: BookingRules;
}

const defaultRules: BookingRules = {
  buffer_time_before: 0,
  buffer_time_after: 0,
  max_bookings_per_day: 0,
  advance_booking_min: 0,
  advance_booking_max: 365,
  cancellation_deadline: 24,
  cancellation_penalty: 0,
  allow_override: true,
};

export function BookingRulesEditor({
  serviceId,
  initialRules,
}: BookingRulesEditorProps) {
  const [rules, setRules] = useState<BookingRules>(
    initialRules || defaultRules
  );
  const [showSuccess, setShowSuccess] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (initialRules) {
      setRules(initialRules);
    }
  }, [initialRules]);

  const saveMutation = useMutation({
    mutationFn: async (rules: BookingRules) => {
      const response = await apiClient.put(
        `/api/services/${serviceId}/booking-rules`,
        rules
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

  const handleSave = () => {
    saveMutation.mutate(rules);
  };

  const handleReset = () => {
    setRules(initialRules || defaultRules);
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Booking Rules
          </h3>
          <p className="text-sm text-muted-foreground">
            Configure rules and constraints for booking this service
          </p>
        </div>

        {showSuccess && (
          <Alert variant="success">
            <CheckIcon size={20} />
            <div>
              <h4 className="font-semibold">Success</h4>
              <p className="text-sm">Booking rules updated successfully</p>
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
                  : "Failed to update booking rules"}
              </p>
            </div>
          </Alert>
        )}

        {/* Buffer Times */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="buffer_before">Buffer Time Before (minutes)</Label>
            <Input
              id="buffer_before"
              type="number"
              min="0"
              value={rules.buffer_time_before}
              onChange={(e) =>
                setRules({
                  ...rules,
                  buffer_time_before: parseInt(e.target.value) || 0,
                })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              Time gap required before this booking
            </p>
          </div>

          <div>
            <Label htmlFor="buffer_after">Buffer Time After (minutes)</Label>
            <Input
              id="buffer_after"
              type="number"
              min="0"
              value={rules.buffer_time_after}
              onChange={(e) =>
                setRules({
                  ...rules,
                  buffer_time_after: parseInt(e.target.value) || 0,
                })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              Time gap required after this booking
            </p>
          </div>
        </div>

        {/* Max Bookings Per Day */}
        <div>
          <Label htmlFor="max_bookings">Max Bookings Per Day</Label>
          <Input
            id="max_bookings"
            type="number"
            min="0"
            value={rules.max_bookings_per_day}
            onChange={(e) =>
              setRules({
                ...rules,
                max_bookings_per_day: parseInt(e.target.value) || 0,
              })
            }
          />
          <p className="text-xs text-muted-foreground mt-1">
            Maximum bookings allowed per day (0 = unlimited)
          </p>
        </div>

        {/* Advance Booking Window */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="advance_min">Minimum Days in Advance</Label>
            <Input
              id="advance_min"
              type="number"
              min="0"
              value={rules.advance_booking_min}
              onChange={(e) =>
                setRules({
                  ...rules,
                  advance_booking_min: parseInt(e.target.value) || 0,
                })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              Minimum days required to book in advance
            </p>
          </div>

          <div>
            <Label htmlFor="advance_max">Maximum Days in Advance</Label>
            <Input
              id="advance_max"
              type="number"
              min="1"
              value={rules.advance_booking_max}
              onChange={(e) =>
                setRules({
                  ...rules,
                  advance_booking_max: parseInt(e.target.value) || 365,
                })
              }
            />
            <p className="text-xs text-muted-foreground mt-1">
              Maximum days allowed to book in advance
            </p>
          </div>
        </div>

        {/* Cancellation Policy */}
        <div className="border-t border-border pt-6">
          <h4 className="font-medium text-foreground mb-4">
            Cancellation Policy
          </h4>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="cancel_deadline">
                Cancellation Deadline (hours)
              </Label>
              <Input
                id="cancel_deadline"
                type="number"
                min="0"
                value={rules.cancellation_deadline}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    cancellation_deadline: parseInt(e.target.value) || 24,
                  })
                }
              />
              <p className="text-xs text-muted-foreground mt-1">
                Hours before booking when penalty applies
              </p>
            </div>

            <div>
              <Label htmlFor="cancel_penalty">Cancellation Penalty (%)</Label>
              <Input
                id="cancel_penalty"
                type="number"
                min="0"
                max="100"
                value={rules.cancellation_penalty}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    cancellation_penalty: parseFloat(e.target.value) || 0,
                  })
                }
              />
              <p className="text-xs text-muted-foreground mt-1">
                Percentage of booking price charged as penalty
              </p>
            </div>
          </div>
        </div>

        {/* Allow Override */}
        <div className="flex items-center justify-between border-t border-border pt-6">
          <div>
            <Label htmlFor="allow_override">Allow Manager Override</Label>
            <p className="text-xs text-muted-foreground mt-1">
              Allow managers to bypass these rules when needed
            </p>
          </div>
          <Switch
            id="allow_override"
            checked={rules.allow_override}
            onCheckedChange={(checked) =>
              setRules({ ...rules, allow_override: checked })
            }
          />
        </div>

        {/* Preview */}
        <div className="bg-muted/50 p-4 rounded-lg">
          <h4 className="font-medium text-foreground mb-2">Rules Summary</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            {rules.buffer_time_before > 0 && (
              <li>• {rules.buffer_time_before} min buffer before booking</li>
            )}
            {rules.buffer_time_after > 0 && (
              <li>• {rules.buffer_time_after} min buffer after booking</li>
            )}
            {rules.max_bookings_per_day > 0 && (
              <li>• Max {rules.max_bookings_per_day} bookings per day</li>
            )}
            {rules.advance_booking_min > 0 && (
              <li>
                • Must book at least {rules.advance_booking_min} days ahead
              </li>
            )}
            {rules.advance_booking_max < 365 && (
              <li>• Can book up to {rules.advance_booking_max} days ahead</li>
            )}
            {rules.cancellation_penalty > 0 && (
              <li>
                • {rules.cancellation_penalty}% penalty if cancelled within{" "}
                {rules.cancellation_deadline} hours
              </li>
            )}
            {rules.allow_override && <li>• Manager override allowed</li>}
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
              "Save Rules"
            )}
          </Button>
          <Button variant="outline" onClick={handleReset}>
            Reset
          </Button>
        </div>
      </div>
    </Card>
  );
}
