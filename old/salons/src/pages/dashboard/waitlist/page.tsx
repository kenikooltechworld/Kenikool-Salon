import { useState } from "react";
import {
  useWaitlistEntries,
  useBulkDeleteWaitlist,
  useBulkNotifyWaitlist,
} from "@/lib/api/hooks/useWaitlist";
import { WaitlistAdminList, WaitlistStatusModal } from "@/components/waitlist";
import { ClockIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { showToast } from "@/lib/utils/toast";

export default function WaitlistPage() {
  const { data: entries = [], isLoading } = useWaitlistEntries();
  const deleteMutation = useBulkDeleteWaitlist();
  const notifyMutation = useBulkNotifyWaitlist();
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);

  const handleUpdateStatus = (entry: any) => {
    setSelectedEntry(entry);
    setIsStatusModalOpen(true);
  };

  const handleNotify = async (id: string) => {
    try {
      await notifyMutation.mutateAsync(id);
      showToast("Client notified successfully", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to notify client",
        "error"
      );
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this waitlist entry?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      showToast("Waitlist entry removed successfully", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to remove entry",
        "error"
      );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <ClockIcon size={32} className="text-[var(--primary)]" />
          Waitlist
        </h1>
        <p className="text-[var(--muted-foreground)] mt-1">
          Manage client waitlist and availability notifications
        </p>
      </div>

      <Card className="p-6">
        <WaitlistAdminList
          entries={entries}
          onUpdateStatus={handleUpdateStatus}
          onNotify={handleNotify}
          onDelete={handleDelete}
        />
      </Card>

      <WaitlistStatusModal
        isOpen={isStatusModalOpen}
        onClose={() => {
          setIsStatusModalOpen(false);
          setSelectedEntry(null);
        }}
        entry={selectedEntry}
      />
    </div>
  );
}
