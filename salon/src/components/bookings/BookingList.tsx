import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import type { Booking, BookingFilters, BookingStatus } from "@/types";
import { BookingStatusBadge } from "./BookingStatusBadge";
import { formatDate, formatTime } from "@/lib/utils/format";
import { EyeIcon, CheckIcon, TrashIcon, SearchIcon } from "@/components/icons";

interface BookingListProps {
  bookings: Booking[];
  isLoading: boolean;
  onViewBooking: (id: string) => void;
  onConfirmBooking: (id: string) => void;
  onCancelBooking: (id: string) => void;
  filters?: BookingFilters;
  onFiltersChange?: (filters: BookingFilters) => void;
  isConfirming?: boolean;
  isCancelling?: boolean;
}

const statusOptions: BookingStatus[] = [
  "scheduled",
  "confirmed",
  "completed",
  "cancelled",
  "no_show",
];

export function BookingList({
  bookings,
  isLoading,
  onViewBooking,
  onConfirmBooking,
  onCancelBooking,
  isConfirming = false,
  isCancelling = false,
}: BookingListProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<BookingStatus | "all">(
    "all",
  );

  const filteredBookings = bookings.filter((booking) => {
    if (selectedStatus !== "all" && booking.status !== selectedStatus)
      return false;
    if (searchTerm && !booking.id.includes(searchTerm)) return false;
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        <div className="flex-1 relative">
          <SearchIcon
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Search bookings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 h-10"
          />
        </div>
        <select
          value={selectedStatus}
          onChange={(e) =>
            setSelectedStatus(e.target.value as BookingStatus | "all")
          }
          className="px-3 sm:px-4 py-2 h-10 border border-border rounded-lg bg-background text-foreground text-sm"
        >
          <option value="all">All Status</option>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Mobile: Card View, Desktop: Table View */}
      <div className="hidden md:block border border-border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted border-b border-border">
            <tr>
              <th className="px-3 sm:px-4 py-3 text-left text-xs sm:text-sm font-semibold text-foreground">
                ID
              </th>
              <th className="px-3 sm:px-4 py-3 text-left text-xs sm:text-sm font-semibold text-foreground">
                Date
              </th>
              <th className="px-3 sm:px-4 py-3 text-left text-xs sm:text-sm font-semibold text-foreground">
                Time
              </th>
              <th className="px-3 sm:px-4 py-3 text-left text-xs sm:text-sm font-semibold text-foreground">
                Status
              </th>
              <th className="px-3 sm:px-4 py-3 text-left text-xs sm:text-sm font-semibold text-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <>
                {[...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-border">
                    <td className="px-3 sm:px-4 py-3">
                      <Skeleton className="h-4 w-16" />
                    </td>
                    <td className="px-3 sm:px-4 py-3">
                      <Skeleton className="h-4 w-24" />
                    </td>
                    <td className="px-3 sm:px-4 py-3">
                      <Skeleton className="h-4 w-32" />
                    </td>
                    <td className="px-3 sm:px-4 py-3">
                      <Skeleton className="h-6 w-20 rounded-full" />
                    </td>
                    <td className="px-3 sm:px-4 py-3">
                      <div className="flex gap-2">
                        <Skeleton className="h-9 w-9 rounded" />
                        <Skeleton className="h-9 w-9 rounded" />
                      </div>
                    </td>
                  </tr>
                ))}
              </>
            ) : filteredBookings.length > 0 ? (
              filteredBookings.map((booking) => (
                <tr
                  key={booking.id}
                  className="border-b border-border hover:bg-muted/50 transition"
                >
                  <td className="px-3 sm:px-4 py-3 text-xs sm:text-sm text-foreground">
                    {booking.id.slice(0, 8)}
                  </td>
                  <td className="px-3 sm:px-4 py-3 text-xs sm:text-sm text-foreground">
                    {formatDate(new Date(booking.startTime))}
                  </td>
                  <td className="px-3 sm:px-4 py-3 text-xs sm:text-sm text-foreground">
                    {formatTime(new Date(booking.startTime))} -{" "}
                    {formatTime(new Date(booking.endTime))}
                  </td>
                  <td className="px-3 sm:px-4 py-3">
                    <BookingStatusBadge status={booking.status} size="sm" />
                  </td>
                  <td className="px-3 sm:px-4 py-3">
                    <div className="flex gap-1 sm:gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onViewBooking(booking.id)}
                        title="View booking"
                        className="h-9 w-9 p-0"
                      >
                        <EyeIcon size={16} />
                      </Button>
                      {booking.status === "scheduled" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onConfirmBooking(booking.id)}
                          title="Confirm booking"
                          disabled={isConfirming || isCancelling}
                          className="h-9 w-9 p-0"
                        >
                          {isConfirming ? "..." : <CheckIcon size={16} />}
                        </Button>
                      )}
                      {(booking.status === "scheduled" ||
                        booking.status === "confirmed") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onCancelBooking(booking.id)}
                          title="Cancel booking"
                          disabled={isConfirming || isCancelling}
                          className="h-9 w-9 p-0"
                        >
                          {isCancelling ? "..." : <TrashIcon size={16} />}
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-8 text-center text-muted-foreground"
                >
                  No bookings found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile: Card View */}
      <div className="md:hidden space-y-3">
        {isLoading ? (
          <>
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="border border-border rounded-lg p-3 space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1 space-y-2">
                    <Skeleton className="h-3 w-12" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                  <Skeleton className="h-6 w-20 rounded-full shrink-0" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-2">
                    <Skeleton className="h-3 w-12" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-3 w-12" />
                    <Skeleton className="h-4 w-28" />
                  </div>
                </div>
                <div className="flex gap-2 pt-2 border-t border-border">
                  <Skeleton className="flex-1 h-9" />
                  <Skeleton className="flex-1 h-9" />
                </div>
              </div>
            ))}
          </>
        ) : filteredBookings.length > 0 ? (
          filteredBookings.map((booking) => (
            <div
              key={booking.id}
              className="border border-border rounded-lg p-3 space-y-2 hover:bg-muted/30 transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-muted-foreground">ID</p>
                  <p className="font-semibold text-sm text-foreground">
                    {booking.id.slice(0, 8)}
                  </p>
                </div>
                <BookingStatusBadge status={booking.status} size="sm" />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <p className="text-muted-foreground">Date</p>
                  <p className="font-medium text-foreground">
                    {formatDate(new Date(booking.startTime))}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Time</p>
                  <p className="font-medium text-foreground">
                    {formatTime(new Date(booking.startTime))} -{" "}
                    {formatTime(new Date(booking.endTime))}
                  </p>
                </div>
              </div>
              <div className="flex gap-2 pt-2 border-t border-border">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewBooking(booking.id)}
                  className="flex-1 h-9 text-xs"
                >
                  <EyeIcon size={14} />
                  View
                </Button>
                {booking.status === "scheduled" && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => onConfirmBooking(booking.id)}
                    disabled={isConfirming || isCancelling}
                    className="flex-1 h-9 text-xs"
                  >
                    <CheckIcon size={14} />
                    {isConfirming ? "..." : "Confirm"}
                  </Button>
                )}
                {(booking.status === "scheduled" ||
                  booking.status === "confirmed") && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => onCancelBooking(booking.id)}
                    disabled={isConfirming || isCancelling}
                    className="flex-1 h-9 text-xs"
                  >
                    <TrashIcon size={14} />
                    {isCancelling ? "..." : "Cancel"}
                  </Button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No bookings found
          </div>
        )}
      </div>
    </div>
  );
}
