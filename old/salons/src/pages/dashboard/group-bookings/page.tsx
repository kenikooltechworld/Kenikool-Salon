import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription } from "@/components/ui/card";
import { PlusIcon } from "@/components/icons";
import {
  GroupBookingFormModal,
  GroupBookingList,
} from "@/components/group-bookings";
import { useGroupBookings } from "@/lib/api/hooks/useGroupBookings";

export default function GroupBookingsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: groupBookings = [] } = useGroupBookings();

  // Calculate stats from actual data
  const stats = {
    total: groupBookings.length,
    pending: groupBookings.filter((b) => b.status === "pending").length,
    confirmed: groupBookings.filter((b) => b.status === "confirmed").length,
    completed: groupBookings.filter((b) => b.status === "completed").length,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--foreground)]">
            Group Bookings
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Manage group bookings and party reservations
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <PlusIcon className="w-5 h-5 mr-2" />
          Create Group Booking
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Total Bookings</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--foreground)]">
              {stats.total}
            </p>
          </CardContent>
        </Card>
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Pending</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--warning)]">
              {stats.pending}
            </p>
          </CardContent>
        </Card>
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Confirmed</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--success)]">
              {stats.confirmed}
            </p>
          </CardContent>
        </Card>
        <Card variant="elevated">
          <CardContent>
            <CardDescription>Completed</CardDescription>
            <p className="text-2xl font-bold mt-1 text-[var(--info)]">
              {stats.completed}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Group Bookings List */}
      <GroupBookingList />

      {/* Create Modal */}
      <GroupBookingFormModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
}
