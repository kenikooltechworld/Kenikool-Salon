import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { useUpdateStylistSchedule } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";

interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  stylist: Stylist;
}

const DAYS = [
  { value: 0, label: "Sunday" },
  { value: 1, label: "Monday" },
  { value: 2, label: "Tuesday" },
  { value: 3, label: "Wednesday" },
  { value: 4, label: "Thursday" },
  { value: 5, label: "Friday" },
  { value: 6, label: "Saturday" },
];

export function ScheduleModal({
  isOpen,
  onClose,
  onSuccess,
  stylist,
}: ScheduleModalProps) {
  const [schedule, setSchedule] = useState<
    Array<{
      day_of_week: number;
      start_time: string;
      end_time: string;
      enabled: boolean;
    }>
  >([]);

  const updateScheduleMutation = useUpdateStylistSchedule();

  useEffect(() => {
    // Debug logging
    console.log("Schedule Modal - stylist data:", {
      hasSchedule: !!stylist?.schedule,
      scheduleType: typeof stylist?.schedule,
      isArray: Array.isArray(stylist?.schedule),
      hasWorkingHours: !!stylist?.schedule?.working_hours,
      workingHoursType: typeof stylist?.schedule?.working_hours,
      workingHoursIsArray: Array.isArray(stylist?.schedule?.working_hours),
      schedule: stylist?.schedule,
    });

    // Check if schedule exists and has working_hours array
    if (
      stylist?.schedule &&
      typeof stylist.schedule === "object" &&
      !Array.isArray(stylist.schedule) &&
      stylist.schedule.working_hours &&
      Array.isArray(stylist.schedule.working_hours)
    ) {
      // Convert day names to day_of_week numbers
      const dayNameToNumber: { [key: string]: number } = {
        sunday: 0,
        monday: 1,
        tuesday: 2,
        wednesday: 3,
        thursday: 4,
        friday: 5,
        saturday: 6,
      };

      // Convert existing schedule to include enabled flag and day_of_week
      const existingSchedule = stylist.schedule.working_hours.map((s: any) => ({
        day_of_week:
          typeof s.day === "string"
            ? dayNameToNumber[s.day.toLowerCase()]
            : s.day_of_week || s.day,
        start_time: s.start_time,
        end_time: s.end_time,
        enabled: s.is_working !== false,
      }));

      // Fill in missing days
      const fullSchedule = DAYS.map((day) => {
        const existing = existingSchedule.find(
          (s: any) => s.day_of_week === day.value
        );
        return (
          existing || {
            day_of_week: day.value,
            start_time: "09:00",
            end_time: "17:00",
            enabled: false,
          }
        );
      });

      setSchedule(fullSchedule);
    } else {
      // Default schedule - also handles case where schedule is incorrectly an array
      console.log("Using default schedule");
      setSchedule(
        DAYS.map((day) => ({
          day_of_week: day.value,
          start_time: "09:00",
          end_time: "17:00",
          enabled: day.value >= 1 && day.value <= 5, // Mon-Fri by default
        }))
      );
    }
  }, [stylist, isOpen]);

  const handleToggleDay = (dayIndex: number) => {
    setSchedule((prev) =>
      prev.map((s, i) => (i === dayIndex ? { ...s, enabled: !s.enabled } : s))
    );
  };

  const handleTimeChange = (
    dayIndex: number,
    field: "start_time" | "end_time",
    value: string
  ) => {
    setSchedule((prev) =>
      prev.map((s, i) => (i === dayIndex ? { ...s, [field]: value } : s))
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Only send enabled days
    const activeSchedule = schedule
      .filter((s) => s.enabled)
      .map(({ enabled: _enabled, ...rest }) => rest);

    try {
      await updateScheduleMutation.mutateAsync({
        id: stylist.id,
        schedule: activeSchedule,
      });
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Error updating schedule:", error);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Schedule - {stylist.name}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Set working hours for each day of the week
          </p>

          <div className="space-y-3">
            {schedule.map((day, index) => (
              <div
                key={day.day_of_week}
                className="p-3 border border-[var(--border)] rounded-lg"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-foreground">
                    {DAYS[index].label}
                  </span>
                  <Switch
                    checked={day.enabled}
                    onChange={() => handleToggleDay(index)}
                  />
                </div>

                {day.enabled && (
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs text-muted-foreground mb-1">
                        Start Time
                      </label>
                      <Input
                        type="time"
                        value={day.start_time}
                        onChange={(e) =>
                          handleTimeChange(index, "start_time", e.target.value)
                        }
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-muted-foreground mb-1">
                        End Time
                      </label>
                      <Input
                        type="time"
                        value={day.end_time}
                        onChange={(e) =>
                          handleTimeChange(index, "end_time", e.target.value)
                        }
                        required
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={updateScheduleMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={updateScheduleMutation.isPending}
            >
              {updateScheduleMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Saving...
                </>
              ) : (
                "Save Schedule"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
