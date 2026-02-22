import React, { useState } from "react";
import { RecurringBookingForm } from "@/components/booking/recurring-booking-form";
import { RecurringBookingList } from "@/components/booking/recurring-booking-list";
import { useRecurringBookings } from "@/lib/api/hooks/useRecurringBookings";

export default function RecurringBookingsPage() {
  const [showForm, setShowForm] = useState(false);
  const { recurringBookings, loading, refetch } = useRecurringBookings();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Recurring Bookings</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "Create Recurring Booking"}
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <RecurringBookingForm
            onSuccess={() => {
              setShowForm(false);
              refetch();
            }}
          />
        </div>
      )}

      <RecurringBookingList bookings={recurringBookings} loading={loading} />
    </div>
  );
}
