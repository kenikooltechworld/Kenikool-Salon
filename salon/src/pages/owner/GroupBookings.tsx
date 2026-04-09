import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";
import {
  useGroupBookings,
  useConfirmGroupBooking,
  useCancelGroupBooking,
  type GroupBooking,
} from "@/hooks/useGroupBookings";
import { Users, Calendar, Check, X, Eye } from "@/components/icons";

export default function GroupBookings() {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [selectedBooking, setSelectedBooking] = useState<GroupBooking | null>(
    null,
  );
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const { data: bookings, isLoading } = useGroupBookings({
    status: statusFilter || undefined,
  });
  const confirmBooking = useConfirmGroupBooking();
  const cancelBooking = useCancelGroupBooking();

  const handleConfirm = async (bookingId: string) => {
    if (
      !confirm("Confirm this group booking and create individual appointments?")
    ) {
      return;
    }

    try {
      await confirmBooking.mutateAsync(bookingId);
      alert("Group booking confirmed successfully!");
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to confirm booking");
    }
  };

  const handleCancel = async (bookingId: string) => {
    const reason = prompt("Enter cancellation reason:");
    if (!reason) return;

    try {
      await cancelBooking.mutateAsync({
        bookingId,
        cancellationReason: reason,
      });
      alert("Group booking cancelled successfully!");
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to cancel booking");
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "secondary" | "accent" | "outline" | "destructive"
    > = {
      pending: "accent",
      confirmed: "default",
      in_progress: "default",
      completed: "default",
      cancelled: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  if (isLoading) {
    return <div className="p-6">Loading group bookings...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Users size={28} />
            Group Bookings
          </h1>
          <p className="text-gray-600 mt-1">
            Manage group bookings and coordinate multiple appointments
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-4 mb-6">
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Status</label>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <SelectItem value="">All Statuses</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="confirmed">Confirmed</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </Select>
          </div>
        </div>
      </Card>

      {/* Bookings List */}
      <div className="space-y-4">
        {bookings && bookings.length === 0 && (
          <Card className="p-8 text-center">
            <Users size={48} className="mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600">No group bookings found</p>
          </Card>
        )}

        {bookings?.map((booking) => (
          <Card key={booking.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold">
                    {booking.group_name}
                  </h3>
                  {getStatusBadge(booking.status)}
                  <Badge variant="secondary">{booking.group_type}</Badge>
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>
                    <strong>Organizer:</strong> {booking.organizer_name} (
                    {booking.organizer_email})
                  </p>
                  <p className="flex items-center gap-1">
                    <Calendar size={14} />
                    {new Date(booking.booking_date).toLocaleString()}
                  </p>
                  <p className="flex items-center gap-1">
                    <Users size={14} />
                    {booking.total_participants} participants
                  </p>
                </div>
              </div>

              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">
                  ${booking.final_total.toFixed(2)}
                </div>
                {booking.discount_percentage > 0 && (
                  <div className="text-sm text-green-600">
                    {booking.discount_percentage}% group discount
                  </div>
                )}
                <div className="text-sm text-gray-500 mt-1">
                  Base: ${booking.base_total.toFixed(2)}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-4 border-t">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedBooking(booking);
                  setShowDetailsModal(true);
                }}
              >
                <Eye size={16} className="mr-1" />
                View Details
              </Button>

              {booking.status === "pending" && (
                <>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleConfirm(booking.id)}
                    disabled={confirmBooking.isPending}
                  >
                    <Check size={16} className="mr-1" />
                    Confirm
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleCancel(booking.id)}
                    disabled={cancelBooking.isPending}
                  >
                    <X size={16} className="mr-1" />
                    Cancel
                  </Button>
                </>
              )}
            </div>
          </Card>
        ))}
      </div>

      {/* Details Modal */}
      {selectedBooking && (
        <Modal
          open={showDetailsModal}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedBooking(null);
          }}
        >
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              Group Booking Details
            </h2>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Group Information</h4>
                <div className="text-sm space-y-1">
                  <p>
                    <strong>Name:</strong> {selectedBooking.group_name}
                  </p>
                  <p>
                    <strong>Type:</strong> {selectedBooking.group_type}
                  </p>
                  <p>
                    <strong>Date:</strong>{" "}
                    {new Date(selectedBooking.booking_date).toLocaleString()}
                  </p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Organizer</h4>
                <div className="text-sm space-y-1">
                  <p>{selectedBooking.organizer_name}</p>
                  <p>{selectedBooking.organizer_email}</p>
                  <p>{selectedBooking.organizer_phone}</p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">
                  Participants ({selectedBooking.participants.length})
                </h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {selectedBooking.participants.map((participant, index) => (
                    <Card key={index} className="p-3 bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="text-sm">
                          <p className="font-medium">{participant.name}</p>
                          {participant.email && (
                            <p className="text-gray-600">{participant.email}</p>
                          )}
                        </div>
                        {getStatusBadge(participant.status || "pending")}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              {selectedBooking.special_requests && (
                <div>
                  <h4 className="font-semibold mb-2">Special Requests</h4>
                  <p className="text-sm text-gray-600">
                    {selectedBooking.special_requests}
                  </p>
                </div>
              )}

              <div>
                <h4 className="font-semibold mb-2">Pricing</h4>
                <div className="text-sm space-y-1">
                  <div className="flex justify-between">
                    <span>Base Total:</span>
                    <span>${selectedBooking.base_total.toFixed(2)}</span>
                  </div>
                  {selectedBooking.discount_percentage > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>
                        Group Discount ({selectedBooking.discount_percentage}%):
                      </span>
                      <span>
                        -${selectedBooking.discount_amount.toFixed(2)}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between font-bold pt-2 border-t">
                    <span>Final Total:</span>
                    <span>${selectedBooking.final_total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
