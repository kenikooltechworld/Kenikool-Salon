import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";

interface StaffTimeOffFormProps {
  onSubmit?: (data: TimeOffFormData) => void;
  isLoading?: boolean;
  onSuccess?: () => void;
}

export interface TimeOffFormData {
  start_date: string;
  end_date: string;
  reason?: string;
}

export function StaffTimeOffForm({
  onSubmit,
  isLoading = false,
  onSuccess,
}: StaffTimeOffFormProps) {
  const [formData, setFormData] = useState<TimeOffFormData>({
    start_date: "",
    end_date: "",
    reason: "",
  });
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous messages
    setSuccessMessage(null);
    setErrorMessage(null);

    // Validate dates
    if (!formData.start_date || !formData.end_date) {
      setErrorMessage("Both start and end dates are required");
      return;
    }

    const start = new Date(formData.start_date);
    const end = new Date(formData.end_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Check if start date is in the future or today
    if (start < today) {
      setErrorMessage("Start date must be today or in the future");
      return;
    }

    // Check if start date is before end date
    if (start >= end) {
      setErrorMessage("Start date must be before end date");
      return;
    }

    // Call the onSubmit callback
    if (onSubmit) {
      onSubmit(formData);
      // Clear form data after submission
      setFormData({
        start_date: "",
        end_date: "",
        reason: "",
      });
      onSuccess?.();
    }
  };

  const daysDuration =
    formData.start_date && formData.end_date
      ? Math.ceil(
          (new Date(formData.end_date).getTime() -
            new Date(formData.start_date).getTime()) /
            (1000 * 60 * 60 * 24),
        )
      : 0;

  return (
    <form onSubmit={handleFormSubmit} className="space-y-4">
      {successMessage && (
        <Alert className="bg-success/10 border-success/50">
          <CheckCircleIcon size={16} className="text-success" />
          <AlertDescription className="text-success">
            {successMessage}
          </AlertDescription>
        </Alert>
      )}

      {errorMessage && (
        <Alert className="bg-destructive/10 border-destructive/50">
          <AlertCircleIcon size={16} className="text-destructive" />
          <AlertDescription className="text-destructive">
            {errorMessage}
          </AlertDescription>
        </Alert>
      )}

      <div>
        <Label htmlFor="start-date">Start Date *</Label>
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
        <Label htmlFor="end-date">End Date *</Label>
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

      {formData.start_date && formData.end_date && daysDuration > 0 && (
        <div className="text-sm text-muted-foreground bg-muted p-2 rounded">
          Duration: {daysDuration} day{daysDuration !== 1 ? "s" : ""}
        </div>
      )}

      <div>
        <Label htmlFor="reason">Reason *</Label>
        <Textarea
          id="reason"
          placeholder="Enter reason for time off"
          value={formData.reason}
          onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
          rows={3}
          required
        />
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? "Submitting..." : "Request Time Off"}
      </Button>
    </form>
  );
}
