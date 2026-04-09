import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StaffAppointmentCard } from "./StaffAppointmentCard";
import type { StaffAppointment } from "@/hooks/useMyAppointments";

interface StaffAppointmentsListProps {
  appointments: StaffAppointment[];
  isLoading?: boolean;
  error?: string;
  onViewDetails?: (appointment: StaffAppointment) => void;
  onRetry?: () => void;
}

export function StaffAppointmentsList({
  appointments,
  isLoading = false,
  error,
  onViewDetails,
  onRetry,
}: StaffAppointmentsListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
        <p className="text-sm text-destructive font-medium">
          Failed to load appointments
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          {error || "Network error. Please try again."}
        </p>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="mt-3"
          >
            Retry
          </Button>
        )}
      </div>
    );
  }

  if (appointments.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-muted/50 p-8 text-center">
        <p className="text-muted-foreground">No appointments found</p>
        <p className="text-sm text-muted-foreground mt-1">
          Your appointments will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {appointments.map((appointment) => (
        <StaffAppointmentCard
          key={appointment.id}
          appointment={appointment}
          onViewDetails={onViewDetails}
        />
      ))}
    </div>
  );
}
