import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";

interface FamilyMember {
  id: string;
  name: string;
  relationship: string;
}

interface FamilyBookingFlowProps {
  familyId: string;
  onSuccess?: (bookingId: string) => void;
  onCancel?: () => void;
}

export function FamilyBookingFlow({
  familyId,
  onSuccess,
  onCancel,
}: FamilyBookingFlowProps) {
  const { toast } = useToast();
  const [step, setStep] = useState<"members" | "services" | "payment" | "review">(
    "members"
  );
  const [selectedMembers, setSelectedMembers] = useState<string[]>([]);
  const [memberServices, setMemberServices] = useState<
    Record<string, { serviceId: string; stylistId: string; date: string; time: string }>
  >({});
  const [deferredPayment, setDeferredPayment] = useState(false);
  const [creditLimit, setCreditLimit] = useState(0);

  const { data: familyData } = useQuery({
    queryKey: ["family-account", familyId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/family-accounts/${familyId}`);
      return response.data;
    },
  });

  const { data: services } = useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const response = await apiClient.get("/api/services?is_active=true");
      return response.data;
    },
  });

  const createBookingMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/api/family-accounts/bookings", {
        family_id: familyId,
        member_bookings: selectedMembers.map((memberId) => ({
          member_id: memberId,
          ...memberServices[memberId],
        })),
        deferred_payment: deferredPayment,
        credit_limit: deferredPayment ? creditLimit : 0,
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast("Family bookings created successfully!", "success");
      onSuccess?.(data.booking_id);
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to create family bookings",
        "error"
      );
    },
  });

  const members = familyData?.members || [];
  const totalPrice = selectedMembers.reduce((sum, memberId) => {
    const service = services?.find(
      (s: any) => s.id === memberServices[memberId]?.serviceId
    );
    return sum + (service?.price || 0);
  }, 0);

  const handleMemberToggle = (memberId: string) => {
    setSelectedMembers((prev) =>
      prev.includes(memberId)
        ? prev.filter((id) => id !== memberId)
        : [...prev, memberId]
    );
  };

  const handleMemberServiceChange = (
    memberId: string,
    field: string,
    value: string
  ) => {
    setMemberServices((prev) => ({
      ...prev,
      [memberId]: {
        ...prev[memberId],
        [field]: value,
      },
    }));
  };

  const handleSubmit = async () => {
    if (selectedMembers.length === 0) {
      toast("Please select at least one family member", "error");
      return;
    }

    for (const memberId of selectedMembers) {
      const booking = memberServices[memberId];
      if (!booking?.serviceId || !booking?.date || !booking?.time) {
        toast("Please complete booking details for all selected members", "error");
        return;
      }
    }

    await createBookingMutation.mutateAsync();
  };

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <div className="flex gap-2">
        {["members", "services", "payment", "review"].map((s, idx) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === s
                  ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                  : ["members", "services", "payment", "review"].indexOf(step) > idx
                  ? "bg-[var(--accent)] text-[var(--accent-foreground)]"
                  : "bg-[var(--muted)] text-[var(--muted-foreground)]"
              }`}
            >
              {idx + 1}
            </div>
            {idx < 3 && (
              <div
                className={`w-8 h-1 mx-1 ${
                  ["members", "services", "payment", "review"].indexOf(step) > idx
                    ? "bg-[var(--accent)]"
                    : "bg-[var(--muted)]"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Select Members */}
      {step === "members" && (
        <Card>
          <CardHeader>
            <CardTitle>Select Family Members</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {members.map((member: FamilyMember) => (
                <div key={member.id} className="flex items-center gap-3 p-3 border border-[var(--border)] rounded-lg">
                  <Checkbox
                    checked={selectedMembers.includes(member.id)}
                    onCheckedChange={() => handleMemberToggle(member.id)}
                  />
                  <div className="flex-1">
                    <p className="font-medium text-[var(--foreground)]">
                      {member.name}
                    </p>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      {member.relationship}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2 pt-4">
              <Button onClick={onCancel} variant="outline" className="flex-1">
                Cancel
              </Button>
              <Button
                onClick={() => setStep("services")}
                className="flex-1"
                disabled={selectedMembers.length === 0}
              >
                Next: Select Services
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Select Services */}
      {step === "services" && (
        <Card>
          <CardHeader>
            <CardTitle>Select Services for Each Member</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {selectedMembers.map((memberId) => {
              const member = members.find((m: FamilyMember) => m.id === memberId);
              return (
                <div key={memberId} className="p-4 border border-[var(--border)] rounded-lg space-y-3">
                  <h4 className="font-semibold text-[var(--foreground)]">
                    {member?.name}
                  </h4>

                  <div>
                    <Label>Service</Label>
                    <select
                      value={memberServices[memberId]?.serviceId || ""}
                      onChange={(e) =>
                        handleMemberServiceChange(memberId, "serviceId", e.target.value)
                      }
                      className="w-full mt-1 p-2 border border-[var(--border)] rounded"
                    >
                      <option value="">Select a service</option>
                      {services?.map((service: any) => (
                        <option key={service.id} value={service.id}>
                          {service.name} - ₦{service.price.toLocaleString()}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <Label>Date</Label>
                    <Input
                      type="date"
                      value={memberServices[memberId]?.date || ""}
                      onChange={(e) =>
                        handleMemberServiceChange(memberId, "date", e.target.value)
                      }
                      min={new Date().toISOString().split("T")[0]}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label>Time</Label>
                    <Input
                      type="time"
                      value={memberServices[memberId]?.time || ""}
                      onChange={(e) =>
                        handleMemberServiceChange(memberId, "time", e.target.value)
                      }
                      className="mt-1"
                    />
                  </div>
                </div>
              );
            })}

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep("members")}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={() => setStep("payment")}
                className="flex-1"
              >
                Next: Payment Options
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Payment Options */}
      {step === "payment" && (
        <Card>
          <CardHeader>
            <CardTitle>Payment Options</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-semibold text-blue-900 mb-2">
                Total Amount: ₦{totalPrice.toLocaleString()}
              </p>
              <p className="text-sm text-blue-800">
                {selectedMembers.length} member{selectedMembers.length !== 1 ? "s" : ""} • {selectedMembers.length} service{selectedMembers.length !== 1 ? "s" : ""}
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 border border-[var(--border)] rounded-lg">
                <Checkbox
                  checked={deferredPayment}
                  onCheckedChange={(checked) => setDeferredPayment(checked as boolean)}
                />
                <div className="flex-1">
                  <p className="font-medium text-[var(--foreground)]">
                    Deferred Payment
                  </p>
                  <p className="text-sm text-[var(--muted-foreground)]">
                    Pay for all bookings later
                  </p>
                </div>
              </div>

              {deferredPayment && (
                <div>
                  <Label>Credit Limit (₦)</Label>
                  <Input
                    type="number"
                    value={creditLimit}
                    onChange={(e) => setCreditLimit(Number(e.target.value))}
                    placeholder="Set credit limit"
                    className="mt-1"
                    min={totalPrice}
                  />
                  <p className="text-xs text-[var(--muted-foreground)] mt-1">
                    Minimum: ₦{totalPrice.toLocaleString()}
                  </p>
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep("services")}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={() => setStep("review")}
                className="flex-1"
              >
                Review Bookings
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Review */}
      {step === "review" && (
        <Card>
          <CardHeader>
            <CardTitle>Review Family Bookings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {selectedMembers.map((memberId) => {
                const member = members.find((m: FamilyMember) => m.id === memberId);
                const booking = memberServices[memberId];
                const service = services?.find((s: any) => s.id === booking?.serviceId);

                return (
                  <div key={memberId} className="p-3 bg-[var(--muted)] rounded-lg">
                    <p className="font-medium text-[var(--foreground)]">
                      {member?.name}
                    </p>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      {service?.name} • {booking?.date} at {booking?.time}
                    </p>
                    <p className="text-sm font-semibold text-[var(--primary)] mt-1">
                      ₦{service?.price.toLocaleString()}
                    </p>
                  </div>
                );
              })}
            </div>

            <div className="border-t border-[var(--border)] pt-4">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-[var(--foreground)]">
                  Total:
                </span>
                <span className="text-2xl font-bold text-[var(--primary)]">
                  ₦{totalPrice.toLocaleString()}
                </span>
              </div>
              {deferredPayment && (
                <p className="text-sm text-[var(--muted-foreground)] mt-2">
                  Payment deferred • Credit limit: ₦{creditLimit.toLocaleString()}
                </p>
              )}
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep("payment")}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={handleSubmit}
                className="flex-1"
                disabled={createBookingMutation.isPending}
              >
                {createBookingMutation.isPending ? "Creating..." : "Confirm Bookings"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
