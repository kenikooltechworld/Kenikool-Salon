import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectItem } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreatePublicGroupBooking,
  type GroupBookingParticipant,
} from "@/hooks/usePublicGroupBookings";
import { useServices } from "@/hooks/useServices";
import { useStaff } from "@/hooks/useStaff";
import { useToast } from "@/components/ui/toast";
import { Users, Plus, Trash2, NairaSign, Info, RefreshCwIcon } from "@/components/icons";

export default function GroupBooking() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { data: services, isLoading: servicesLoading, refetch: refetchServices } =
    useServices();
  const { data: staff, isLoading: staffLoading, refetch: refetchStaff } =
    useStaff();
  const createBooking = useCreatePublicGroupBooking();

  const isOptionsLoading = servicesLoading || staffLoading;

  const [groupName, setGroupName] = useState("");
  const [groupType, setGroupType] = useState("other");
  const [organizerName, setOrganizerName] = useState("");
  const [organizerEmail, setOrganizerEmail] = useState("");
  const [organizerPhone, setOrganizerPhone] = useState("");
  const [bookingDate, setBookingDate] = useState("");
  const [specialRequests, setSpecialRequests] = useState("");
  const [participants, setParticipants] = useState<GroupBookingParticipant[]>([
    { name: "", service_id: "", staff_id: "", email: "", phone: "" },
    { name: "", service_id: "", staff_id: "", email: "", phone: "" },
  ]);

  const addParticipant = () => {
    if (participants.length >= 20) {
      alert("Maximum 20 participants allowed");
      return;
    }
    setParticipants([
      ...participants,
      { name: "", service_id: "", staff_id: "", email: "", phone: "" },
    ]);
  };

  const removeParticipant = (index: number) => {
    if (participants.length <= 2) {
      alert("Minimum 2 participants required");
      return;
    }
    setParticipants(participants.filter((_, i) => i !== index));
  };

  const updateParticipant = (index: number, field: string, value: string) => {
    const updated = [...participants];
    updated[index] = { ...updated[index], [field]: value };
    setParticipants(updated);
  };

  const calculatePricing = () => {
    let baseTotal = 0;
    participants.forEach((p) => {
      const service = services?.find((s) => s.id === p.service_id);
      if (service) {
        baseTotal += service.price;
      }
    });

    let discountPct = 0;
    if (participants.length >= 10) discountPct = 20;
    else if (participants.length >= 5) discountPct = 15;
    else if (participants.length >= 3) discountPct = 10;

    const discountAmount = baseTotal * (discountPct / 100);
    const finalTotal = baseTotal - discountAmount;

    return { baseTotal, discountPct, discountAmount, finalTotal };
  };

  const pricing = calculatePricing();

  if (isOptionsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-center mb-8">
            <Skeleton className="h-12 w-12 mx-auto mb-4 rounded-full" />
            <Skeleton className="h-8 w-64 mx-auto mb-2" />
            <Skeleton className="h-4 w-96 mx-auto" />
          </div>

          <Card className="p-6 space-y-4">
            <Skeleton className="h-6 w-32" />
            <div className="space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          </Card>

          <Card className="p-6 space-y-4">
            <Skeleton className="h-6 w-40" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full md:col-span-2" />
            </div>
          </Card>

          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-9 w-32" />
            </div>
            <div className="space-y-4">
              {[...Array(2)].map((_, i) => (
                <Card key={i} className="p-4 bg-gray-50 space-y-3">
                  <Skeleton className="h-5 w-24" />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                </Card>
              ))}
            </div>
          </Card>

          <Card className="p-6 space-y-4">
            <Skeleton className="h-6 w-40" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </Card>

          <div className="flex gap-4">
            <Skeleton className="h-10 flex-1" />
            <Skeleton className="h-10 flex-1" />
          </div>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (
      !groupName ||
      !organizerName ||
      !organizerEmail ||
      !organizerPhone ||
      !bookingDate
    ) {
      alert("Please fill in all organizer details");
      return;
    }

    const invalidParticipants = participants.filter(
      (p) => !p.name || !p.service_id,
    );
    if (invalidParticipants.length > 0) {
      alert("Please fill in name and service for all participants");
      return;
    }

    try {
      const result = await createBooking.mutateAsync({
        group_name: groupName,
        group_type: groupType,
        organizer_name: organizerName,
        organizer_email: organizerEmail,
        organizer_phone: organizerPhone,
        booking_date: new Date(bookingDate).toISOString(),
        participants: participants.map((p) => ({
          name: p.name,
          email: p.email || undefined,
          phone: p.phone || undefined,
          service_id: p.service_id,
          staff_id: p.staff_id || undefined,
        })),
        special_requests: specialRequests || undefined,
      });

      navigate(`/public/group-booking-confirmation/₦{result.id}`);
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to create group booking");
    }
  };

  const handleRefresh = () => {
    refetchServices();
    refetchStaff();
    showToast({
      title: "Refreshed",
      description: "Services and staff updated",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="text-center flex-1">
            <Users size={48} className="mx-auto mb-4 text-blue-600" />
            <h1 className="text-3xl font-bold mb-2">Group Booking</h1>
            <p className="text-gray-600">
              Book for multiple people and save with group discounts
            </p>
          </div>
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <RefreshCwIcon size={16} />
            Refresh
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Group Details */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Group Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Group Name *
                </label>
                <Input
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  placeholder="e.g., Smith Family Spa Day"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Group Type
                </label>
                <Select
                  value={groupType}
                  onChange={(e) => setGroupType(e.target.value)}
                >
                  <SelectItem value="family">Family</SelectItem>
                  <SelectItem value="corporate">Corporate</SelectItem>
                  <SelectItem value="party">Party</SelectItem>
                  <SelectItem value="event">Event</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Preferred Date & Time *
                </label>
                <Input
                  type="datetime-local"
                  value={bookingDate}
                  onChange={(e) => setBookingDate(e.target.value)}
                  required
                />
              </div>
            </div>
          </Card>

          {/* Organizer Details */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Organizer Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <Input
                  value={organizerName}
                  onChange={(e) => setOrganizerName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Email *
                </label>
                <Input
                  type="email"
                  value={organizerEmail}
                  onChange={(e) => setOrganizerEmail(e.target.value)}
                  required
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1">
                  Phone *
                </label>
                <Input
                  type="tel"
                  value={organizerPhone}
                  onChange={(e) => setOrganizerPhone(e.target.value)}
                  required
                />
              </div>
            </div>
          </Card>

          {/* Participants */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">
                Participants ({participants.length})
              </h2>
              <Button
                type="button"
                onClick={addParticipant}
                variant="outline"
                size="sm"
              >
                <Plus size={16} className="mr-1" />
                Add Participant
              </Button>
            </div>

            <div className="space-y-4">
              {participants.map((participant, index) => (
                <Card key={index} className="p-4 bg-gray-50">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-medium">Participant {index + 1}</h3>
                    {participants.length > 2 && (
                      <Button
                        type="button"
                        onClick={() => removeParticipant(index)}
                        variant="ghost"
                        size="sm"
                      >
                        <Trash2 size={16} />
                      </Button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Name *
                      </label>
                      <Input
                        value={participant.name}
                        onChange={(e) =>
                          updateParticipant(index, "name", e.target.value)
                        }
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Service *
                      </label>
                      <Select
                        value={participant.service_id}
                        onChange={(e) =>
                          updateParticipant(index, "service_id", e.target.value)
                        }
                        required
                        disabled={isOptionsLoading}
                      >
                        <SelectItem value="">
                          {servicesLoading ? "Loading services..." : "Select service"}
                        </SelectItem>
                        {services?.map((service) => (
                          <SelectItem key={service.id} value={service.id}>
                            {service.name} - ₦{service.price}
                          </SelectItem>
                        ))}
                      </Select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Preferred Staff (Optional)
                      </label>
                      <Select
                        value={participant.staff_id || ""}
                        onChange={(e) =>
                          updateParticipant(index, "staff_id", e.target.value)
                        }
                        disabled={isOptionsLoading}
                      >
                        <SelectItem value="">
                          {staffLoading ? "Loading staff..." : "Any available"}
                        </SelectItem>
                        {staff?.map((s) => (
                          <SelectItem key={s.id} value={s.id}>
                            {s.firstName} {s.lastName}
                          </SelectItem>
                        ))}
                      </Select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Email (Optional)
                      </label>
                      <Input
                        type="email"
                        value={participant.email || ""}
                        onChange={(e) =>
                          updateParticipant(index, "email", e.target.value)
                        }
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>

          {/* Pricing Summary */}
          <Card className="p-6 bg-blue-50">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <NairaSign size={20} className="mr-2" />
              Pricing Summary
            </h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Base Total:</span>
                <span>₦{pricing.baseTotal.toFixed(2)}</span>
              </div>
              {pricing.discountPct > 0 && (
                <>
                  <div className="flex justify-between text-green-600">
                    <span>Group Discount ({pricing.discountPct}%):</span>
                    <span>-₦{pricing.discountAmount.toFixed(2)}</span>
                  </div>
                  <Badge variant="default" className="w-full justify-center">
                    You save ₦{pricing.discountAmount.toFixed(2)}!
                  </Badge>
                </>
              )}
              <div className="flex justify-between text-lg font-bold pt-2 border-t">
                <span>Final Total:</span>
                <span>₦{pricing.finalTotal.toFixed(2)}</span>
              </div>
            </div>

            <div className="mt-4 p-3 bg-white rounded flex items-start gap-2">
              <Info size={16} className="mt-0.5 text-blue-600" />
              <div className="text-sm text-gray-600">
                <p className="font-medium mb-1">Group Discount Tiers:</p>
                <ul className="space-y-1">
                  <li>• 3-4 people: 10% off</li>
                  <li>• 5-9 people: 15% off</li>
                  <li>• 10+ people: 20% off</li>
                </ul>
              </div>
            </div>
          </Card>

          {/* Special Requests */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Special Requests</h2>
            <Textarea
              value={specialRequests}
              onChange={(e) => setSpecialRequests(e.target.value)}
              placeholder="Any special requests or notes for your group booking..."
              rows={4}
            />
          </Card>

          {/* Submit */}
          <div className="flex gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate("/public")}
              className="flex-1"
              disabled={createBooking.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createBooking.isPending}
              className="flex-1"
            >
              {createBooking.isPending
                ? "Submitting..."
                : "Submit Group Booking"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
