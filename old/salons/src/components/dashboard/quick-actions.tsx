import { memo, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  PlusIcon,
  UsersIcon,
  ScissorsIcon,
  UserIcon,
} from "@/components/icons";

/**
 * QuickActions component displays quick action buttons for common tasks
 * Memoized to prevent unnecessary re-renders
 */
export const QuickActions = memo(function QuickActions() {
  const handleNewBooking = useCallback(() => {
    window.location.href = "/dashboard/bookings";
  }, []);

  const handleAddClient = useCallback(() => {
    window.location.href = "/dashboard/clients";
  }, []);

  const handleAddService = useCallback(() => {
    window.location.href = "/dashboard/services";
  }, []);

  const handleAddStaff = useCallback(() => {
    window.location.href = "/dashboard/staff";
  }, []);

  return (
    <Card className="p-6 animate-in fade-in-0 slide-in-from-bottom-4 duration-500">
      <h2 className="text-lg font-semibold text-foreground mb-4">
        Quick Actions
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Button
          variant="outline"
          className="h-auto py-4 flex-col gap-2 transition-all duration-300 ease-out hover:scale-105 hover:shadow-md transform will-change-transform"
          onClick={handleNewBooking}
        >
          <PlusIcon
            size={20}
            className="transition-transform duration-300 ease-out group-hover:scale-110"
          />
          <span className="text-sm">New Booking</span>
        </Button>
        <Button
          variant="outline"
          className="h-auto py-4 flex-col gap-2 transition-all duration-300 ease-out hover:scale-105 hover:shadow-md transform will-change-transform"
          onClick={handleAddClient}
        >
          <UsersIcon
            size={20}
            className="transition-transform duration-300 ease-out group-hover:scale-110"
          />
          <span className="text-sm">Add Client</span>
        </Button>
        <Button
          variant="outline"
          className="h-auto py-4 flex-col gap-2 transition-all duration-300 ease-out hover:scale-105 hover:shadow-md transform will-change-transform"
          onClick={handleAddService}
        >
          <ScissorsIcon
            size={20}
            className="transition-transform duration-300 ease-out group-hover:scale-110"
          />
          <span className="text-sm">Add Service</span>
        </Button>
        <Button
          variant="outline"
          className="h-auto py-4 flex-col gap-2 transition-all duration-300 ease-out hover:scale-105 hover:shadow-md transform will-change-transform"
          onClick={handleAddStaff}
        >
          <UserIcon
            size={20}
            className="transition-transform duration-300 ease-out group-hover:scale-110"
          />
          <span className="text-sm">Add Staff</span>
        </Button>
      </div>
    </Card>
  );
});
