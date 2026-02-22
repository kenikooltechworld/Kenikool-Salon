import { useState } from "react";
import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckCircleIcon, AlertTriangleIcon } from "@/components/icons";
import { useAtRiskClients, useCreateWinbackCampaign } from "@/lib/api/hooks/useClients";

interface WinbackCampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function WinbackCampaignModal({
  isOpen,
  onClose,
  onSuccess,
}: WinbackCampaignModalProps) {
  const { data: atRiskData } = useAtRiskClients(90, 0, 1000);
  const createCampaign = useCreateWinbackCampaign();

  const [selectedClientIds, setSelectedClientIds] = useState<string[]>([]);
  const [channel, setChannel] = useState<"sms" | "email" | "whatsapp">("sms");
  const [message, setMessage] = useState("");
  const [offer, setOffer] = useState("");
  const [selectAll, setSelectAll] = useState(false);

  const handleSelectAll = (checked: boolean) => {
    setSelectAll(checked);
    if (checked && atRiskData?.clients) {
      setSelectedClientIds(atRiskData.clients.map((c) => c.id));
    } else {
      setSelectedClientIds([]);
    }
  };

  const handleSelectClient = (clientId: string, checked: boolean) => {
    if (checked) {
      setSelectedClientIds([...selectedClientIds, clientId]);
    } else {
      setSelectedClientIds(selectedClientIds.filter((id) => id !== clientId));
    }
  };

  const handleSubmit = async () => {
    if (selectedClientIds.length === 0) {
      alert("Please select at least one client");
      return;
    }

    if (!message.trim()) {
      alert("Please enter a message");
      return;
    }

    try {
      await createCampaign.mutateAsync({
        client_ids: selectedClientIds,
        message,
        channel,
        offer: offer || undefined,
      });

      onSuccess?.();
    } catch (error) {
      console.error("Failed to create campaign:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
        <div className="bg-background rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-background border-b border-border p-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-foreground">
              Create Win-Back Campaign
            </h2>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Success Message */}
            {createCampaign.isSuccess && (
              <Alert variant="success">
                <CheckCircleIcon size={20} />
                <div>
                  <h3 className="font-semibold">Campaign Created Successfully</h3>
                  <p className="text-sm">
                    Win-back campaign has been created and will be sent to{" "}
                    {selectedClientIds.length} clients.
                  </p>
                </div>
              </Alert>
            )}

            {/* Error Message */}
            {createCampaign.isError && (
              <Alert variant="error">
                <AlertTriangleIcon size={20} />
                <div>
                  <h3 className="font-semibold">Error Creating Campaign</h3>
                  <p className="text-sm">
                    {createCampaign.error?.message || "Failed to create campaign"}
                  </p>
                </div>
              </Alert>
            )}

            {/* Channel Selection */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Communication Channel
              </label>
              <Select
                value={channel}
                onChange={(e) => setChannel(e.target.value as any)}
                disabled={createCampaign.isPending}
              >
                <option value="sms">SMS</option>
                <option value="email">Email</option>
                <option value="whatsapp">WhatsApp</option>
              </Select>
            </div>

            {/* Message */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Message
              </label>
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter your win-back message..."
                rows={4}
                disabled={createCampaign.isPending}
              />
              <p className="text-xs text-muted-foreground mt-1">
                {message.length} characters
              </p>
            </div>

            {/* Offer (Optional) */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Special Offer (Optional)
              </label>
              <Input
                value={offer}
                onChange={(e) => setOffer(e.target.value)}
                placeholder="e.g., 20% off your next visit"
                disabled={createCampaign.isPending}
              />
            </div>

            {/* Client Selection */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-foreground">
                  Select At-Risk Clients
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    disabled={createCampaign.isPending}
                  />
                  <span>Select All</span>
                </label>
              </div>

              <div className="border border-border rounded-lg p-3 max-h-64 overflow-y-auto space-y-2">
                {atRiskData?.clients && atRiskData.clients.length > 0 ? (
                  atRiskData.clients.map((client) => (
                    <label
                      key={client.id}
                      className="flex items-center gap-3 p-2 hover:bg-muted/50 rounded cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedClientIds.includes(client.id)}
                        onChange={(e) =>
                          handleSelectClient(client.id, e.target.checked)
                        }
                        disabled={createCampaign.isPending}
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-foreground">
                          {client.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {client.phone} • {client.days_since_last_visit} days inactive
                        </p>
                      </div>
                    </label>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No at-risk clients found
                  </p>
                )}
              </div>

              <p className="text-sm text-muted-foreground mt-2">
                {selectedClientIds.length} client{selectedClientIds.length !== 1 ? "s" : ""}{" "}
                selected
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-background border-t border-border p-6 flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={createCampaign.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={
                createCampaign.isPending ||
                selectedClientIds.length === 0 ||
                !message.trim()
              }
            >
              {createCampaign.isPending ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Creating...
                </>
              ) : (
                "Create Campaign"
              )}
            </Button>
          </div>
        </div>
      </div>
    </Dialog>
  );
}
