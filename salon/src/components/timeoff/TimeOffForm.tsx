import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface TimeOffFormProps {
  staffId: string;
  staffName?: string;
  onSubmit: (data: TimeOffFormData) => void;
  isLoading?: boolean;
}

export interface TimeOffFormData {
  staff_id: string;
  start_date: string;
  end_date: string;
  reason: string;
}

export function TimeOffForm({
  staffId,
  staffName,
  onSubmit,
  isLoading = false,
}: TimeOffFormProps) {
  const [formData, setFormData] = useState<TimeOffFormData>({
    staff_id: staffId,
    start_date: "",
    end_date: "",
    reason: "",
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
        <Label htmlFor="start-date">Start Date</Label>
        <Input
          id="start-date"
          type="date"
          value={formData.start_date}
          onChange={(e) =>
            setFormData({ ...formData, start_date: e.target.value })
          }
          required
        />
      </div>

      <div>
        <Label htmlFor="end-date">End Date</Label>
        <Input
          id="end-date"
          type="date"
          value={formData.end_date}
          onChange={(e) =>
            setFormData({ ...formData, end_date: e.target.value })
          }
          required
        />
      </div>

      <div>
        <Label htmlFor="reason">Reason</Label>
        <Textarea
          id="reason"
          value={formData.reason}
          onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
          placeholder="Enter reason for time off"
          required
        />
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? "Submitting..." : "Request Time Off"}
      </Button>
    </form>
  );
}
