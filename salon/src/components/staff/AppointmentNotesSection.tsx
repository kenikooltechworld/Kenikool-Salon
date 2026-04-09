import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircleIcon } from "@/components/icons";
import { NotesEditor } from "./NotesEditor";
import { formatDate } from "@/lib/utils/format";
import { useMyAppointments } from "@/hooks/useMyAppointments";
import type { Appointment } from "@/hooks/useAppointments";

interface AppointmentNotesSectionProps {
  appointment: Appointment;
  onNotesUpdate: (notes: string) => Promise<void>;
  isLoading?: boolean;
  canEdit?: boolean;
}

export default function AppointmentNotesSection({
  appointment,
  onNotesUpdate,
  isLoading = false,
  canEdit = true,
}: AppointmentNotesSectionProps) {
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [previousNotes, setPreviousNotes] = useState<string | null>(null);

  // Fetch previous appointment notes for follow-up context
  const { data: previousAppointments } = useMyAppointments({
    status: "completed",
  });

  useEffect(() => {
    if (previousAppointments && previousAppointments.length > 0) {
      // Find the most recent completed appointment with the same customer
      const previousAppointment = previousAppointments
        .filter(
          (apt) =>
            apt.customerId === appointment.customerId &&
            apt.id !== appointment.id &&
            new Date(apt.startTime) < new Date(appointment.startTime),
        )
        .sort(
          (a, b) =>
            new Date(b.startTime).getTime() - new Date(a.startTime).getTime(),
        )[0];

      if (previousAppointment && previousAppointment.notes) {
        setPreviousNotes(previousAppointment.notes);
      }
    }
  }, [
    previousAppointments,
    appointment.customerId,
    appointment.id,
    appointment.startTime,
  ]);

  const handleSaveNotes = async (notes: string) => {
    setError(null);
    try {
      await onNotesUpdate(notes);
      setRetryCount(0);
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to save notes";
      setError(errorMsg);
      setRetryCount((prev) => prev + 1);
      throw err;
    }
  };

  const handleRetry = async () => {
    if (appointment.notes) {
      try {
        await onNotesUpdate(appointment.notes);
        setError(null);
        setRetryCount(0);
      } catch (err) {
        const errorMsg =
          err instanceof Error ? err.message : "Failed to save notes";
        setError(errorMsg);
        setRetryCount((prev) => prev + 1);
      }
    }
  };

  // Determine if appointment can be edited (before completion)
  const canEditNotes =
    canEdit &&
    (appointment.status === "scheduled" ||
      appointment.status === "confirmed" ||
      appointment.status === "in_progress");

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Appointment Notes</CardTitle>
          {!canEditNotes && <Badge variant="secondary">Read-only</Badge>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Follow-up Notes from Previous Appointments */}
        {previousNotes && (
          <div className="space-y-2 bg-blue-50 dark:bg-blue-950 p-3 rounded border border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                Follow-up Notes from Previous Appointment
              </p>
            </div>
            <div className="bg-white dark:bg-slate-900 p-2 rounded text-sm text-foreground whitespace-pre-wrap border border-blue-100 dark:border-blue-800">
              {previousNotes}
            </div>
          </div>
        )}

        {/* Service Notes Section */}
        {appointment.notes && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-muted-foreground">
                Service Notes
              </p>
              <span className="text-xs text-muted-foreground">
                {formatDate(new Date(appointment.createdAt))}
              </span>
            </div>
            <div className="bg-muted/50 p-3 rounded text-sm text-foreground whitespace-pre-wrap border border-border">
              {appointment.notes}
            </div>
          </div>
        )}

        {/* Private Notes Editor */}
        {canEditNotes ? (
          <div className="border-t border-border pt-4">
            <NotesEditor
              initialNotes={appointment.notes || ""}
              onSave={handleSaveNotes}
              isLoading={isLoading}
              readOnly={false}
            />
          </div>
        ) : (
          <div className="border-t border-border pt-4">
            <NotesEditor
              initialNotes={appointment.notes || ""}
              onSave={handleSaveNotes}
              isLoading={isLoading}
              readOnly={true}
            />
          </div>
        )}

        {/* Error State with Retry */}
        {error && (
          <Alert className="bg-destructive/10 border-destructive/30">
            <AlertCircleIcon className="h-4 w-4 text-destructive" />
            <AlertDescription className="text-destructive">
              <div className="flex items-center justify-between">
                <span>{error}</span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleRetry}
                  disabled={isLoading}
                  className="ml-2"
                >
                  {isLoading ? (
                    <>
                      <Spinner size="sm" className="mr-2" />
                      Retrying...
                    </>
                  ) : (
                    "Retry"
                  )}
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Retry Count Indicator */}
        {retryCount > 0 && (
          <p className="text-xs text-muted-foreground">
            Retry attempts: {retryCount}
          </p>
        )}

        {/* Appointment Status Info */}
        <div className="border-t border-border pt-4">
          <p className="text-xs text-muted-foreground">
            {canEditNotes
              ? "You can edit notes until the appointment is completed."
              : "Notes cannot be edited after appointment completion."}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
