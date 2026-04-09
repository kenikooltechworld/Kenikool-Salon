import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ClockIcon, UsersIcon, XCircleIcon } from "@/components/icons";
import {
  useWaitlistPosition,
  useCancelWaitlist,
} from "@/hooks/usePublicWaitlist";

export default function WaitlistStatus() {
  const [email, setEmail] = useState("");
  const [searchEmail, setSearchEmail] = useState<string | null>(null);

  const { data: position, isLoading } = useWaitlistPosition(searchEmail);
  const cancelWaitlist = useCancelWaitlist();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchEmail(email);
  };

  const handleCancel = async () => {
    if (!searchEmail) return;

    try {
      await cancelWaitlist.mutateAsync(searchEmail);
      setSearchEmail(null);
      setEmail("");
    } catch (error) {
      console.error("Failed to cancel waitlist:", error);
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-2xl font-bold text-gray-900 mb-2">
        Check Waitlist Status
      </h3>
      <p className="text-gray-600 mb-6">
        Enter your email to see your position in the queue.
      </p>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="email" className="sr-only">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
            />
          </div>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Checking..." : "Check Status"}
          </Button>
        </div>
      </form>

      {searchEmail && !isLoading && !position && (
        <Alert>
          <AlertDescription>
            No waitlist entry found for this email address.
          </AlertDescription>
        </Alert>
      )}

      {position && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <UsersIcon className="w-5 h-5 text-blue-600" />
                <div className="text-sm text-gray-600">Your Position</div>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                #{position.position}
              </div>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <ClockIcon className="w-5 h-5 text-purple-600" />
                <div className="text-sm text-gray-600">Estimated Wait</div>
              </div>
              <div className="text-3xl font-bold text-purple-600">
                {position.estimated_wait_time_minutes} min
              </div>
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-600 mb-1">Status</div>
                <div className="font-semibold text-gray-900 capitalize">
                  {position.status}
                </div>
              </div>
              <div>
                <div className="text-gray-600 mb-1">Checked In</div>
                <div className="font-semibold text-gray-900">
                  {new Date(position.check_in_time).toLocaleTimeString()}
                </div>
              </div>
              {position.service_name && (
                <div>
                  <div className="text-gray-600 mb-1">Service</div>
                  <div className="font-semibold text-gray-900">
                    {position.service_name}
                  </div>
                </div>
              )}
              {position.staff_name && (
                <div>
                  <div className="text-gray-600 mb-1">Staff</div>
                  <div className="font-semibold text-gray-900">
                    {position.staff_name}
                  </div>
                </div>
              )}
            </div>
          </div>

          <Alert>
            <AlertDescription>
              We'll send you notifications when your turn is approaching. Please
              keep your phone nearby.
            </AlertDescription>
          </Alert>

          <Button
            variant="destructive"
            className="w-full"
            onClick={handleCancel}
            disabled={cancelWaitlist.isPending}
          >
            {cancelWaitlist.isPending ? (
              "Cancelling..."
            ) : (
              <>
                <XCircleIcon className="w-4 h-4 mr-2" />
                Cancel Waitlist Entry
              </>
            )}
          </Button>

          {cancelWaitlist.isError && (
            <Alert variant="destructive">
              <AlertDescription>
                Failed to cancel waitlist entry. Please try again.
              </AlertDescription>
            </Alert>
          )}
        </div>
      )}
    </Card>
  );
}
