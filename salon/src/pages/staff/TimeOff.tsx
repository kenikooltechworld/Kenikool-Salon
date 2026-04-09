import { useState } from "react";
import {
  useMyTimeOffRequests,
  useCreateMyTimeOffRequest,
} from "@/hooks/useMyTimeOffRequests";
import {
  StaffTimeOffForm,
  type TimeOffFormData,
} from "@/components/staff/StaffTimeOffForm";
import { StaffTimeOffList } from "@/components/staff/StaffTimeOffList";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

const ALLOCATED_DAYS = 20; // Default allocated days

export default function StaffTimeOff() {
  const { showToast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch time off requests
  const {
    data: requests = [],
    isLoading,
    error,
    refetch,
  } = useMyTimeOffRequests();

  // Create time off request mutation
  const createTimeOffMutation = useCreateMyTimeOffRequest();

  // Handle form submission
  const handleSubmitTimeOff = async (formData: TimeOffFormData) => {
    setIsSubmitting(true);
    try {
      // Validate reason is not empty
      if (!formData.reason || formData.reason.trim() === "") {
        showToast({
          title: "Missing Information",
          description: "Please provide a reason for your time off request",
          variant: "error",
        });
        setIsSubmitting(false);
        return;
      }

      await createTimeOffMutation.mutateAsync({
        start_date: formData.start_date,
        end_date: formData.end_date,
        reason: formData.reason,
      });

      showToast({
        title: "Success",
        description: "Your time off request has been submitted",
      });

      // Refresh the list
      refetch();
    } catch (err: any) {
      // Extract user-friendly error message from API response
      let errorMessage = "Unable to submit your request. Please try again.";

      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        // Map technical errors to user-friendly messages
        if (detail.includes("start_date") || detail.includes("start date")) {
          errorMessage = "The start date must be today or in the future";
        } else if (detail.includes("end_date") || detail.includes("end date")) {
          errorMessage = "The end date must be after the start date";
        } else if (detail.includes("reason")) {
          errorMessage = "Please provide a reason for your time off";
        } else if (detail.includes("Staff member not found")) {
          errorMessage =
            "Unable to process your request. Please contact support.";
        } else {
          errorMessage = detail;
        }
      }

      showToast({
        title: "Unable to Submit",
        description: errorMessage,
        variant: "error",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRefresh = () => {
    refetch();
    showToast({
      title: "Refreshed",
      description: "Time off requests list updated",
    });
  };

  // Calculate time off balance
  const approvedDays = requests
    .filter((req: any) => req.status === "approved")
    .reduce((total: number, req: any) => {
      const start = new Date(req.start_date);
      const end = new Date(req.end_date);
      const days = Math.ceil(
        (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24),
      );
      return total + days;
    }, 0);

  const remainingDays = ALLOCATED_DAYS - approvedDays;

  // Sort requests by date descending (most recent first)
  const sortedRequests = [...requests].sort(
    (a, b) =>
      new Date(b.start_date).getTime() - new Date(a.start_date).getTime(),
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">My Time Off</h1>
          <p className="text-muted-foreground mt-2">
            Submit and manage your time off requests
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      {/* Time Off Balance Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Time Off Balance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Allocated Days</p>
              <p className="text-2xl font-bold text-foreground">
                {ALLOCATED_DAYS}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Approved Days</p>
              <p className="text-2xl font-bold text-foreground">
                {approvedDays}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Remaining Days</p>
              <p
                className={`text-2xl font-bold ${remainingDays >= 0 ? "text-success" : "text-destructive"}`}
              >
                {remainingDays}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Two-column layout: Form on left, List on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Section */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Request Time Off</CardTitle>
            </CardHeader>
            <CardContent>
              <StaffTimeOffForm
                onSubmit={handleSubmitTimeOff}
                isLoading={isSubmitting}
              />
            </CardContent>
          </Card>
        </div>

        {/* List Section */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Your Requests</CardTitle>
            </CardHeader>
            <CardContent>
              <StaffTimeOffList
                requests={sortedRequests}
                isLoading={isLoading}
                error={error?.message}
                onRetry={handleRefresh}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
