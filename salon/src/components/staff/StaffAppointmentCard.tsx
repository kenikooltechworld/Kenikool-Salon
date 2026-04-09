import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatDate, formatTime } from "@/lib/utils/format";
import type { StaffAppointment } from "@/hooks/useMyAppointments";
import type { BadgeProps } from "@/components/ui/badge";

interface StaffAppointmentCardProps {
  appointment: StaffAppointment;
  onViewDetails?: (appointment: StaffAppointment) => void;
}

const statusVariants: Record<
  StaffAppointment["status"],
  NonNullable<BadgeProps["variant"]>
> = {
  scheduled: "default",
  confirmed: "secondary",
  in_progress: "accent",
  completed: "outline",
  cancelled: "destructive",
};

const statusLabels: Record<StaffAppointment["status"], string> = {
  scheduled: "Scheduled",
  confirmed: "Confirmed",
  in_progress: "In Progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

export function StaffAppointmentCard({
  appointment,
  onViewDetails,
}: StaffAppointmentCardProps) {
  return (
    <Card hover>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base">
              {appointment.customerName}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {appointment.serviceName}
            </p>
          </div>
          <Badge variant={statusVariants[appointment.status]}>
            {statusLabels[appointment.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p className="text-muted-foreground">Date</p>
            <p className="font-medium">
              {formatDate(new Date(appointment.startTime))}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Time</p>
            <p className="font-medium">
              {formatTime(new Date(appointment.startTime))}
            </p>
          </div>
        </div>

        <div className="pt-2 border-t border-border">
          <p className="text-sm text-muted-foreground mb-2">Contact</p>
          <div className="space-y-1 text-sm">
            {appointment.customerPhone && (
              <p>
                <span className="text-muted-foreground">Phone: </span>
                <a
                  href={`tel:${appointment.customerPhone}`}
                  className="text-primary hover:underline"
                >
                  {appointment.customerPhone}
                </a>
              </p>
            )}
            {appointment.customerEmail && (
              <p>
                <span className="text-muted-foreground">Email: </span>
                <a
                  href={`mailto:${appointment.customerEmail}`}
                  className="text-primary hover:underline"
                >
                  {appointment.customerEmail}
                </a>
              </p>
            )}
          </div>
        </div>

        {appointment.notes && (
          <div className="pt-2 border-t border-border">
            <p className="text-sm text-muted-foreground mb-1">Notes</p>
            <p className="text-sm text-foreground">{appointment.notes}</p>
          </div>
        )}

        <div className="pt-2 border-t border-border flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewDetails?.(appointment)}
            className="flex-1"
          >
            View Details
          </Button>
          <Button variant="ghost" size="sm" className="px-2">
            ${appointment.price.toFixed(2)}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
