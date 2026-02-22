"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ScheduleTemplateModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onTemplateCreated?: () => void;
}

const DAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

export function ScheduleTemplateModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onTemplateCreated,
}: ScheduleTemplateModalProps) {
  const [templateName, setTemplateName] = useState("");
  const [isDefault, setIsDefault] = useState(false);
  const [schedule, setSchedule] = useState<
    Record<string, Array<{ start: string; end: string }>>
  >({
    monday: [{ start: "09:00", end: "17:00" }],
    tuesday: [{ start: "09:00", end: "17:00" }],
    wednesday: [{ start: "09:00", end: "17:00" }],
    thursday: [{ start: "09:00", end: "17:00" }],
    friday: [{ start: "09:00", end: "17:00" }],
    saturday: [{ start: "10:00", end: "16:00" }],
    sunday: [],
  });

  const createTemplateMutation = useMutation({
    mutationFn: async () => {
      if (!templateName.trim()) {
        throw new Error("Template name is required");
      }

      const res = await fetch(`/api/staff/schedule-templates`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          staff_id: staffId,
          name: templateName,
          is_default: isDefault,
          schedule,
        }),
      });

      if (!res.ok) throw new Error("Failed to create template");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Schedule template created");
      onTemplateCreated?.();
      onClose();
      setTemplateName("");
      setIsDefault(false);
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to create template");
    },
  });

  const updateDayTime = (
    day: string,
    index: number,
    field: "start" | "end",
    value: string,
  ) => {
    setSchedule((prev) => {
      const daySchedule = [...(prev[day] || [])];
      if (!daySchedule[index]) {
        daySchedule[index] = { start: "09:00", end: "17:00" };
      }
      daySchedule[index][field] = value;
      return { ...prev, [day]: daySchedule };
    });
  };

  const toggleDay = (day: string) => {
    setSchedule((prev) => ({
      ...prev,
      [day]: prev[day]?.length > 0 ? [] : [{ start: "09:00", end: "17:00" }],
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Schedule Template - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Template Name */}
          <div>
            <Label htmlFor="template-name">Template Name</Label>
            <Input
              id="template-name"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="e.g., Summer Schedule, Default"
              className="mt-1"
            />
          </div>

          {/* Default Template */}
          <div className="flex items-center gap-2">
            <Checkbox
              id="is-default"
              checked={isDefault}
              onCheckedChange={(checked) => setIsDefault(checked as boolean)}
            />
            <Label htmlFor="is-default" className="cursor-pointer">
              Set as default template
            </Label>
          </div>

          {/* Weekly Schedule */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Weekly Schedule</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {DAYS.map((day) => (
                <div key={day} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Checkbox
                      id={`day-${day}`}
                      checked={(schedule[day] || []).length > 0}
                      onCheckedChange={() => toggleDay(day)}
                    />
                    <Label
                      htmlFor={`day-${day}`}
                      className="capitalize cursor-pointer flex-1"
                    >
                      {day}
                    </Label>
                  </div>

                  {(schedule[day] || []).length > 0 && (
                    <div className="ml-6 flex gap-2 items-center">
                      <Input
                        type="time"
                        value={schedule[day][0]?.start || "09:00"}
                        onChange={(e) =>
                          updateDayTime(day, 0, "start", e.target.value)
                        }
                        className="w-24"
                      />
                      <span className="text-sm text-muted-foreground">to</span>
                      <Input
                        type="time"
                        value={schedule[day][0]?.end || "17:00"}
                        onChange={(e) =>
                          updateDayTime(day, 0, "end", e.target.value)
                        }
                        className="w-24"
                      />
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Info */}
          <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-blue-800">
            ℹ️ You can apply this template to staff members for specific date
            ranges.
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => createTemplateMutation.mutate()}
            disabled={!templateName.trim() || createTemplateMutation.isPending}
          >
            {createTemplateMutation.isPending
              ? "Creating..."
              : "Create Template"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
