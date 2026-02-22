import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, XIcon, PhoneIcon, MailIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import {
  useWaitlistEntries,
  useCreateBookingFromWaitlist,
  useBulkUpdateWaitlist,
  type WaitlistEntry,
} from "@/lib/api/hooks/useWaitlist";

interface WaitlistManagementProps {
  bookings?: any[];
}

export function WaitlistManagement({}: WaitlistManagementProps) {
  const { addToast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch waitlist data using react-query
  const { data: waitlistData, isLoading } = useWaitlistEntries({
    sort_by: "priority",
    limit: 100,
  });

  // Mutations for actions
  const createBookingMutation = useCreateBookingFromWaitlist();
  const updateStatusMutation = useBulkUpdateWaitlist();

  const waitlist = waitlistData?.items || [];

  const filteredWaitlist = waitlist.filter(
    (entry: WaitlistEntry) =>
      entry.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.service_name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleContact = async (entry: WaitlistEntry) => {
    try {
      await updateStatusMutation.mutateAsync({
        waitlist_ids: [entry.id],
        status: "notified",
      });
      addToast({
        title: "Success",
        description: `Contacted ${entry.client_name}`,
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to contact client",
        variant: "error",
      });
    }
  };

  const handleBook = async (entry: WaitlistEntry) => {
    try {
      const today = new Date().toISOString().split("T")[0];
      await createBookingMutation.mutateAsync({
        waitlist_id: entry.id,
        booking_date: entry.preferred_date || today,
        booking_time: "10:00",
      });
      addToast({
        title: "Success",
        description: `Booked ${entry.client_name}`,
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to book client",
        variant: "error",
      });
    }
  };

  const handleCancel = async (entry: WaitlistEntry) => {
    try {
      await updateStatusMutation.mutateAsync({
        waitlist_ids: [entry.id],
        status: "cancelled",
      });
      addToast({
        title: "Success",
        description: `Cancelled ${entry.client_name}'s waitlist entry`,
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to cancel waitlist entry",
        variant: "error",
      });
    }
  };

  const getStatusVariant = (
    status: string,
  ): "default" | "secondary" | "destructive" | "outline" | "accent" => {
    switch (status) {
      case "waiting":
        return "accent";
      case "notified":
        return "secondary";
      case "booked":
        return "default";
      case "cancelled":
        return "destructive";
      case "expired":
        return "outline";
      default:
        return "outline";
    }
  };

  return (
    <div className="space-y-3 sm:space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div className="min-w-0">
          <h3 className="text-sm sm:text-lg font-semibold">Waitlist</h3>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {waitlist.length} entries
          </p>
        </div>
      </div>

      <Input
        placeholder="Search..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="text-xs sm:text-sm"
      />

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner size="lg" />
        </div>
      ) : (
        <div className="space-y-2 sm:space-y-3">
          {filteredWaitlist.map((entry: WaitlistEntry) => (
            <Card key={entry.id} className="p-3 sm:p-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="space-y-2 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <div className="min-w-0">
                      <h4 className="font-semibold text-sm">
                        #{entry.priority_score}
                      </h4>
                      <p className="text-xs sm:text-sm font-medium truncate">
                        {entry.client_name}
                      </p>
                    </div>
                    <Badge
                      variant={getStatusVariant(entry.status)}
                      className="text-xs shrink-0"
                    >
                      {entry.status}
                    </Badge>
                  </div>
                  <p className="text-xs sm:text-sm text-muted-foreground truncate">
                    {entry.service_name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Added: {new Date(entry.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="space-y-2 text-xs sm:text-sm">
                  <div className="flex items-center gap-2 truncate">
                    <PhoneIcon size={14} className="shrink-0" />
                    <a
                      href={`tel:${entry.client_phone}`}
                      className="truncate hover:underline"
                    >
                      {entry.client_phone}
                    </a>
                  </div>
                  {entry.client_email && (
                    <div className="flex items-center gap-2 truncate">
                      <MailIcon size={14} className="shrink-0" />
                      <a
                        href={`mailto:${entry.client_email}`}
                        className="truncate hover:underline"
                      >
                        {entry.client_email}
                      </a>
                    </div>
                  )}
                  {entry.preferred_date && (
                    <p className="text-xs">
                      Pref:{" "}
                      {new Date(entry.preferred_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>

              {entry.status === "waiting" && (
                <div className="flex flex-wrap gap-2 mt-3 sm:mt-4">
                  <Button
                    size="sm"
                    onClick={() => handleContact(entry)}
                    variant="outline"
                    className="text-xs sm:text-sm flex-1 sm:flex-none"
                    disabled={updateStatusMutation.isPending}
                  >
                    Contact
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleBook(entry)}
                    className="text-xs sm:text-sm flex-1 sm:flex-none flex items-center gap-1"
                    disabled={createBookingMutation.isPending}
                  >
                    <CheckIcon size={14} />
                    Book
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleCancel(entry)}
                    className="text-xs sm:text-sm flex-1 sm:flex-none"
                    disabled={updateStatusMutation.isPending}
                  >
                    <XIcon size={14} />
                  </Button>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      {!isLoading && filteredWaitlist.length === 0 && (
        <Card className="p-6 sm:p-8 text-center text-xs sm:text-sm text-muted-foreground">
          No waitlist entries found
        </Card>
      )}
    </div>
  );
}
