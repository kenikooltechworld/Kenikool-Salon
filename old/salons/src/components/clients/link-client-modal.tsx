import { useState, useMemo } from "react";
import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckCircleIcon, AlertTriangleIcon, SearchIcon } from "@/components/icons";
import { useClients, useLinkClient } from "@/lib/api/hooks/useClients";

interface LinkClientModalProps {
  isOpen: boolean;
  clientId: string;
  onClose: () => void;
}

export function LinkClientModal({
  isOpen,
  clientId,
  onClose,
}: LinkClientModalProps) {
  const { data: clientsData } = useClients({ limit: 1000 });
  const linkClient = useLinkClient(clientId);

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedClientId, setSelectedClientId] = useState("");
  const [relationshipType, setRelationshipType] = useState<
    "family" | "friend" | "referral"
  >("family");
  const [notes, setNotes] = useState("");

  // Filter clients based on search term
  const filteredClients = useMemo(() => {
    if (!clientsData?.items) return [];

    return clientsData.items
      .filter((c: any) => c.id !== clientId) // Exclude current client
      .filter((c: any) =>
        searchTerm === ""
          ? true
          : c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            c.phone.includes(searchTerm) ||
            (c.email && c.email.includes(searchTerm))
      );
  }, [clientsData, searchTerm, clientId]);

  const handleSubmit = async () => {
    if (!selectedClientId) {
      alert("Please select a client to link");
      return;
    }

    try {
      await linkClient.mutateAsync({
        related_client_id: selectedClientId,
        relationship_type: relationshipType,
        notes: notes || undefined,
      });

      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      console.error("Failed to link client:", error);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center">
        <div className="bg-background rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-background border-b border-border p-6 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">
              Link Client
            </h2>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            {/* Success Message */}
            {linkClient.isSuccess && (
              <Alert variant="success">
                <CheckCircleIcon size={20} />
                <div>
                  <h3 className="font-semibold">Client Linked Successfully</h3>
                  <p className="text-sm">
                    The relationship has been created and saved.
                  </p>
                </div>
              </Alert>
            )}

            {/* Error Message */}
            {linkClient.isError && (
              <Alert variant="error">
                <AlertTriangleIcon size={20} />
                <div>
                  <h3 className="font-semibold">Error Linking Client</h3>
                  <p className="text-sm">
                    {linkClient.error?.message || "Failed to link client"}
                  </p>
                </div>
              </Alert>
            )}

            {!linkClient.isSuccess && (
              <>
                {/* Search Clients */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Search Client
                  </label>
                  <div className="relative">
                    <SearchIcon
                      size={18}
                      className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
                    />
                    <Input
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search by name, phone, or email..."
                      className="pl-10"
                      disabled={linkClient.isPending}
                    />
                  </div>
                </div>

                {/* Client Selection */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Select Client
                  </label>
                  <div className="border border-border rounded-lg max-h-48 overflow-y-auto">
                    {filteredClients.length > 0 ? (
                      <div className="divide-y divide-border">
                        {filteredClients.map((client: any) => (
                          <label
                            key={client.id}
                            className="flex items-center gap-3 p-3 hover:bg-muted/50 cursor-pointer"
                          >
                            <input
                              type="radio"
                              name="client"
                              value={client.id}
                              checked={selectedClientId === client.id}
                              onChange={(e) =>
                                setSelectedClientId(e.target.value)
                              }
                              disabled={linkClient.isPending}
                            />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-foreground">
                                {client.name}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {client.phone}
                              </p>
                            </div>
                          </label>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-center text-sm text-muted-foreground">
                        {searchTerm
                          ? "No clients found"
                          : "Start typing to search"}
                      </div>
                    )}
                  </div>
                </div>

                {/* Relationship Type */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Relationship Type
                  </label>
                  <Select
                    value={relationshipType}
                    onChange={(e) =>
                      setRelationshipType(e.target.value as any)
                    }
                    disabled={linkClient.isPending}
                  >
                    <option value="family">Family</option>
                    <option value="friend">Friend</option>
                    <option value="referral">Referral</option>
                  </Select>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Notes (Optional)
                  </label>
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add any notes about this relationship..."
                    rows={3}
                    disabled={linkClient.isPending}
                  />
                </div>
              </>
            )}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-background border-t border-border p-6 flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={linkClient.isPending}
            >
              {linkClient.isSuccess ? "Close" : "Cancel"}
            </Button>
            {!linkClient.isSuccess && (
              <Button
                onClick={handleSubmit}
                disabled={linkClient.isPending || !selectedClientId}
              >
                {linkClient.isPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Linking...
                  </>
                ) : (
                  "Link Client"
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </Dialog>
  );
}
