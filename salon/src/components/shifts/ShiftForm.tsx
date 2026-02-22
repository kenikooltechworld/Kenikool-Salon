import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Shift } from "@/hooks/useShifts";

interface ShiftFormProps {
  staffId: string;
  staffName?: string;
  shift?: Shift;
  onSubmit: (data: ShiftFormData) => void;
  isLoading?: boolean;
}

export interface ShiftFormData {
  staff_id: string;
  start_time: string;
  end_time: string;
  status?: "scheduled" | "in_progress" | "completed" | "cancelled";
}

export function ShiftForm({
  staffId,
  staffName,
  shift,
  onSubmit,
  isLoading = false,
}: ShiftFormProps) {
  const [formData, setFormData] = useState<ShiftFormData>({
    staff_id: staffId,
    start_time: shift?.start_time || "",
    end_time: shift?.end_time || "",
    status: shift?.status || "scheduled",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="staff-name">Staff Member</Label>
        <Input
          id="staff-name"
          type="text"
          value={staffName || ""}
          disabled
          className="bg-gray-100"
        />
      </div>

      <div>
        <Label htmlFor="start-time">Start Date & Time</Label>
        <Input
          id="start-time"
          type="datetime-local"
          value={formData.start_time}
          onChange={(e) =>
            setFormData({ ...formData, start_time: e.target.value })
          }
          required
        />
      </div>

      <div>
        <Label htmlFor="end-time">End Date & Time</Label>
        <Input
          id="end-time"
          type="datetime-local"
          value={formData.end_time}
          onChange={(e) =>
            setFormData({ ...formData, end_time: e.target.value })
          }
          required
        />
      </div>

      <div>
        <Label htmlFor="status">Status</Label>
        <Select
          value={formData.status || "scheduled"}
          onValueChange={(value) =>
            setFormData({
              ...formData,
              status: value as ShiftFormData["status"],
            })
          }
        >
          <option value="scheduled">Scheduled</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </Select>
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? "Saving..." : shift ? "Update Shift" : "Create Shift"}
      </Button>
    </form>
  );
}
