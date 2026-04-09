import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  useMyAppointment,
  useCompleteAppointment,
  useCancelAppointment,
  useRescheduleAppointment,
  useUpdateAppointmentNotes,
} from "@/hooks/useMyAppointments";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { formatDate, formatTime } from "@/lib/utils/format";
import { ArrowLeftIcon } from "@/components/icons";
import AppointmentCancellationModal from "@/components/staff/AppointmentCancellationModal";
import AppointmentRescheduleModal from "@/components/staff/AppointmentRescheduleModal";
import AppointmentNotesSection from "@/components/staff/AppointmentNotesSection";
import type { Appointment } from "@/hooks/useAppointments";
import type { BadgeProps } from "@/components/ui/badge";

const statusVariants: Record<
  Appointment["status"],
  NonNullable<BadgeProps["variant"]>
> = {
  scheduled: "default",
  confirmed: "secondary",
  in_progress: "accent",
  completed: "outline",
  cancelled: "destructive",
  no_show: "destructive",
};

const statusLabels: Record<Appointment["status"], string> = {
  scheduled: "Scheduled",
  confirmed: "Confirmed",
  in_progress: "In Progress",
  completed: "Completed",
  cancelled: "Cancelled",
  no_show: "No Show",
};

export default function AppointmentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);

  const { data: appointment, isLoading, error } = useMyAppointment(id || "");

  const completeAppointmentMutation = useCompleteAppointment();
  const cancelAppointmentMutation = useCancelAppointment();
  const rescheduleAppointmentMutation = useRescheduleAppointment();
  const updateNotesMutation = useUpdateAppointmentNotes();

  const handleCompleteAppointment = async () => {
    if (!id) return;

    try {
      await completeAppointmentMutation.mutateAsync(id);
      showToast({
        title: "Success",
        description: "Appointment marked as completed",
      });
      navigate("/staff/appointments");
    } catch (err: any) {
      let errorMessage =
        "Unable to complete this appointment. Please try again.";

      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (detail.includes("already completed")) {
          errorMessage = "This appointment has already been completed";
        } else if (detail.includes("already cancelled")) {
          errorMessage = "This appointment has been cancelled";
        } else if (detail.includes("not found")) {
          errorMessage = "Appointment not found";
        } else {
          errorMessage = detail;
        }
      }

      showToast({
        title: "Unable to Complete",
        description: errorMessage,
        variant: "error",
      });
    }
  };

  const handleCancelAppointment = async (reason: string) => {
    if (!id) return;

    try {
      await cancelAppointmentMutation.mutateAsync({ id, reason });
      showToast({
        title: "Success",
        description: "Appointment cancelled successfully",
      });
      setShowCancelModal(false);
      navigate("/staff/appointments");
    } catch (err: any) {
      let errorMessage = "Unable to cancel this appointment. Please try again.";

      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (detail.includes("already cancelled")) {
          errorMessage = "This appointment has already been cancelled";
        } else if (detail.includes("already completed")) {
          errorMessage = "Cannot cancel a completed appointment";
        } else if (detail.includes("not found")) {
          errorMessage = "Appointment not found";
        } else if (detail.includes("reason")) {
          errorMessage = "Please provide a reason for cancellation";
        } else {
          errorMessage = detail;
        }
      }

      showToast({
        title: "Unable to Cancel",
        description: errorMessage,
        variant: "error",
      });
    }
  };

  const handleRescheduleAppointment = async (
    newStartTime: string,
    newEndTime: string,
  ) => {
    if (!id) return;

    try {
      await rescheduleAppointmentMutation.mutateAsync({
        id,
        startTime: newStartTime,
        endTime: newEndTime,
      });
      showToast({
        title: "Success",
        description: "Appointment rescheduled successfully",
      });
      setShowRescheduleModal(false);
    } catch (err: any) {
      let errorMessage =
        "Unable to reschedule this appointment. Please try again.";

      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (detail.includes("already cancelled")) {
          errorMessage = "Cannot reschedule a cancelled appointment";
        } else if (detail.includes("already completed")) {
          errorMessage = "Cannot reschedule a completed appointment";
        } else if (detail.includes("not available")) {
          errorMessage = "The selected time slot is not available";
        } else if (detail.includes("in the past")) {
          errorMessage = "Cannot reschedule to a time in the past";
        } else if (detail.includes("not found")) {
          errorMessage = "Appointment not found";
        } else {
          errorMessage = detail;
        }
      }

      showToast({
        title: "Unable to Reschedule",
        description: errorMessage,
        variant: "error",
      });
    }
  };

  const handleUpdateNotes = async (notes: string) => {
    if (!id) return;

    try {
      await updateNotesMutation.mutateAsync({ id, notes });
      showToast({
        title: "Success",
        description: "Notes updated successfully",
      });
    } catch (err: any) {
      let errorMessage = "Unable to update notes. Please try again.";

      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (detail.includes("not found")) {
          errorMessage = "Appointment not found";
        } else if (detail.includes("too long")) {
          errorMessage = "Notes are too long. Please shorten them.";
        } else {
          errorMessage = detail;
        }
      }

      showToast({
        title: "Unable to Update Notes",
        description: errorMessage,
        variant: "error",
      });
      throw err;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/staff/appointments")}
          className="mb-4"
        >
          <ArrowLeftIcon size={16} className="mr-2" />
          Back
        </Button>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error && !appointment) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/staff/appointments")}
          className="mb-4"
        >
          <ArrowLeftIcon size={16} className="mr-2" />
          Back
        </Button>
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-6">
          <p className="text-sm text-destructive font-medium">
            Failed to load appointment
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            {error?.message ||
              "An error occurred while loading the appointment"}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/staff/appointments")}
            className="mt-4"
          >
            Back to Appointments
          </Button>
        </div>
      </div>
    );
  }

  if (!appointment) {
    return (
      <div className="space-y-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/staff/appointments")}
          className="mb-4"
        >
          <ArrowLeftIcon size={16} className="mr-2" />
          Back
        </Button>
        <div className="rounded-lg border border-border bg-muted/50 p-6 text-center">
          <p className="text-muted-foreground">Appointment not found</p>
        </div>
      </div>
    );
  }

  const canMarkComplete =
    appointment.status === "scheduled" ||
    appointment.status === "confirmed" ||
    appointment.status === "in_progress";

  const canCancelOrReschedule =
    appointment.status === "scheduled" || appointment.status === "confirmed";

  return (
    <div className="space-y-6">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate("/staff/appointments")}
        className="mb-4"
      >
        <ArrowLeftIcon size={16} className="mr-2" />
        Back to Appointments
      </Button>

      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">Appointment Details</CardTitle>
              <p className="text-muted-foreground mt-2">ID: {appointment.id}</p>
            </div>
            <Badge variant={statusVariants[appointment.status]}>
              {statusLabels[appointment.status]}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground font-medium">Date</p>
              <p className="text-lg font-semibold mt-1">
                {formatDate(new Date(appointment.startTime))}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">Time</p>
              <p className="text-lg font-semibold mt-1">
                {formatTime(new Date(appointment.startTime))} -{" "}
                {formatTime(new Date(appointment.endTime))}
              </p>
            </div>
          </div>

          {/* Customer Info */}
          <div className="border-t border-border pt-4">
            <p className="text-sm text-muted-foreground font-medium mb-3">
              Customer
            </p>
            <div className="space-y-2">
              <div>
                <p className="text-sm text-muted-foreground">Customer ID</p>
                <p className="font-medium">{appointment.customerId}</p>
              </div>
            </div>
          </div>

          {/* Service Info */}
          <div className="border-t border-border pt-4">
            <p className="text-sm text-muted-foreground font-medium mb-3">
              Service
            </p>
            <div className="space-y-2">
              <div>
                <p className="text-sm text-muted-foreground">Service ID</p>
                <p className="font-medium">{appointment.serviceId}</p>
              </div>
            </div>
          </div>

          {/* Notes */}
          {appointment.notes && (
            <div className="border-t border-border pt-4">
              <p className="text-sm text-muted-foreground font-medium mb-2">
                Notes
              </p>
              <p className="text-sm text-foreground bg-muted/50 p-3 rounded">
                {appointment.notes}
              </p>
            </div>
          )}

          {/* Cancellation Reason */}
          {appointment.cancellation_reason && (
            <div className="border-t border-border pt-4">
              <p className="text-sm text-muted-foreground font-medium mb-2">
                Cancellation Reason
              </p>
              <p className="text-sm text-foreground bg-destructive/10 p-3 rounded">
                {appointment.cancellation_reason}
              </p>
            </div>
          )}

          {/* Created At */}
          <div className="border-t border-border pt-4">
            <p className="text-xs text-muted-foreground">
              Created on {formatDate(new Date(appointment.createdAt))}
            </p>
          </div>

          {/* Actions */}
          <div className="border-t border-border pt-4 flex flex-wrap gap-2">
            {canMarkComplete && (
              <>
                {!showConfirmDialog ? (
                  <Button
                    onClick={() => setShowConfirmDialog(true)}
                    disabled={completeAppointmentMutation.isPending}
                  >
                    {completeAppointmentMutation.isPending
                      ? "Marking as Complete..."
                      : "Mark as Completed"}
                  </Button>
                ) : (
                  <div className="flex gap-2 items-center">
                    <div className="text-sm text-muted-foreground">
                      Mark as completed?
                    </div>
                    <Button
                      size="sm"
                      onClick={handleCompleteAppointment}
                      disabled={completeAppointmentMutation.isPending}
                    >
                      {completeAppointmentMutation.isPending
                        ? "Confirming..."
                        : "Confirm"}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowConfirmDialog(false)}
                      disabled={completeAppointmentMutation.isPending}
                    >
                      Cancel
                    </Button>
                  </div>
                )}
              </>
            )}

            {canCancelOrReschedule && (
              <>
                <Button
                  variant="outline"
                  onClick={() => setShowRescheduleModal(true)}
                  disabled={
                    rescheduleAppointmentMutation.isPending ||
                    cancelAppointmentMutation.isPending
                  }
                >
                  Reschedule
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => setShowCancelModal(true)}
                  disabled={
                    cancelAppointmentMutation.isPending ||
                    rescheduleAppointmentMutation.isPending
                  }
                >
                  Cancel Appointment
                </Button>
              </>
            )}

            <Button
              variant="outline"
              onClick={() => navigate("/staff/appointments")}
            >
              Back
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Appointment Notes Section */}
      <AppointmentNotesSection
        appointment={appointment}
        onNotesUpdate={handleUpdateNotes}
        isLoading={updateNotesMutation.isPending}
        canEdit={
          appointment.status === "scheduled" ||
          appointment.status === "confirmed" ||
          appointment.status === "in_progress"
        }
      />

      {/* Modals */}
      <AppointmentCancellationModal
        open={showCancelModal}
        onOpenChange={setShowCancelModal}
        onConfirm={handleCancelAppointment}
        isLoading={cancelAppointmentMutation.isPending}
      />

      <AppointmentRescheduleModal
        open={showRescheduleModal}
        onOpenChange={setShowRescheduleModal}
        onConfirm={handleRescheduleAppointment}
        appointmentId={appointment.id}
        staffId={appointment.staffId}
        serviceId={appointment.serviceId}
        currentStartTime={appointment.startTime}
        isLoading={rescheduleAppointmentMutation.isPending}
      />
    </div>
  );
}
