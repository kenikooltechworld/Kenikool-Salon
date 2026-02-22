"use client";

import { useQuery } from "@tanstack/react-query";
import { format, startOfWeek, addDays } from "date-fns";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

interface ScheduleCalendarViewProps {
  startDate?: Date;
  endDate?: Date;
  staffIds?: string[];
}

export function ScheduleCalendarView({
  startDate = new Date(),
  endDate = addDays(startDate, 6),
  staffIds,
}: ScheduleCalendarViewProps) {
  const { data: calendar, isLoading } = useQuery({
    queryKey: ["schedule-calendar", startDate, endDate, staffIds],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append("start_date", startDate.toISOString());
      params.append("end_date", endDate.toISOString());
      if (staffIds?.length) {
        staffIds.forEach((id) => params.append("staff_ids", id));
      }

      const res = await fetch(`/api/staff/schedule/calendar?${params}`);
      if (!res.ok) throw new Error("Failed to fetch calendar");
      return res.json();
    },
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Staff Schedule Calendar</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!calendar?.staff || calendar.staff.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Staff Schedule Calendar</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No schedule data available
          </p>
        </CardContent>
      </Card>
    );
  }

  // Generate week days
  const weekStart = startOfWeek(startDate);
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Staff Schedule Calendar</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="min-w-max">
            {/* Header with days */}
            <div className="grid grid-cols-8 gap-2 mb-4">
              <div className="font-semibold text-sm">Staff</div>
              {weekDays.map((day) => (
                <div key={day.toISOString()} className="text-center">
                  <div className="font-semibold text-sm">
                    {format(day, "EEE")}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {format(day, "MMM d")}
                  </div>
                </div>
              ))}
            </div>

            {/* Staff rows */}
            {calendar.staff.map((staffData: any) => (
              <div
                key={staffData.staff_id}
                className="grid grid-cols-8 gap-2 mb-4"
              >
                <div className="font-medium text-sm truncate">
                  {staffData.staff_name}
                </div>

                {weekDays.map((day) => {
                  const dayStr = format(day, "yyyy-MM-dd");
                  const availability = staffData.availability;
                  const timeOffs = availability.time_offs || [];
                  const bookings = availability.bookings || [];

                  const dayTimeOff = timeOffs.find(
                    (t: any) =>
                      new Date(t.start_date).toDateString() ===
                      day.toDateString(),
                  );
                  const dayBookings = bookings.filter(
                    (b: any) =>
                      new Date(b.date).toDateString() === day.toDateString(),
                  );

                  return (
                    <div
                      key={dayStr}
                      className="border rounded p-2 min-h-20 bg-gray-50 text-xs"
                    >
                      {dayTimeOff ? (
                        <Badge className="bg-red-100 text-red-800 mb-1">
                          {dayTimeOff.type}
                        </Badge>
                      ) : dayBookings.length > 0 ? (
                        <div className="space-y-1">
                          <Badge className="bg-blue-100 text-blue-800">
                            {dayBookings.length} booking(s)
                          </Badge>
                          {dayBookings
                            .slice(0, 2)
                            .map((booking: any, idx: number) => (
                              <div
                                key={idx}
                                className="text-xs text-muted-foreground"
                              >
                                {booking.duration_minutes}min
                              </div>
                            ))}
                        </div>
                      ) : (
                        <Badge className="bg-green-100 text-green-800">
                          Available
                        </Badge>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
