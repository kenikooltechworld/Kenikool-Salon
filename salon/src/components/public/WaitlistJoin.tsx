import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ClockIcon, UsersIcon, CheckCircleIcon } from "@/components/icons";
import {
  useWaitlistStatus,
  useJoinWaitlist,
  type JoinWaitlistData,
} from "@/hooks/usePublicWaitlist";

interface WaitlistJoinProps {
  serviceId: string;
  serviceName: string;
  staffId?: string;
  staffName?: string;
  onSuccess?: (queueEntryId: string, position: number) => void;
}

export default function WaitlistJoin({
  serviceId,
  serviceName,
  staffId,
  staffName,
  onSuccess,
}: WaitlistJoinProps) {
  const { data: status, isLoading: statusLoading } = useWaitlistStatus();
  const joinWaitlist = useJoinWaitlist();

  const [formData, setFormData] = useState({
    customer_name: "",
    customer_email: "",
    customer_phone: "",
    notes: "",
  });

  const [showSuccess, setShowSuccess] = useState(false);
  const [successData, setSuccessData] = useState<{
    position: number;
    estimatedWait: number;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const waitlistData: JoinWaitlistData = {
      service_id: serviceId,
      staff_id: staffId,
      customer_name: formData.customer_name,
      customer_email: formData.customer_email,
      customer_phone: formData.customer_phone,
      notes: formData.notes || undefined,
    };

    try {
      const response = await joinWaitlist.mutateAsync(waitlistData);
      setSuccessData({
        position: response.position,
        estimatedWait: response.estimated_wait_time_minutes,
      });
      setShowSuccess(true);

      if (onSuccess) {
        onSuccess(response.queue_entry_id, response.position);
      }
    } catch (error) {
      console.error("Failed to join waitlist:", error);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (statusLoading) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          Loading waitlist status...
        </div>
      </Card>
    );
  }

  if (!status?.is_accepting) {
    return (
      <Card className="p-6">
        <Alert>
          <AlertDescription>
            {status?.message ||
              "Waitlist is currently not accepting new entries."}
          </AlertDescription>
        </Alert>
      </Card>
    );
  }

  if (showSuccess && successData) {
    return (
      <Card className="p-6">
        <div className="text-center">
          <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            You're on the Waitlist!
          </h3>
          <p className="text-gray-600 mb-6">
            We'll notify you when it's your turn.
          </p>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Your Position</div>
              <div className="text-3xl font-bold text-blue-600">
                #{successData.position}
              </div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Estimated Wait</div>
              <div className="text-3xl font-bold text-purple-600">
                {successData.estimatedWait} min
              </div>
            </div>
          </div>

          <Alert className="mb-4">
            <AlertDescription>
              We've sent a confirmation to {formData.customer_email}. You'll
              receive updates about your position in the queue.
            </AlertDescription>
          </Alert>

          <Button
            variant="outline"
            onClick={() => {
              setShowSuccess(false);
              setFormData({
                customer_name: "",
                customer_email: "",
                customer_phone: "",
                notes: "",
              });
            }}
          >
            Join Another Waitlist
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Join the Waitlist
        </h3>
        <p className="text-gray-600">
          No available time slots? Join our waitlist and we'll notify you when a
          spot opens up.
        </p>
      </div>

      {/* Waitlist Status */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          <UsersIcon className="w-5 h-5 text-gray-600" />
          <div>
            <div className="text-sm text-gray-600">People Waiting</div>
            <div className="text-lg font-semibold text-gray-900">
              {status?.queue_length || 0}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
          <ClockIcon className="w-5 h-5 text-gray-600" />
          <div>
            <div className="text-sm text-gray-600">Avg. Wait Time</div>
            <div className="text-lg font-semibold text-gray-900">
              {status?.average_wait_time_minutes || 0} min
            </div>
          </div>
        </div>
      </div>

      {/* Service Info */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <div className="text-sm text-gray-600 mb-1">Service</div>
        <div className="font-semibold text-gray-900">{serviceName}</div>
        {staffName && (
          <>
            <div className="text-sm text-gray-600 mt-2 mb-1">Staff</div>
            <div className="font-semibold text-gray-900">{staffName}</div>
          </>
        )}
      </div>

      {/* Join Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="customer_name">Full Name *</Label>
          <Input
            id="customer_name"
            name="customer_name"
            type="text"
            required
            value={formData.customer_name}
            onChange={handleChange}
            placeholder="John Doe"
          />
        </div>

        <div>
          <Label htmlFor="customer_email">Email *</Label>
          <Input
            id="customer_email"
            name="customer_email"
            type="email"
            required
            value={formData.customer_email}
            onChange={handleChange}
            placeholder="john@example.com"
          />
        </div>

        <div>
          <Label htmlFor="customer_phone">Phone Number *</Label>
          <Input
            id="customer_phone"
            name="customer_phone"
            type="tel"
            required
            value={formData.customer_phone}
            onChange={handleChange}
            placeholder="+1 (555) 123-4567"
          />
        </div>

        <div>
          <Label htmlFor="notes">Additional Notes (Optional)</Label>
          <Textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Any special requests or preferences..."
            rows={3}
          />
        </div>

        {joinWaitlist.isError && (
          <Alert variant="destructive">
            <AlertDescription>
              Failed to join waitlist. Please try again.
            </AlertDescription>
          </Alert>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={joinWaitlist.isPending}
        >
          {joinWaitlist.isPending ? "Joining..." : "Join Waitlist"}
        </Button>
      </form>
    </Card>
  );
}
