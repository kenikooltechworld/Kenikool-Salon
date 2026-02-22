import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  useGroupBookings,
  useUpdateGroupBookingStatus,
} from "@/lib/api/hooks/useGroupBookings";
import type { GroupBooking } from "@/lib/api/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import {
  UsersIcon,
  CalendarIcon,
  PhoneIcon,
  SearchIcon,
  FilterIcon,
} from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { format } from "date-fns";

export function GroupBookingList() {
  const navigate = useNavigate();
  const { data: groupBookings = [], isLoading } = useGroupBookings();
  const updateStatus = useUpdateGroupBookingStatus();
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filtered and paginated bookings
  const filteredBookings = useMemo(() => {
    let filtered = [...groupBookings];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (booking) =>
          booking.organizer_name.toLowerCase().includes(query) ||
          booking.organizer_phone.includes(query) ||
          booking.organizer_email?.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter((booking) => booking.status === statusFilter);
    }

    // Date range filter
    if (dateFrom) {
      filtered = filtered.filter(
        (booking) => new Date(booking.booking_date) >= new Date(dateFrom)
      );
    }
    if (dateTo) {
      filtered = filtered.filter(
        (booking) =>
          new Date(booking.booking_date) <= new Date(dateTo + "T23:59:59")
      );
    }

    // Sort by booking date (newest first)
    filtered.sort(
      (a, b) =>
        new Date(b.booking_date).getTime() - new Date(a.booking_date).getTime()
    );

    return filtered;
  }, [groupBookings, searchQuery, statusFilter, dateFrom, dateTo]);

  // Pagination
  const totalPages = Math.ceil(filteredBookings.length / itemsPerPage);
  const paginatedBookings = filteredBookings.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleStatusUpdate = async (bookingId: string, status: string) => {
    try {
      setUpdatingId(bookingId);
      await updateStatus.mutateAsync({ bookingId, status });
      showToast(`Group booking ${status}`, "success");
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      showToast(
        err.response?.data?.message || "Failed to update status",
        "error"
      );
    } finally {
      setUpdatingId(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "success";
      case "pending":
        return "warning";
      case "cancelled":
        return "error";
      case "completed":
        return "info";
      default:
        return "secondary";
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setStatusFilter("all");
    setDateFrom("");
    setDateTo("");
    setCurrentPage(1);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name, phone, or email..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <Select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </Select>
            </div>

            {/* Date From */}
            <div>
              <Input
                type="date"
                placeholder="From date"
                value={dateFrom}
                onChange={(e) => {
                  setDateFrom(e.target.value);
                  setCurrentPage(1);
                }}
              />
            </div>

            {/* Date To */}
            <div>
              <Input
                type="date"
                placeholder="To date"
                value={dateTo}
                onChange={(e) => {
                  setDateTo(e.target.value);
                  setCurrentPage(1);
                }}
              />
            </div>
          </div>

          {/* Clear Filters */}
          {(searchQuery || statusFilter !== "all" || dateFrom || dateTo) && (
            <div className="mt-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing {filteredBookings.length} of {groupBookings.length}{" "}
                bookings
              </p>
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <FilterIcon className="w-4 h-4 mr-2" />
                Clear Filters
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Bookings List */}
      {paginatedBookings.length === 0 ? (
        <Card className="text-center">
          <CardContent className="py-12">
            <UsersIcon className="w-12 h-12 mx-auto mb-4 text-[var(--muted-foreground)]" />
            <h3 className="text-lg font-semibold mb-2 text-[var(--foreground)]">
              {groupBookings.length === 0
                ? "No Group Bookings"
                : "No bookings match your filters"}
            </h3>
            <p className="text-[var(--muted-foreground)]">
              {groupBookings.length === 0
                ? "Group bookings will appear here once created."
                : "Try adjusting your search or filter criteria."}
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="space-y-4">
            {paginatedBookings.map((booking: GroupBooking) => (
              <Card
                key={booking._id}
                variant="elevated"
                hover
                className="cursor-pointer transition-all"
                onClick={() =>
                  navigate(`/dashboard/group-bookings/${booking._id}`)
                }
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-[var(--foreground)]">
                        {booking.organizer_name}
                      </h3>
                      <Badge variant={getStatusColor(booking.status)}>
                        {booking.status}
                      </Badge>
                    </div>

                    <div
                      className="flex gap-2"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {booking.status === "pending" && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              handleStatusUpdate(booking._id, "confirmed")
                            }
                            disabled={updatingId === booking._id}
                          >
                            {updatingId === booking._id
                              ? "Updating..."
                              : "Confirm"}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              handleStatusUpdate(booking._id, "cancelled")
                            }
                            disabled={updatingId === booking._id}
                          >
                            Cancel
                          </Button>
                        </>
                      )}

                      {booking.status === "confirmed" && (
                        <Button
                          size="sm"
                          onClick={() =>
                            handleStatusUpdate(booking._id, "completed")
                          }
                          disabled={updatingId === booking._id}
                        >
                          {updatingId === booking._id
                            ? "Updating..."
                            : "Complete"}
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-2">
                  <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
                    <PhoneIcon className="w-4 h-4" />
                    <span className="text-sm">{booking.organizer_phone}</span>
                  </div>

                  <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
                    <CalendarIcon className="w-4 h-4" />
                    <span className="text-sm">
                      {format(new Date(booking.booking_date), "PPP")} at{" "}
                      {format(new Date(booking.booking_date), "p")}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-[var(--muted-foreground)]">
                    <UsersIcon className="w-4 h-4" />
                    <span className="text-sm">
                      {booking.total_members} members
                    </span>
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-[var(--border)]">
                    <div>
                      <p className="text-xs text-[var(--muted-foreground)]">
                        Total Price
                      </p>
                      <p className="text-lg font-bold text-[var(--primary)]">
                        ₦{booking.total_price.toLocaleString()}
                      </p>
                    </div>
                    <Badge
                      variant={
                        booking.payment_status === "paid"
                          ? "success"
                          : "warning"
                      }
                    >
                      {booking.payment_status}
                    </Badge>
                  </div>
                </CardContent>

                <CardFooter className="border-t border-[var(--border)] pt-3">
                  <p className="text-xs text-[var(--muted-foreground)]">
                    Created {format(new Date(booking.created_at), "PPP")}
                  </p>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Page {currentPage} of {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setCurrentPage((p) => Math.min(totalPages, p + 1))
                  }
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
