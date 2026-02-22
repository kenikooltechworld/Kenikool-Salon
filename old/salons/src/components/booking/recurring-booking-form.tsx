/**
 * RecurringBookingForm Component
 * Allows selection of recurrence frequency and interval
 * Validates: Requirements 8.1
 */
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { CalendarIcon } from "@/components/icons";

interface RecurringBookingFormProps {
  onSubmit: (recurrence: RecurrenceConfig) => void;
  loading?: boolean;
}

export interface RecurrenceConfig {
  frequency: "daily" | "weekly" | "monthly" | "custom";
  interval: number;
  endType: "occurrences" | "date";
  endValue: number | string;
}

/**
 * Component for configuring recurring bookings
 */
export const RecurringBookingForm: React.FC<RecurringBookingFormProps> = ({
  onSubmit,
  loading = false,
}) => {
  const [frequency, setFrequency] =
    useState<RecurrenceConfig["frequency"]>("weekly");
  const [interval, setInterval] = useState(1);
  const [endType, setEndType] = useState<"occurrences" | "date">("occurrences");
  const [endValue, setEndValue] = useState<number | string>(4);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      frequency,
      interval,
      endType,
      endValue,
    });
  };

  const frequencyLabels = {
    daily: "Every Day",
    weekly: "Every Week",
    monthly: "Every Month",
    custom: "Custom",
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Card className="p-4 border-primary/20 bg-primary/5 space-y-4">
        {/* Header */}
        <div className="flex items-center gap-2">
          <CalendarIcon size={20} className="text-primary" />
          <h3 className="font-semibold text-foreground">Recurring Booking</h3>
        </div>

        {/* Frequency Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">
            Frequency
          </label>
          <div className="grid grid-cols-2 gap-2">
            {(["daily", "weekly", "monthly", "custom"] as const).map((freq) => (
              <Button
                key={freq}
                type="button"
                onClick={() => setFrequency(freq)}
                variant={frequency === freq ? "primary" : "outline"}
                size="sm"
                className="text-xs"
              >
                {frequencyLabels[freq]}
              </Button>
            ))}
          </div>
        </div>

        {/* Interval */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">
            Repeat Every
          </label>
          <div className="flex items-center gap-2">
            <Input
              type="number"
              min="1"
              max="365"
              value={interval}
              onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
              className="w-20"
            />
            <span className="text-sm text-muted-foreground">
              {frequency === "daily" && "day(s)"}
              {frequency === "weekly" && "week(s)"}
              {frequency === "monthly" && "month(s)"}
              {frequency === "custom" && "day(s)"}
            </span>
          </div>
        </div>

        {/* End Type */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Ends</label>
          <RadioGroup
            value={endType}
            onValueChange={(value: any) => setEndType(value)}
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="occurrences" id="occurrences" />
              <Label htmlFor="occurrences" className="text-sm cursor-pointer">
                After occurrences
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="date" id="end-date" />
              <Label htmlFor="end-date" className="text-sm cursor-pointer">
                On specific date
              </Label>
            </div>
          </RadioGroup>
        </div>

        {/* End Value */}
        <div className="space-y-2">
          {endType === "occurrences" ? (
            <>
              <label className="text-sm font-medium text-foreground">
                Number of Occurrences
              </label>
              <Input
                type="number"
                min="1"
                max="365"
                value={endValue}
                onChange={(e) => setEndValue(parseInt(e.target.value) || 1)}
              />
            </>
          ) : (
            <>
              <label className="text-sm font-medium text-foreground">
                End Date
              </label>
              <Input
                type="date"
                value={endValue as string}
                onChange={(e) => setEndValue(e.target.value)}
              />
            </>
          )}
        </div>

        {/* Summary */}
        <Card className="p-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <CalendarIcon size={16} />
            <span>
              {frequency === "daily" && `Every day`}
              {frequency === "weekly" && `Every ${interval} week(s)`}
              {frequency === "monthly" && `Every ${interval} month(s)`}
              {frequency === "custom" && `Every ${interval} day(s)`}
              {endType === "occurrences" && ` for ${endValue} times`}
              {endType === "date" && ` until ${endValue}`}
            </span>
          </div>
        </Card>
      </Card>

      {/* Submit */}
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? "Creating..." : "Create Recurring Booking"}
      </Button>
    </form>
  );
};

export default RecurringBookingForm;
