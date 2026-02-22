import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronLeftIcon, ChevronRightIcon } from "@/components/icons";
import type { Booking } from "@/lib/api/types";

interface BookingCalendarViewProps {
  bookings: Booking[];
  onBookingClick?: (booking: Booking) => void;
}

export function BookingCalendarView({
  bookings,
  onBookingClick,
}: BookingCalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<"month" | "week" | "day">("month");
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatDate = (date: Date) => date.toISOString().split("T")[0];

  const getBookingsForDate = (date: Date) => {
    const dateStr = formatDate(date);
    return bookings.filter(
      (b) => formatDate(new Date(b.booking_date)).split("T")[0] === dateStr,
    );
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "confirmed":
        return "default";
      case "pending":
        return "accent";
      case "completed":
        return "secondary";
      case "cancelled":
        return "destructive";
      default:
        return "outline";
    }
  };

  const previousMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() - 1),
    );
  };

  const nextMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() + 1),
    );
  };

  const today = new Date();
  const daysInMonth = getDaysInMonth(currentDate);
  const firstDay = getFirstDayOfMonth(currentDate);
  const days = [];

  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }

  for (let i = 1; i <= daysInMonth; i++) {
    days.push(new Date(currentDate.getFullYear(), currentDate.getMonth(), i));
  }

  const monthName = currentDate.toLocaleString("default", {
    month: "long",
    year: "numeric",
  });

  const getWeekDays = () => {
    const start = new Date(currentDate);
    start.setDate(start.getDate() - start.getDay());
    const weekDays = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(start);
      day.setDate(day.getDate() + i);
      weekDays.push(day);
    }
    return weekDays;
  };

  const getDayBookings = () => {
    const date = selectedDate || currentDate;
    return getBookingsForDate(date).sort(
      (a, b) =>
        new Date(a.booking_date).getTime() - new Date(b.booking_date).getTime(),
    );
  };

  const handleMiniCalendarDateClick = (day: Date) => {
    setSelectedDate(day);
    setView("day");
  };

  return (
    <div className="w-full flex flex-col gap-3 sm:gap-4 md:gap-6">
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-slate-900 truncate">
            {monthName}
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            {bookings.length} total bookings
          </p>
        </div>

        {/* View Switcher - Responsive */}
        <div className="flex gap-1 bg-white rounded-lg p-1 shadow-sm border border-slate-200 w-fit">
          <Button
            variant={view === "month" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setView("month")}
            className="text-xs sm:text-sm font-medium px-2 sm:px-3"
            title="Month view"
          >
            <span className="hidden sm:inline">Month</span>
            <span className="sm:hidden">M</span>
          </Button>
          <Button
            variant={view === "week" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setView("week")}
            className="text-xs sm:text-sm font-medium px-2 sm:px-3"
            title="Week view"
          >
            <span className="hidden sm:inline">Week</span>
            <span className="sm:hidden">W</span>
          </Button>
          <Button
            variant={view === "day" ? "primary" : "ghost"}
            size="sm"
            onClick={() => setView("day")}
            className="text-xs sm:text-sm font-medium px-2 sm:px-3"
            title="Day view"
          >
            <span className="hidden sm:inline">Day</span>
            <span className="sm:hidden">D</span>
          </Button>
        </div>
      </div>

      {/* Main content area - Responsive layout */}
      <div className="flex flex-col lg:flex-row gap-3 sm:gap-4 md:gap-6">
        {/* Left Sidebar - Visible on all screens, responsive layout */}
        <div className="lg:w-64 flex flex-col space-y-4 flex-shrink-0">
          {/* Mini Calendar */}
          <Card className="p-3 sm:p-4 shadow-md border-0">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-xs sm:text-sm text-slate-900 truncate">
                  {monthName}
                </h3>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={previousMonth}
                    className="h-6 w-6 p-0"
                    title="Previous month"
                  >
                    <ChevronLeftIcon size={14} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={nextMonth}
                    className="h-6 w-6 p-0"
                    title="Next month"
                  >
                    <ChevronRightIcon size={14} />
                  </Button>
                </div>
              </div>

              {/* Mini day headers */}
              <div className="grid grid-cols-7 gap-1">
                {["S", "M", "T", "W", "T", "F", "S"].map((day) => (
                  <div
                    key={day}
                    className="text-center text-xs font-semibold text-slate-600"
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Mini calendar grid */}
              <div className="grid grid-cols-7 gap-1">
                {days.map((day, idx) => {
                  const isToday =
                    day && day.toDateString() === today.toDateString();
                  const isSelected =
                    day &&
                    selectedDate &&
                    day.toDateString() === selectedDate.toDateString();

                  return (
                    <button
                      key={idx}
                      onClick={() => day && handleMiniCalendarDateClick(day)}
                      className={`h-7 sm:h-8 text-xs font-medium rounded transition-all ${
                        !day
                          ? "bg-transparent"
                          : isToday
                            ? "bg-blue-500 text-white font-bold hover:bg-blue-600"
                            : isSelected
                              ? "bg-blue-100 text-blue-700 border border-blue-300 hover:bg-blue-200"
                              : "text-slate-700 hover:bg-slate-200"
                      }`}
                      title={day ? day.toDateString() : ""}
                    >
                      {day ? day.getDate() : ""}
                    </button>
                  );
                })}
              </div>
            </div>
          </Card>

          {/* Stats */}
          <Card className="p-3 sm:p-4 shadow-md border-0 space-y-3">
            <div>
              <p className="text-xs text-slate-600 font-medium">
                Total Bookings
              </p>
              <p className="text-xl sm:text-2xl font-bold text-slate-900">
                {bookings.length}
              </p>
            </div>
            <div className="pt-3 border-t border-slate-200 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-600">Confirmed</span>
                <span className="font-bold text-blue-600">
                  {bookings.filter((b) => b.status === "confirmed").length}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-600">Pending</span>
                <span className="font-bold text-amber-600">
                  {bookings.filter((b) => b.status === "pending").length}
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-600">Completed</span>
                <span className="font-bold text-green-600">
                  {bookings.filter((b) => b.status === "completed").length}
                </span>
              </div>
            </div>
          </Card>
        </div>

        {/* Main Calendar Area - Full width on mobile */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Month View */}
          {view === "month" && (
            <Card className="flex-1 p-2 sm:p-3 md:p-4 shadow-lg border-0 overflow-x-auto bg-white">
              {/* Day headers */}
              <div className="grid grid-cols-7 gap-0.5 sm:gap-1 mb-2 sm:mb-3">
                {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(
                  (day) => (
                    <div
                      key={day}
                      className="text-center font-semibold text-xs sm:text-sm text-slate-600 py-1 sm:py-2"
                    >
                      <span className="hidden sm:inline">{day}</span>
                      <span className="sm:hidden">{day.slice(0, 1)}</span>
                    </div>
                  ),
                )}
              </div>

              {/* Calendar grid - Responsive sizing */}
              <div className="grid grid-cols-7 gap-0.5 sm:gap-1">
                {days.map((day, idx) => {
                  const dayBookings = day ? getBookingsForDate(day) : [];
                  const isToday =
                    day && day.toDateString() === today.toDateString();
                  const isSelected =
                    day &&
                    selectedDate &&
                    day.toDateString() === selectedDate.toDateString();

                  return (
                    <div
                      key={idx}
                      onClick={() => day && setSelectedDate(day)}
                      className={`rounded border transition-all cursor-pointer flex flex-col p-1 sm:p-2 min-h-16 sm:min-h-20 md:min-h-24 ${
                        !day
                          ? "bg-slate-50 border-transparent"
                          : isToday
                            ? "border-2 border-blue-500 bg-blue-50 shadow-md"
                            : isSelected
                              ? "border-2 border-slate-400 bg-slate-100"
                              : "border border-slate-200 bg-white hover:border-slate-300 hover:shadow-md"
                      }`}
                      title={day ? day.toDateString() : ""}
                    >
                      {day && (
                        <>
                          <div
                            className={`text-xs sm:text-sm font-bold mb-0.5 sm:mb-1 ${
                              isToday ? "text-blue-600" : "text-slate-900"
                            }`}
                          >
                            {day.getDate()}
                          </div>

                          {dayBookings.length > 0 && (
                            <div className="flex-1 space-y-0.5 overflow-hidden">
                              {dayBookings.slice(0, 1).map((booking) => (
                                <div
                                  key={booking.id}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    onBookingClick?.(booking);
                                  }}
                                  className="text-xs truncate"
                                >
                                  <Badge
                                    variant={getStatusBadgeVariant(
                                      booking.status,
                                    )}
                                    className="truncate text-xs w-full justify-start"
                                    title={`${booking.client_name} - ${booking.service_name}`}
                                  >
                                    {booking.client_name}
                                  </Badge>
                                </div>
                              ))}
                              {dayBookings.length > 1 && (
                                <div className="text-xs text-slate-600 font-medium px-0.5">
                                  +{dayBookings.length - 1}
                                </div>
                              )}
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Week View */}
          {view === "week" && (
            <Card className="flex-1 p-2 sm:p-3 md:p-4 shadow-lg border-0 overflow-x-auto bg-white">
              <div className="grid grid-cols-7 gap-1 sm:gap-2 w-full min-w-max">
                {getWeekDays().map((day) => {
                  const dayBookings = getBookingsForDate(day);
                  const isToday = day.toDateString() === today.toDateString();

                  return (
                    <div
                      key={formatDate(day)}
                      className={`rounded border p-2 sm:p-3 min-h-48 sm:min-h-64 md:min-h-80 flex flex-col flex-1 min-w-32 sm:min-w-40 ${
                        isToday
                          ? "border-blue-500 bg-blue-50"
                          : "border-slate-200 bg-white"
                      }`}
                      title={day.toDateString()}
                    >
                      <div className="font-semibold text-xs sm:text-sm text-slate-900 mb-2 sm:mb-3 truncate">
                        {day.toLocaleDateString("default", {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                        })}
                      </div>

                      <div className="flex-1 space-y-1 sm:space-y-2 overflow-y-auto">
                        {dayBookings.length > 0 ? (
                          dayBookings.map((booking) => (
                            <div
                              key={booking.id}
                              onClick={() => onBookingClick?.(booking)}
                              className="p-1.5 sm:p-2 rounded border-l-4 cursor-pointer hover:shadow-md transition-all bg-card text-xs sm:text-sm"
                              title={`${booking.client_name} - ${booking.service_name}`}
                            >
                              <Badge
                                variant={getStatusBadgeVariant(booking.status)}
                                className="mb-1 text-xs"
                              >
                                {booking.status}
                              </Badge>
                              <p className="text-xs font-semibold truncate">
                                {booking.client_name}
                              </p>
                              <p className="text-xs opacity-75 truncate">
                                {booking.service_name}
                              </p>
                            </div>
                          ))
                        ) : (
                          <div className="text-xs text-slate-400 text-center py-4">
                            No bookings
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Day View */}
          {view === "day" && (
            <Card className="flex-1 p-2 sm:p-3 md:p-4 shadow-lg border-0 overflow-y-auto bg-white">
              <div className="w-full max-w-4xl">
                <div className="mb-3 sm:mb-4 md:mb-6">
                  <h2 className="text-base sm:text-lg md:text-2xl font-bold text-slate-900 truncate">
                    {(selectedDate || currentDate).toLocaleDateString(
                      "default",
                      {
                        weekday: "long",
                        month: "long",
                        day: "numeric",
                      },
                    )}
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-600 mt-1">
                    {getDayBookings().length} booking
                    {getDayBookings().length !== 1 ? "s" : ""}
                  </p>
                </div>

                <div className="space-y-2 sm:space-y-3">
                  {getDayBookings().length > 0 ? (
                    getDayBookings().map((booking) => (
                      <div
                        key={booking.id}
                        onClick={() => onBookingClick?.(booking)}
                        className="p-2 sm:p-3 md:p-4 rounded-lg border-l-4 cursor-pointer hover:shadow-lg transition-all bg-card"
                        title={`${booking.client_name} - ${booking.service_name}`}
                      >
                        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-3 mb-2">
                          <div className="min-w-0 flex-1">
                            <p className="font-semibold text-xs sm:text-sm truncate">
                              {booking.client_name}
                            </p>
                            <p className="text-xs sm:text-sm opacity-75 truncate">
                              {booking.service_name}
                            </p>
                          </div>
                          <Badge
                            variant={getStatusBadgeVariant(booking.status)}
                            className="text-xs flex-shrink-0 w-fit"
                          >
                            {booking.status}
                          </Badge>
                        </div>

                        <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 text-xs sm:text-sm mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-border flex-wrap">
                          <div className="font-medium">
                            {new Date(booking.booking_date).toLocaleTimeString(
                              [],
                              {
                                hour: "2-digit",
                                minute: "2-digit",
                              },
                            )}
                          </div>
                          <div className="opacity-75 truncate">
                            {booking.stylist_name}
                          </div>
                          <div className="font-semibold sm:ml-auto">
                            ₦{booking.service_price?.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 sm:py-12 text-slate-400">
                      <p className="text-sm sm:text-base">
                        No bookings for this day
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
