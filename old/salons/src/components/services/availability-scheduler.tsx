import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckIcon, AlertTriangleIcon, CalendarIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQueryClient } from "@tanstack/react-query";

interface ServiceAvailability {
  days_of_week: number[];
  time_ranges: Array<{ start: string; end: string }>;
  seasonal_ranges: Array<{ start: string; end: string }>;
  is_limited_time: boolean;
  limited_time_end: string | null;
}

interface AvailabilitySchedulerProps {
  serviceId: string;
  initialAvailability?: ServiceAvailability;
}

const defaultAvailability: ServiceAvailability = {
  days_of_week: [0, 1, 2, 3, 4, 5, 6],
  time_ranges: [],
  seasonal_ranges: [],
  is_limited_time: false,
  limited_time_end: null,
};

const dayNames = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

export function AvailabilityScheduler({
  serviceId,
  initialAvailability,
}: AvailabilitySchedulerProps) {
  const [availability, setAvailability] = useState<ServiceAvailability>(
    initialAvailability
      ? { ...defaultAvailability, ...initialAvailability }
      : defaultAvailability,
  );
  const [showSuccess, setShowSuccess] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    if (initialAvailability) {
      setAvailability({ ...defaultAvailability, ...initialAvailability });
    }
  }, [initialAvailability]);

  const saveMutation = useMutation({
    mutationFn: async (availability: ServiceAvailability) => {
      const response = await apiClient.put(
        `/api/services/${serviceId}/availability`,
        availability,
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
    saveMutation.mutate(availability);
  };

  const toggleDay = (day: number) => {
    const days = availability.days_of_week;
    if (days.includes(day)) {
      setAvailability({
        ...availability,
        days_of_week: days.filter((d) => d !== day),
      });
    } else {
      setAvailability({
        ...availability,
        days_of_week: [...days, day].sort(),
      });
    }
  };

  const addTimeRange = () => {
    setAvailability({
      ...availability,
      time_ranges: [
        ...availability.time_ranges,
        { start: "09:00", end: "17:00" },
      ],
    });
  };

  const updateTimeRange = (
    index: number,
    field: "start" | "end",
    value: string,
  ) => {
    const ranges = [...availability.time_ranges];
    ranges[index][field] = value;
    setAvailability({ ...availability, time_ranges: ranges });
  };

  const removeTimeRange = (index: number) => {
    setAvailability({
      ...availability,
      time_ranges: availability.time_ranges.filter((_, i) => i !== index),
    });
  };

  const addSeasonalRange = () => {
    const today = new Date().toISOString().split("T")[0];
    setAvailability({
      ...availability,
      seasonal_ranges: [
        ...availability.seasonal_ranges,
        { start: today, end: today },
      ],
    });
  };

  const updateSeasonalRange = (
    index: number,
    field: "start" | "end",
    value: string,
  ) => {
    const ranges = [...availability.seasonal_ranges];
    ranges[index][field] = value;
    setAvailability({ ...availability, seasonal_ranges: ranges });
  };

  const removeSeasonalRange = (index: number) => {
    setAvailability({
      ...availability,
      seasonal_ranges: availability.seasonal_ranges.filter(
        (_, i) => i !== index,
      ),
    });
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Service Availability
          </h3>
          <p className="text-sm text-muted-foreground">
            Configure when this service is available for booking
          </p>
        </div>

        {showSuccess && (
          <Alert variant="success">
            <CheckIcon size={20} />
            <div>
              <h4 className="font-semibold">Success</h4>
              <p className="text-sm">Availability updated successfully</p>
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
                  : "Failed to update availability"}
              </p>
            </div>
          </Alert>
        )}

        {/* Days of Week */}
        <div>
          <Label>Available Days</Label>
          <div className="grid grid-cols-7 gap-2 mt-2">
            {dayNames.map((day, index) => (
              <button
                key={index}
                onClick={() => toggleDay(index)}
                className={`p-2 text-sm rounded-lg border transition-all duration-200 cursor-pointer ${
                  availability.days_of_week.includes(index)
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-background text-muted-foreground border-border hover:bg-muted hover:shadow-sm"
                }`}
              >
                {day.slice(0, 3)}
              </button>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Select the days when this service is available
          </p>
        </div>

        {/* Time Ranges */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <Label>Time Ranges</Label>
            <Button variant="outline" size="sm" onClick={addTimeRange}>
              Add Time Range
            </Button>
          </div>

          {availability.time_ranges.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No time restrictions (available all day)
            </p>
          ) : (
            <div className="space-y-2">
              {availability.time_ranges.map((range, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    type="time"
                    value={range.start}
                    onChange={(e) =>
                      updateTimeRange(index, "start", e.target.value)
                    }
                  />
                  <span className="text-muted-foreground">to</span>
                  <Input
                    type="time"
                    value={range.end}
                    onChange={(e) =>
                      updateTimeRange(index, "end", e.target.value)
                    }
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeTimeRange(index)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-2">
            Specify time ranges when service is available (leave empty for all
            day)
          </p>
        </div>

        {/* Seasonal Ranges */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <Label>Seasonal Availability</Label>
            <Button variant="outline" size="sm" onClick={addSeasonalRange}>
              Add Season
            </Button>
          </div>

          {availability.seasonal_ranges.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No seasonal restrictions (available year-round)
            </p>
          ) : (
            <div className="space-y-2">
              {availability.seasonal_ranges.map((range, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    type="date"
                    value={range.start}
                    onChange={(e) =>
                      updateSeasonalRange(index, "start", e.target.value)
                    }
                  />
                  <span className="text-muted-foreground">to</span>
                  <Input
                    type="date"
                    value={range.end}
                    onChange={(e) =>
                      updateSeasonalRange(index, "end", e.target.value)
                    }
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeSeasonalRange(index)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          )}
          <p className="text-xs text-muted-foreground mt-2">
            Specify date ranges when service is available (leave empty for
            year-round)
          </p>
        </div>

        {/* Limited Time Offer */}
        <div className="border-t border-border pt-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <Label htmlFor="limited_time">Limited Time Offer</Label>
              <p className="text-xs text-muted-foreground mt-1">
                Mark this service as a limited time offer
              </p>
            </div>
            <Switch
              id="limited_time"
              checked={availability.is_limited_time}
              onCheckedChange={(checked) =>
                setAvailability({ ...availability, is_limited_time: checked })
              }
            />
          </div>

          {availability.is_limited_time && (
            <div>
              <Label htmlFor="limited_end">Offer End Date</Label>
              <Input
                id="limited_end"
                type="datetime-local"
                value={availability.limited_time_end || ""}
                onChange={(e) =>
                  setAvailability({
                    ...availability,
                    limited_time_end: e.target.value,
                  })
                }
              />
              <p className="text-xs text-muted-foreground mt-1">
                Service will be automatically deactivated after this date
              </p>
            </div>
          )}
        </div>

        {/* Preview */}
        <div className="bg-muted/50 p-4 rounded-lg">
          <h4 className="font-medium text-foreground mb-2">
            Availability Summary
          </h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>
              • Available on:{" "}
              {availability.days_of_week.length === 7
                ? "All days"
                : availability.days_of_week.map((d) => dayNames[d]).join(", ")}
            </li>
            {availability.time_ranges.length > 0 && (
              <li>
                • Time ranges:{" "}
                {availability.time_ranges
                  .map((r) => `${r.start} - ${r.end}`)
                  .join(", ")}
              </li>
            )}
            {availability.seasonal_ranges.length > 0 && (
              <li>
                • Seasonal:{" "}
                {availability.seasonal_ranges
                  .map((r) => `${r.start} to ${r.end}`)
                  .join(", ")}
              </li>
            )}
            {availability.is_limited_time && availability.limited_time_end && (
              <li>• Limited offer until {availability.limited_time_end}</li>
            )}
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
              "Save Availability"
            )}
          </Button>
          <Button
            variant="outline"
            onClick={() =>
              setAvailability(initialAvailability || defaultAvailability)
            }
          >
            Reset
          </Button>
        </div>
      </div>
    </Card>
  );
}
