import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useGroupBookingById } from "@/hooks/usePublicGroupBookings";
import {
  CheckCircle,
  Calendar,
  Users,
  Mail,
  Phone,
  DollarSign,
} from "@/components/icons";

export default function GroupBookingConfirmation() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: booking, isLoading } = useGroupBookingById(id!);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading booking details...</p>
        </div>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-8 max-w-md text-center">
          <h2 className="text-xl font-semibold mb-4">Booking Not Found</h2>
          <p className="text-gray-600 mb-6">
            We couldn't find the booking you're looking for.
          </p>
          <Button onClick={() => navigate("/public")}>Return to Home</Button>
        </Card>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Success Header */}
        <div className="text-center mb-8">
          <CheckCircle size={64} className="mx-auto mb-4 text-green-600" />
          <h1 className="text-3xl font-bold mb-2">Group Booking Submitted!</h1>
          <p className="text-gray-600">
            Your group booking request has been received. We'll review it and
            send confirmation to your email.
          </p>
        </div>

        {/* Booking Status */}
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Booking Status</h2>
            <Badge
              variant={
                booking.status === "confirmed"
                  ? "default"
                  : booking.status === "cancelled"
                    ? "destructive"
                    : "default"
              }
            >
              {booking.status.toUpperCase()}
            </Badge>
          </div>
          <p className="text-sm text-gray-600">
            Booking ID: <span className="font-mono">{booking.id}</span>
          </p>
        </Card>

        {/* Group Details */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Group Details</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Users size={20} className="text-gray-400 mt-0.5" />
              <div>
                <p className="font-medium">{booking.group_name}</p>
                <p className="text-sm text-gray-600">
                  {booking.total_participants} participants •{" "}
                  {booking.group_type}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar size={20} className="text-gray-400 mt-0.5" />
              <div>
                <p className="font-medium">Preferred Date & Time</p>
                <p className="text-sm text-gray-600">
                  {formatDate(booking.booking_date)}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Organizer Details */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Organizer Contact</h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Mail size={20} className="text-gray-400" />
              <div>
                <p className="font-medium">{booking.organizer_name}</p>
                <p className="text-sm text-gray-600">
                  {booking.organizer_email}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Phone size={20} className="text-gray-400" />
              <p className="text-sm text-gray-600">{booking.organizer_phone}</p>
            </div>
          </div>
        </Card>

        {/* Pricing Summary */}
        <Card className="p-6 mb-6 bg-blue-50">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <DollarSign size={20} className="mr-2" />
            Pricing Summary
          </h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Base Total:</span>
              <span>${booking.base_total.toFixed(2)}</span>
            </div>
            {booking.discount_percentage > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Group Discount ({booking.discount_percentage}%):</span>
                <span>-${booking.discount_amount.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-lg font-bold pt-2 border-t">
              <span>Final Total:</span>
              <span>${booking.final_total.toFixed(2)}</span>
            </div>
          </div>
        </Card>

        {/* Special Requests */}
        {booking.special_requests && (
          <Card className="p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Special Requests</h2>
            <p className="text-gray-600">{booking.special_requests}</p>
          </Card>
        )}

        {/* Next Steps */}
        <Card className="p-6 mb-6 bg-yellow-50">
          <h2 className="text-xl font-semibold mb-4">What Happens Next?</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>We'll review your group booking request</li>
            <li>You'll receive a confirmation email within 24 hours</li>
            <li>
              Once confirmed, individual appointments will be created for each
              participant
            </li>
            <li>
              Payment instructions will be included in the confirmation email
            </li>
          </ol>
        </Card>

        {/* Actions */}
        <div className="flex gap-4">
          <Button
            onClick={() => navigate("/public")}
            variant="outline"
            className="flex-1"
          >
            Return to Home
          </Button>
          <Button
            onClick={() => window.print()}
            variant="outline"
            className="flex-1"
          >
            Print Confirmation
          </Button>
        </div>
      </div>
    </div>
  );
}
