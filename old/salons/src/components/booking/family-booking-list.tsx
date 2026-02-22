import React from "react";
import { useFamilyAccounts } from "@/lib/api/hooks/useFamilyAccounts";
import { useBookings } from "@/lib/api/hooks/useBookings";
import { format } from "date-fns";

interface FamilyBooking {
  id: string;
  memberName: string;
  memberId: string;
  serviceName: string;
  stylistName: string;
  date: string;
  time: string;
  status: string;
}

interface FamilyBookingListProps {
  onBookingSelect?: (booking: FamilyBooking) => void;
}

export const FamilyBookingList: React.FC<FamilyBookingListProps> = ({
  onBookingSelect,
}) => {
  const { familyMembers, loading: membersLoading } = useFamilyAccounts();
  const { bookings, loading: bookingsLoading } = useBookings();

  if (membersLoading || bookingsLoading) {
    return <div className="text-sm text-gray-500">Loading bookings...</div>;
  }

  // Group bookings by family member
  const bookingsByMember = familyMembers?.reduce(
    (acc, member) => {
      const memberBookings = bookings.filter((b) => b.client_id === member.id);
      if (memberBookings.length > 0) {
        acc[member.id] = {
          memberName: member.name,
          bookings: memberBookings,
        };
      }
      return acc;
    },
    {} as Record<string, { memberName: string; bookings: typeof bookings }>,
  );

  if (!bookingsByMember || Object.keys(bookingsByMember).length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
        No family bookings found
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {Object.entries(bookingsByMember).map(
        ([memberId, { memberName, bookings: memberBookings }]) => (
          <div key={memberId} className="space-y-2">
            <h3 className="font-medium text-gray-900">{memberName}</h3>
            <div className="space-y-2">
              {memberBookings.map((booking) => (
                <div
                  key={booking.id}
                  onClick={() =>
                    onBookingSelect?.({
                      id: booking.id,
                      memberId,
                      memberName,
                      serviceName: booking.service_name,
                      stylistName: booking.stylist_name,
                      date: format(
                        new Date(booking.start_time),
                        "MMM dd, yyyy",
                      ),
                      time: format(new Date(booking.start_time), "h:mm a"),
                      status: booking.status,
                    })
                  }
                  className="flex items-center justify-between p-3 border rounded hover:bg-blue-50 cursor-pointer"
                >
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">
                      {booking.service_name}
                    </p>
                    <p className="text-xs text-gray-600">
                      {booking.stylist_name} •{" "}
                      {format(
                        new Date(booking.start_time),
                        "MMM dd, yyyy h:mm a",
                      )}
                    </p>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-1 rounded ${
                      booking.status === "confirmed"
                        ? "bg-green-100 text-green-700"
                        : booking.status === "cancelled"
                          ? "bg-red-100 text-red-700"
                          : "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {booking.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ),
      )}
    </div>
  );
};
