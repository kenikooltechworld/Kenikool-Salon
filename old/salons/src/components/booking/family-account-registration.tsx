import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

interface FamilyMember {
  name: string;
  email: string;
  phone: string;
  relationship: string;
}

interface FamilyAccountRegistrationProps {
  onSuccess?: (familyId: string) => void;
  onCancel?: () => void;
}

export function FamilyAccountRegistration({
  onSuccess,
  onCancel,
}: FamilyAccountRegistrationProps) {
  const { toast } = useToast();
  const [step, setStep] = useState<"primary" | "members" | "review">("primary");
  const [primaryName, setPrimaryName] = useState("");
  const [primaryEmail, setPrimaryEmail] = useState("");
  const [primaryPhone, setPrimaryPhone] = useState("");
  const [members, setMembers] = useState<FamilyMember[]>([]);
  const [currentMember, setCurrentMember] = useState<FamilyMember>({
    name: "",
    email: "",
    phone: "",
    relationship: "",
  });

  const createFamilyMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/api/family-accounts", {
        primary_member: {
          name: primaryName,
          email: primaryEmail,
          phone: primaryPhone,
        },
        family_members: members,
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast("Family account created successfully!", "success");
      onSuccess?.(data.family_id);
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to create family account",
        "error"
      );
    },
  });

  const handleAddMember = () => {
    if (!currentMember.name || !currentMember.relationship) {
      toast("Please fill in name and relationship", "error");
      return;
    }

    setMembers([...members, currentMember]);
    setCurrentMember({ name: "", email: "", phone: "", relationship: "" });
  };

  const handleRemoveMember = (index: number) => {
    setMembers(members.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!primaryName || !primaryEmail || !primaryPhone) {
      toast("Please fill in primary member information", "error");
      return;
    }

    await createFamilyMutation.mutateAsync();
  };

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <div className="flex gap-2">
        {["primary", "members", "review"].map((s, idx) => (
          <div key={s} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === s
                  ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
                  : ["primary", "members", "review"].indexOf(step) > idx
                  ? "bg-[var(--accent)] text-[var(--accent-foreground)]"
                  : "bg-[var(--muted)] text-[var(--muted-foreground)]"
              }`}
            >
              {idx + 1}
            </div>
            {idx < 2 && (
              <div
                className={`w-8 h-1 mx-1 ${
                  ["primary", "members", "review"].indexOf(step) > idx
                    ? "bg-[var(--accent)]"
                    : "bg-[var(--muted)]"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Primary Member */}
      {step === "primary" && (
        <Card>
          <CardHeader>
            <CardTitle>Primary Member Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-[var(--foreground)]">
                Full Name *
              </label>
              <Input
                value={primaryName}
                onChange={(e) => setPrimaryName(e.target.value)}
                placeholder="Enter your full name"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[var(--foreground)]">
                Email *
              </label>
              <Input
                type="email"
                value={primaryEmail}
                onChange={(e) => setPrimaryEmail(e.target.value)}
                placeholder="Enter your email"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[var(--foreground)]">
                Phone *
              </label>
              <Input
                type="tel"
                value={primaryPhone}
                onChange={(e) => setPrimaryPhone(e.target.value)}
                placeholder="Enter your phone number"
                className="mt-1"
              />
            </div>
            <Button
              onClick={() => setStep("members")}
              className="w-full"
              disabled={!primaryName || !primaryEmail || !primaryPhone}
            >
              Next: Add Family Members
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Add Family Members */}
      {step === "members" && (
        <Card>
          <CardHeader>
            <CardTitle>Add Family Members</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Member Name *
                </label>
                <Input
                  value={currentMember.name}
                  onChange={(e) =>
                    setCurrentMember({ ...currentMember, name: e.target.value })
                  }
                  placeholder="Enter member name"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Relationship *
                </label>
                <Input
                  value={currentMember.relationship}
                  onChange={(e) =>
                    setCurrentMember({
                      ...currentMember,
                      relationship: e.target.value,
                    })
                  }
                  placeholder="e.g., Spouse, Child, Parent"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Email
                </label>
                <Input
                  type="email"
                  value={currentMember.email}
                  onChange={(e) =>
                    setCurrentMember({ ...currentMember, email: e.target.value })
                  }
                  placeholder="Enter member email (optional)"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-[var(--foreground)]">
                  Phone
                </label>
                <Input
                  type="tel"
                  value={currentMember.phone}
                  onChange={(e) =>
                    setCurrentMember({ ...currentMember, phone: e.target.value })
                  }
                  placeholder="Enter member phone (optional)"
                  className="mt-1"
                />
              </div>
              <Button
                onClick={handleAddMember}
                variant="secondary"
                className="w-full"
              >
                Add Member
              </Button>
            </div>

            {/* Added Members List */}
            {members.length > 0 && (
              <div className="space-y-2 pt-4 border-t border-[var(--border)]">
                <h4 className="font-medium text-[var(--foreground)]">
                  Family Members ({members.length})
                </h4>
                <div className="space-y-2">
                  {members.map((member, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 bg-[var(--muted)] rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-[var(--foreground)]">
                          {member.name}
                        </p>
                        <p className="text-sm text-[var(--muted-foreground)]">
                          {member.relationship}
                        </p>
                      </div>
                      <button
                        onClick={() => handleRemoveMember(idx)}
                        className="text-[var(--destructive)] hover:bg-[var(--destructive)]/10 p-1 rounded"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep("primary")}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={() => setStep("review")}
                className="flex-1"
              >
                Review
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Review */}
      {step === "review" && (
        <Card>
          <CardHeader>
            <CardTitle>Review Family Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <p className="text-sm text-[var(--muted-foreground)]">
                  Primary Member
                </p>
                <p className="font-medium text-[var(--foreground)]">
                  {primaryName}
                </p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {primaryEmail} • {primaryPhone}
                </p>
              </div>
            </div>

            {members.length > 0 && (
              <div className="border-t border-[var(--border)] pt-4">
                <p className="text-sm font-medium text-[var(--foreground)] mb-2">
                  Family Members ({members.length})
                </p>
                <div className="space-y-2">
                  {members.map((member, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2 bg-[var(--muted)] rounded"
                    >
                      <div>
                        <p className="text-sm font-medium text-[var(--foreground)]">
                          {member.name}
                        </p>
                        <p className="text-xs text-[var(--muted-foreground)]">
                          {member.relationship}
                        </p>
                      </div>
                      <Badge variant="secondary">{member.email || "N/A"}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep("members")}
                variant="outline"
                className="flex-1"
              >
                Back
              </Button>
              <Button
                onClick={handleSubmit}
                className="flex-1"
                disabled={createFamilyMutation.isPending}
              >
                {createFamilyMutation.isPending ? "Creating..." : "Create Account"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cancel Button */}
      {onCancel && (
        <Button onClick={onCancel} variant="ghost" className="w-full">
          Cancel
        </Button>
      )}
    </div>
  );
}
