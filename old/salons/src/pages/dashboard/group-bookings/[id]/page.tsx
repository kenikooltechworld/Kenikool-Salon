import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  useGroupBooking,
  useUpdateGroupBookingStatus,
  useDeleteGroupBooking,
} from "@/lib/api/hooks/useGroupBookings";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/hooks/use-toast";
import { useConfirmation } from "@/hooks/use-confirmation";
import {
  ArrowLeftIcon,
  UsersIcon,
  CalendarIcon,
  PhoneIcon,
  MailIcon,
  ClockIcon,
  EditIcon,
  CreditCardIcon,
  BellIcon,
} from "@/components/icons";
import { format } from "date-fns";
import {
  GroupBookingEditModal,
  PaymentRecordModal,
  SendReminderModal,
} from "@/components/group-bookings";

export default function GroupBookingDetailsPage() {
  const params = useParams();
  const navigate = useNavigate();
  const bookingId = params.id as string;
  const { toast } = useToast();
  const { confirm, ConfirmationDialog } = useConfirmation();

  const { data: booking, isLoading } = useGroupBooking(bookingId);
  const updateStatus = useUpdateGroupBookingStatus();
  const deleteBooking = useDeleteGroupBooking();

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [isReminderModalOpen, setIsReminderModalOpen] = useState(false);

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

  const handleConfirm = async () => {
    const confirmed = await confirm({
      title: "Confirm Booking",
      message: "Are you sure you want to confirm this group booking?",
      confirmText: "Confirm",
    });

    if (confirmed) {
      updateStatus.mutate(
        { bookingId, status: "confirmed" },
        {
          onSuccess: () => {
            toast("Group booking confirmed successfully", "success");
          },
          onError: (error: Error) => {
            toast(error.message || "Failed to confirm booking", "error");
          },
        }
      );
    }
  };

  const handleComplete = async () => {
    const confirmed = await confirm({
      title: "Complete Booking",
      message: "Mark this group booking as completed?",
      confirmText: "Complete",
    });

    if (confirmed) {
      updateStatus.mutate(
        { bookingId, status: "completed" },
        {
          onSuccess: () => {
            toast("Group booking marked as completed", "success");
          },
          onError: (error: Error) => {
            toast(error.message || "Failed to complete booking", "error");
          },
        }
      );
    }
  };

  const handleCancel = async () => {
    const confirmed = await confirm({
      title: "Cancel Booking",
      message:
        "Are you sure you want to cancel this group booking? This action cannot be undone.",
      confirmText: "Cancel Booking",
      variant: "danger",
    });

    if (confirmed) {
      updateStatus.mutate(
        { bookingId, status: "cancelled" },
        {
          onSuccess: () => {
            toast("Group booking cancelled successfully", "success");
          },
          onError: (error: Error) => {
            toast(error.message || "Failed to cancel booking", "error");
          },
        }
      );
    }
  };

  const handleDelete = async () => {
    const confirmed = await confirm({
      title: "Delete Booking",
      message:
        "Are you sure you want to delete this group booking? This action cannot be undone.",
      confirmText: "Delete",
      variant: "danger",
    });

    if (confirmed) {
      deleteBooking.mutate(bookingId, {
        onSuccess: () => {
          toast("Group booking deleted successfully", "success");
          navigate("/dashboard/group-bookings");
        },
        onError: (error: Error) => {
          toast(error.message || "Failed to delete booking", "error");
        },
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <ConfirmationDialog />
        <Spinner size="lg" />
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ConfirmationDialog />
        <Card>
          <CardContent className="py-12 text-center">
            <h2 className="text-xl font-semibold mb-2">
              Group Booking Not Found
            </h2>
            <p className="text-muted-foreground mb-4">
              The group booking you&apos;re looking for doesn&apos;t exist.
            </p>
            <Button onClick={() => navigate("/dashboard/group-bookings")}>
              Back to Group Bookings
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <ConfirmationDialog />

      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => navigate("/dashboard/group-bookings")}
          className="mb-4"
        >
          <ArrowLeftIcon className="w-4 h-4 mr-2" />
          Back to Group Bookings
        </Button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Group Booking Details
            </h1>
            <p className="text-muted-foreground mt-1">
              Booking ID: {booking._id}
            </p>
          </div>
          <Badge
            variant={getStatusColor(booking.status)}
            className="text-lg px-4 py-2"
          >
            {booking.status}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Organizer Information */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Organizer Information</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Name
                  </label>
                  <p className="text-lg font-medium">
                    {booking.organizer_name}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Phone
                  </label>
                  <div className="flex items-center gap-2 mt-1">
                    <PhoneIcon className="w-4 h-4 text-muted-foreground" />
                    <p className="text-lg">{booking.organizer_phone}</p>
                  </div>
                </div>

                {booking.organizer_email && (
                  <div className="md:col-span-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Email
                    </label>
                    <div className="flex items-center gap-2 mt-1">
                      <MailIcon className="w-4 h-4 text-muted-foreground" />
                      <p className="text-lg">{booking.organizer_email}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Booking Details */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Booking Details</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Date & Time
                  </label>
                  <div className="flex items-center gap-2 mt-1">
                    <CalendarIcon className="w-4 h-4 text-muted-foreground" />
                    <p className="text-lg">
                      {format(new Date(booking.booking_date), "PPP")} at{" "}
                      {format(new Date(booking.booking_date), "p")}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Total Members
                  </label>
                  <div className="flex items-center gap-2 mt-1">
                    <UsersIcon className="w-4 h-4 text-muted-foreground" />
                    <p className="text-lg font-semibold">
                      {booking.total_members} members
                    </p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Total Price
                  </label>
                  <p className="text-2xl font-bold text-primary">
                    ₦{booking.total_price.toLocaleString()}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Payment Status
                  </label>
                  <Badge
                    variant={
                      booking.payment_status === "paid" ? "success" : "warning"
                    }
                    className="mt-1"
                  >
                    {booking.payment_status}
                  </Badge>
                </div>
              </div>

              {booking.notes && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Notes
                  </label>
                  <p className="text-base mt-1 p-3 bg-muted rounded-md">
                    {booking.notes}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Members List */}
          {booking.members && booking.members.length > 0 && (
            <Card>
              <CardHeader>
                <h2 className="text-xl font-semibold">Group Members</h2>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {booking.members.map(
                    (
                      member: {
                        client_name: string;
                        client_phone: string;
                        client_email?: string;
                        service_name?: string;
                        service_price?: number;
                      },
                      index: number
                    ) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 bg-muted rounded-md"
                      >
                        <div className="flex-1">
                          <p className="font-medium">{member.client_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {member.client_phone}
                          </p>
                          {member.client_email && (
                            <p className="text-sm text-muted-foreground">
                              {member.client_email}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          {member.service_name && (
                            <Badge variant="outline" className="mb-1">
                              {member.service_name}
                            </Badge>
                          )}
                          {member.service_price !== undefined && (
                            <p className="text-sm font-semibold">
                              ₦{member.service_price.toLocaleString()}
                            </p>
                          )}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Timeline */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Timeline</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <ClockIcon className="w-5 h-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Created</p>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date(booking.created_at), "PPP 'at' p")}
                  </p>
                </div>
              </div>

              {booking.confirmed_at && (
                <div className="flex items-start gap-3">
                  <ClockIcon className="w-5 h-5 text-success mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Confirmed</p>
                    <p className="text-sm text-muted-foreground">
                      {format(new Date(booking.confirmed_at), "PPP 'at' p")}
                    </p>
                  </div>
                </div>
              )}

              {booking.completed_at && (
                <div className="flex items-start gap-3">
                  <ClockIcon className="w-5 h-5 text-info mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Completed</p>
                    <p className="text-sm text-muted-foreground">
                      {format(new Date(booking.completed_at), "PPP 'at' p")}
                    </p>
                  </div>
                </div>
              )}

              {booking.cancelled_at && (
                <div className="flex items-start gap-3">
                  <ClockIcon className="w-5 h-5 text-error mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Cancelled</p>
                    <p className="text-sm text-muted-foreground">
                      {format(new Date(booking.cancelled_at), "PPP 'at' p")}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Actions</h2>
            </CardHeader>
            <CardContent className="space-y-2">
              {/* Edit Button - Available for pending and confirmed */}
              {(booking.status === "pending" ||
                booking.status === "confirmed") && (
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => setIsEditModalOpen(true)}
                >
                  <EditIcon className="w-4 h-4 mr-2" />
                  Edit Booking
                </Button>
              )}

              {/* Payment Button - Available for all except cancelled */}
              {booking.status !== "cancelled" && (
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => setIsPaymentModalOpen(true)}
                >
                  <CreditCardIcon className="w-4 h-4 mr-2" />
                  Record Payment
                </Button>
              )}

              {/* Send Reminder Button - Available for pending and confirmed */}
              {(booking.status === "pending" ||
                booking.status === "confirmed") && (
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => setIsReminderModalOpen(true)}
                >
                  <BellIcon className="w-4 h-4 mr-2" />
                  Send Reminder
                </Button>
              )}

              {booking.status === "pending" && (
                <>
                  <Button
                    className="w-full"
                    variant="primary"
                    onClick={handleConfirm}
                    disabled={updateStatus.isPending}
                  >
                    {updateStatus.isPending
                      ? "Confirming..."
                      : "Confirm Booking"}
                  </Button>
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={handleCancel}
                    disabled={updateStatus.isPending}
                  >
                    Cancel Booking
                  </Button>
                </>
              )}

              {booking.status === "confirmed" && (
                <>
                  <Button
                    className="w-full"
                    variant="primary"
                    onClick={handleComplete}
                    disabled={updateStatus.isPending}
                  >
                    {updateStatus.isPending
                      ? "Completing..."
                      : "Mark as Completed"}
                  </Button>
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={handleCancel}
                    disabled={updateStatus.isPending}
                  >
                    Cancel Booking
                  </Button>
                </>
              )}

              {(booking.status === "cancelled" ||
                booking.status === "completed") && (
                <Button
                  className="w-full"
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={deleteBooking.isPending}
                >
                  {deleteBooking.isPending ? "Deleting..." : "Delete Booking"}
                </Button>
              )}

              <Button
                className="w-full"
                variant="outline"
                onClick={() => window.print()}
              >
                Print Details
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modals */}
      {booking && (
        <>
          <GroupBookingEditModal
            isOpen={isEditModalOpen}
            onClose={() => setIsEditModalOpen(false)}
            booking={booking}
          />
          <PaymentRecordModal
            isOpen={isPaymentModalOpen}
            onClose={() => setIsPaymentModalOpen(false)}
            booking={booking}
          />
          <SendReminderModal
            isOpen={isReminderModalOpen}
            onClose={() => setIsReminderModalOpen(false)}
            booking={booking}
          />
        </>
      )}
    </div>
  );
}
