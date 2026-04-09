import { useState, useEffect } from "react";
import {
  useStaffSettings,
  useUpdateStaffSettings,
} from "@/hooks/staff/useStaffSettings";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

const DAYS_OF_WEEK = [
  { value: "monday", label: "Monday" },
  { value: "tuesday", label: "Tuesday" },
  { value: "wednesday", label: "Wednesday" },
  { value: "thursday", label: "Thursday" },
  { value: "friday", label: "Friday" },
  { value: "saturday", label: "Saturday" },
  { value: "sunday", label: "Sunday" },
];

export default function StaffAvailabilityForm() {
  const { data: settings, isLoading } = useStaffSettings();
  const updateSettings = useUpdateStaffSettings();
  const { addToast } = useToast();

  const [workingHoursStart, setWorkingHoursStart] = useState("");
  const [workingHoursEnd, setWorkingHoursEnd] = useState("");
  const [daysOff, setDaysOff] = useState<string[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (settings) {
      setWorkingHoursStart(settings.working_hours_start || "");
      setWorkingHoursEnd(settings.working_hours_end || "");
      setDaysOff(settings.days_off || []);
    }
  }, [settings]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Validate time format (HH:MM)
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;

    if (workingHoursStart && !timeRegex.test(workingHoursStart)) {
      newErrors.workingHoursStart =
        "Invalid time format. Use HH:MM (e.g., 09:00)";
    }

    if (workingHoursEnd && !timeRegex.test(workingHoursEnd)) {
      newErrors.workingHoursEnd =
        "Invalid time format. Use HH:MM (e.g., 17:00)";
    }

    // Validate that end time is after start time
    if (
      workingHoursStart &&
      workingHoursEnd &&
      timeRegex.test(workingHoursStart) &&
      timeRegex.test(workingHoursEnd)
    ) {
      const [startHour, startMin] = workingHoursStart.split(":").map(Number);
      const [endHour, endMin] = workingHoursEnd.split(":").map(Number);
      const startMinutes = startHour * 60 + startMin;
      const endMinutes = endHour * 60 + endMin;

      if (endMinutes <= startMinutes) {
        newErrors.workingHoursEnd = "End time must be after start time";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleDayOffToggle = (day: string) => {
    setDaysOff((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day],
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await updateSettings.mutateAsync({
        working_hours_start: workingHoursStart || undefined,
        working_hours_end: workingHoursEnd || undefined,
        days_off: daysOff,
      });

      addToast({
        title: "Success",
        description: "Availability preferences updated successfully",
        variant: "success",
      });
    } catch (error: any) {
      addToast({
        title: "Error",
        description:
          error.message || "Failed to update availability preferences",
        variant: "error",
      });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Spinner size="lg" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Availability Preferences</CardTitle>
        <CardDescription>Set your working hours and days off</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Working Hours */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Working Hours</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="workingHoursStart">Start Time</Label>
                <Input
                  id="workingHoursStart"
                  type="time"
                  value={workingHoursStart}
                  onChange={(e) => setWorkingHoursStart(e.target.value)}
                  placeholder="09:00"
                />
                {errors.workingHoursStart && (
                  <p className="text-sm text-destructive">
                    {errors.workingHoursStart}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="workingHoursEnd">End Time</Label>
                <Input
                  id="workingHoursEnd"
                  type="time"
                  value={workingHoursEnd}
                  onChange={(e) => setWorkingHoursEnd(e.target.value)}
                  placeholder="17:00"
                />
                {errors.workingHoursEnd && (
                  <p className="text-sm text-destructive">
                    {errors.workingHoursEnd}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Days Off */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium">Days Off</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {DAYS_OF_WEEK.map((day) => (
                <div key={day.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={day.value}
                    checked={daysOff.includes(day.value)}
                    onCheckedChange={() => handleDayOffToggle(day.value)}
                  />
                  <Label
                    htmlFor={day.value}
                    className="text-sm font-normal cursor-pointer"
                  >
                    {day.label}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button type="submit" disabled={updateSettings.isPending}>
              {updateSettings.isPending ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
