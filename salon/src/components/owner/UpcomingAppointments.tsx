import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CalendarIcon, ClockIcon } from "@/components/icons";
import type { UpcomingAppointment } from "@/hooks/owner";
import { formatTime, formatDate } from "@/lib/utils/date";

interface UpcomingAppointmentsProps {
  appointments: UpcomingAppointment[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  onAppointmentClick?: (appointment: UpcomingAppointment) => void;
}

const getStatusStyle = (status: string): React.CSSProperties => {
  const styles: Record<string, React.CSSProperties> = {
    confirmed: {
      backgroundColor: "var(--success-bg, #dcfce7)",
      color: "var(--success, #22c55e)",
    },
    pending: {
      backgroundColor: "var(--warning-bg, #fef3c7)",
      color: "var(--warning, #f59e0b)",
    },
    completed: {
      backgroundColor: "var(--info-bg, #dbeafe)",
      color: "var(--info, #3b82f6)",
    },
    cancelled: {
      backgroundColor: "var(--destructive-bg, #fee2e2)",
      color: "var(--destructive)",
    },
  };
  return styles[status] || {};
};

export function UpcomingAppointments({
  appointments,
  isLoading = false,
  error,
  onRetry,
  onAppointmentClick,
}: UpcomingAppointmentsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarIcon size={20} />
            Upcoming Appointments
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarIcon size={20} />
            Upcoming Appointments
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load appointments
          </p>
          <p className="text-sm text-muted-foreground">{error}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="w-full"
            >
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  if (appointments.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CalendarIcon size={20} />
            Upcoming Appointments
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No upcoming appointments
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CalendarIcon size={20} />
          Upcoming Appointments
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {appointments.map((appointment) => (
            <div
              key={appointment.id}
              className="flex items-start justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
              onClick={() => onAppointmentClick?.(appointment)}
            >
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-sm">
                    {appointment.customerName}
                  </p>
                  <Badge style={getStatusStyle(appointment.status)}>
                    {appointment.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {appointment.serviceName} • {appointment.staffName}
                </p>
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <CalendarIcon size={12} />
                    {formatDate(appointment.startTime)}
                  </span>
                  <span className="flex items-center gap-1">
                    <ClockIcon size={12} />
                    {formatTime(appointment.startTime)} -{" "}
                    {formatTime(appointment.endTime)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
