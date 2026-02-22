import type { BookingStatus } from "@/types";

interface BookingStatusBadgeProps {
  status: BookingStatus;
  size?: "sm" | "md" | "lg";
}

const statusConfig: Record<
  BookingStatus,
  { label: string; variant: string; bgColor: string }
> = {
  scheduled: {
    label: "Scheduled",
    variant: "secondary",
    bgColor: "bg-primary/10 text-primary",
  },
  confirmed: {
    label: "Confirmed",
    variant: "default",
    bgColor: "bg-success/10 text-success",
  },
  completed: {
    label: "Completed",
    variant: "outline",
    bgColor: "bg-muted text-foreground",
  },
  cancelled: {
    label: "Cancelled",
    variant: "destructive",
    bgColor: "bg-destructive/10 text-destructive",
  },
  no_show: {
    label: "No Show",
    variant: "destructive",
    bgColor: "bg-warning/10 text-warning",
  },
};

export function BookingStatusBadge({
  status,
  size = "md",
}: BookingStatusBadgeProps) {
  const config = statusConfig[status];

  const sizeClasses = {
    sm: "text-xs px-2 py-1",
    md: "text-sm px-3 py-1.5",
    lg: "text-base px-4 py-2",
  };

  return (
    <div
      className={`inline-flex rounded-full ${config.bgColor} ${sizeClasses[size]}`}
    >
      {config.label}
    </div>
  );
}
