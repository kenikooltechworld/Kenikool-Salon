import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Button,
  Badge,
  Spinner,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui";
import {
  useCustomerBookingHistory,
  useRebookAppointment,
} from "@/hooks/useCustomerPortal";
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  DollarSignIcon,
} from "@/components/icons";
import { format } from "date-fns";

export default function BookingHistory() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const { data: bookings, isLoading } = useCustomerBookingHistory(statusFilter);
  const rebook = useRebookAppointment();

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "confirmed":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-blue-100 text-blue-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getPaymentStatusColor = (status?: string) => {
    if (!status) return "bg-gray-100 text-gray-800";

    switch (status.toLowerCase()) {
      case "paid":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleRebook = async (bookingId: string) => {
    try {
      const result = await rebook.mutateAsync(bookingId);
      // Navigate to booking page with pre-filled data
      navigate("/public/booking", {
        state: { rebookData: result.booking_data },
      });
    } catch (error) {
      console.error("Rebook failed:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filter */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">Filter by status:</label>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All bookings" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All bookings</SelectItem>
            <SelectItem value="confirmed">Confirmed</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Bookings List */}
      {!bookings || bookings.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-gray-500 mb-4">No bookings found</p>
          <Button onClick={() => navigate("/public/booking")}>
            Book Your First Appointment
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <Card key={booking.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold mb-1">
                    {booking.service_name}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <UserIcon size={16} />
                    <span>{booking.staff_name}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge className={getStatusColor(booking.status)}>
                    {booking.status}
                  </Badge>
                  {booking.payment_status && (
                    <Badge
                      className={getPaymentStatusColor(booking.payment_status)}
                    >
                      {booking.payment_status}
                    </Badge>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <CalendarIcon size={16} className="text-gray-400" />
                  <span>
                    {format(new Date(booking.booking_date), "MMMM d, yyyy")}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <ClockIcon size={16} className="text-gray-400" />
                  <span>{booking.booking_time}</span>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <DollarSignIcon size={16} className="text-gray-400" />
                  <span>${booking.total_price.toFixed(2)}</span>
                </div>

                {booking.notes && (
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-gray-400">Note:</span>
                    <span className="truncate">{booking.notes}</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    navigate(`/public/portal/bookings/${booking.id}`)
                  }
                >
                  View Details
                </Button>
                {(booking.status === "completed" ||
                  booking.status === "cancelled") && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRebook(booking.id)}
                    disabled={rebook.isPending}
                  >
                    {rebook.isPending ? "Rebooking..." : "Book Again"}
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
