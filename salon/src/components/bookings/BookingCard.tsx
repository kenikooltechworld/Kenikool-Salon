import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Booking } from "@/types";
import { BookingStatusBadge } from "./BookingStatusBadge";
import { formatDate, formatTime } from "@/lib/utils/format";
import { EyeIcon, CheckIcon, TrashIcon } from "@/components/icons";

interface BookingCardProps {
  booking: Booking;
  onView?: (id: string) => void;
  onConfirm?: (id: string) => void;
  onCancel?: (id: string) => void;
  onComplete?: (id: string) => void;
  onMarkNoShow?: (id: string) => void;
  isLoading?: boolean;
}

export function BookingCard({
  booking,
  onView,
  onConfirm,
  onCancel,
  onComplete,
  onMarkNoShow,
  isLoading = false,
}: BookingCardProps) {
  return (
    <Card className="p-3 sm:p-4 space-y-3 hover:shadow-md transition">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm sm:text-base text-foreground truncate">
            Booking #{booking.id.slice(0, 8)}
          </h3>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {formatDate(new Date(booking.startTime))}
          </p>
        </div>
        <BookingStatusBadge status={booking.status} size="sm" />
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs sm:text-sm">
        <div>
          <p className="text-muted-foreground">Start Time</p>
          <p className="font-medium text-foreground">
            {formatTime(new Date(booking.startTime))}
          </p>
        </div>
        <div>
          <p className="text-muted-foreground">End Time</p>
          <p className="font-medium text-foreground">
            {formatTime(new Date(booking.endTime))}
          </p>
        </div>
      </div>

      {booking.notes && (
        <div className="text-xs sm:text-sm">
          <p className="text-muted-foreground">Notes</p>
          <p className="text-foreground line-clamp-2">{booking.notes}</p>
        </div>
      )}

      <div className="flex gap-2 pt-2 border-t border-border overflow-x-auto">
        {onView && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onView(booking.id)}
            disabled={isLoading}
            className="gap-1 shrink-0"
          >
            <EyeIcon size={14} />
            <span>View</span>
          </Button>
        )}
        {booking.status === "scheduled" && onConfirm && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => onConfirm(booking.id)}
            disabled={isLoading}
            className="gap-1 shrink-0"
          >
            <CheckIcon size={14} />
            <span>Confirm</span>
          </Button>
        )}
        {booking.status === "confirmed" && onComplete && (
          <Button
            variant="success"
            size="sm"
            onClick={() => onComplete(booking.id)}
            disabled={isLoading}
            className="gap-1 shrink-0"
          >
            <CheckIcon size={14} />
            <span>Complete</span>
          </Button>
        )}
        {(booking.status === "scheduled" || booking.status === "confirmed") &&
          onCancel && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => onCancel(booking.id)}
              disabled={isLoading}
              className="gap-1 shrink-0"
            >
              <TrashIcon size={14} />
              <span>Cancel</span>
            </Button>
          )}
        {booking.status === "confirmed" && onMarkNoShow && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onMarkNoShow(booking.id)}
            disabled={isLoading}
            className="gap-1 shrink-0"
          >
            <TrashIcon size={14} />
            <span>No-Show</span>
          </Button>
        )}
      </div>
    </Card>
  );
}
