import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { CalendarIcon } from "@/components/icons";
import { format, parseISO } from "date-fns";

interface UpcomingEvent {
  date: string;
  appointment_count: number;
  is_fully_booked: boolean;
}

interface UpcomingEventsWidgetProps {
  events: UpcomingEvent[];
  loading?: boolean;
  onDateClick?: (date: string) => void;
}

export function UpcomingEventsWidget({
  events,
  loading = false,
  onDateClick,
}: UpcomingEventsWidgetProps) {
  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-left-4 duration-500"
      role="region"
      aria-label="Upcoming Events Widget"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Upcoming Events
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => (window.location.href = "/dashboard/bookings")}
          className="transition-all duration-200 ease-out hover:scale-105"
          aria-label="View full calendar"
        >
          View Calendar
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : events.length === 0 ? (
        <div className="text-center py-8 animate-in fade-in-0 zoom-in-95 duration-300">
          <CalendarIcon
            size={48}
            className="mx-auto text-muted-foreground mb-2"
          />
          <p className="text-muted-foreground">No upcoming events</p>
        </div>
      ) : (
        <div className="space-y-3" role="list" aria-label="Upcoming events">
          {events.map((event, index) => {
            const eventDate = parseISO(event.date);

            return (
              <div
                key={event.date}
                role="listitem"
                tabIndex={0}
                className="flex items-center gap-3 p-3 bg-[var(--muted)]/50 rounded-lg hover:bg-[var(--muted)] transition-all duration-300 ease-out hover:scale-[1.02] hover:shadow-sm transform will-change-transform cursor-pointer animate-in fade-in-0 slide-in-from-right-2 focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                style={{ animationDelay: `${index * 50}ms` }}
                onClick={() => onDateClick?.(event.date)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onDateClick?.(event.date);
                  }
                }}
                aria-label={`${format(eventDate, "EEEE, MMM dd")}, ${
                  event.appointment_count
                } appointment${event.appointment_count !== 1 ? "s" : ""}${
                  event.is_fully_booked ? ", fully booked" : ""
                }`}
              >
                <div
                  className="p-2 bg-[var(--primary)]/10 rounded-lg transition-all duration-300 ease-out hover:bg-[var(--primary)]/20 hover:scale-110 transform will-change-transform"
                  aria-hidden="true"
                >
                  <CalendarIcon size={20} className="text-[var(--primary)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-foreground">
                    {format(eventDate, "EEEE, MMM dd")}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {event.appointment_count} appointment
                    {event.appointment_count !== 1 ? "s" : ""}
                  </p>
                </div>
                {event.is_fully_booked && (
                  <Badge
                    variant="warning"
                    aria-label="This day is fully booked"
                  >
                    Fully Booked
                  </Badge>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
