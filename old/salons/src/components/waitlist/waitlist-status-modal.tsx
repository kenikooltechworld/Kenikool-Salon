"use client";

import { useState, useEffect } from "react";
import { useUpdateWaitlistEntry } from "@/lib/api/hooks/useWaitlist";
import { Modal } from "@/components/ui/modal";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { showToast } from "@/lib/utils/toast";

interface WaitlistEntry {
  _id: string;
  client_name: string;
  status: string;
}

interface WaitlistStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  entry: WaitlistEntry | null;
}

const STATUSES = [
  { value: "waiting", label: "Waiting" },
  { value: "notified", label: "Notified" },
  { value: "booked", label: "Booked" },
  { value: "cancelled", label: "Cancelled" },
];

export function WaitlistStatusModal({
  isOpen,
  onClose,
  entry,
}: WaitlistStatusModalProps) {
  const updateMutation = useUpdateWaitlistEntry();
  const [status, setStatus] = useState("waiting");

  useEffect(() => {
    if (entry) {
      setStatus(entry.status);
    }
  }, [entry, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!entry) return;

    try {
      await updateMutation.mutateAsync({
        id: entry._id,
        data: { status },
      });
      showToast("Status updated successfully", "success");
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to update status",
        "error"
      );
    }
  };

  if (!entry) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Update Status - ${entry.client_name}`}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <Label htmlFor="status">Status *</Label>
          <Select id="status" value={status} onValueChange={setStatus} required>
            {STATUSES.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </Select>
        </div>

        <div className="flex gap-3 pt-4 border-t border-[var(--border)]">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={updateMutation.isPending}
            className="flex-1"
          >
            {updateMutation.isPending ? "Updating..." : "Update Status"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
