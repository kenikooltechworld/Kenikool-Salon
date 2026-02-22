import React, { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NoShowPolicyEnforcerProps {
  customerId: string;
  noShowCount: number;
  onPolicyApply: (policy: string) => Promise<void>;
  loading?: boolean;
}

const POLICIES = [
  {
    id: "require-payment",
    name: "Require Advance Payment",
    description: "Customer must pay upfront for all future bookings",
  },
  {
    id: "require-confirmation",
    name: "Require Confirmation",
    description: "Customer must confirm booking 24 hours before appointment",
  },
  {
    id: "deposit",
    name: "Require Deposit",
    description: "Customer must pay a deposit for future bookings",
  },
  {
    id: "restrict-booking",
    name: "Restrict Booking",
    description: "Limit customer to one booking at a time",
  },
];

export const NoShowPolicyEnforcer: React.FC<NoShowPolicyEnforcerProps> = ({
  customerId,
  noShowCount,
  onPolicyApply,
  loading = false,
}) => {
  const [selectedPolicy, setSelectedPolicy] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (noShowCount < 2) {
    return null;
  }

  const handleApplyPolicy = async () => {
    if (!selectedPolicy) return;

    setApplying(true);
    setError(null);

    try {
      await onPolicyApply(selectedPolicy);
      setSelectedPolicy(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to apply policy");
    } finally {
      setApplying(false);
    }
  };

  return (
    <div className="space-y-3 rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-2">
        <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-medium text-red-900">Apply No-Show Policy</h3>
          <p className="text-sm text-red-800 mt-1">
            This customer has {noShowCount} no-shows. Consider applying a
            policy.
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {POLICIES.map((policy) => (
          <label
            key={policy.id}
            className="flex items-start gap-3 p-2 rounded hover:bg-red-100 cursor-pointer"
          >
            <input
              type="radio"
              name="policy"
              value={policy.id}
              checked={selectedPolicy === policy.id}
              onChange={(e) => setSelectedPolicy(e.target.value)}
              disabled={applying || loading}
              className="mt-1"
            />
            <div className="flex-1">
              <p className="font-medium text-sm text-red-900">{policy.name}</p>
              <p className="text-xs text-red-800">{policy.description}</p>
            </div>
          </label>
        ))}
      </div>

      {error && (
        <div className="text-sm text-red-900 bg-red-100 rounded p-2">
          {error}
        </div>
      )}

      <Button
        onClick={handleApplyPolicy}
        disabled={!selectedPolicy || applying || loading}
        className="w-full"
      >
        {applying ? "Applying..." : "Apply Policy"}
      </Button>
    </div>
  );
};
