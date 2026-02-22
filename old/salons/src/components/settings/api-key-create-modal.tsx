import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

interface APIKeyCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    expires_at?: string;
    permissions?: string[];
  }) => void;
  isLoading: boolean;
}

const AVAILABLE_PERMISSIONS = [
  { id: "read:bookings", label: "Read Bookings" },
  { id: "write:bookings", label: "Write Bookings" },
  { id: "read:clients", label: "Read Clients" },
  { id: "write:clients", label: "Write Clients" },
  { id: "read:payments", label: "Read Payments" },
  { id: "write:payments", label: "Write Payments" },
  { id: "read:analytics", label: "Read Analytics" },
];

export function APIKeyCreateModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}: APIKeyCreateModalProps) {
  const { showToast } = useToast();
  const [name, setName] = useState("");
  const [expiresAt, setExpiresAt] = useState("");
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      showToast({
        title: "Validation Error",
        description: "API key name is required",
        variant: "destructive",
      });
      return;
    }

    onSubmit({
      name: name.trim(),
      expires_at: expiresAt || undefined,
      permissions:
        selectedPermissions.length > 0 ? selectedPermissions : undefined,
    });

    // Reset form
    setName("");
    setExpiresAt("");
    setSelectedPermissions([]);
  };

  const togglePermission = (permissionId: string) => {
    setSelectedPermissions((prev) =>
      prev.includes(permissionId)
        ? prev.filter((p) => p !== permissionId)
        : [...prev, permissionId],
    );
  };

  // Calculate minimum date (today)
  const today = new Date().toISOString().split("T")[0];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create API Key">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name */}
        <div>
          <Label htmlFor="name">API Key Name *</Label>
          <Input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Mobile App Integration"
            disabled={isLoading}
          />
        </div>

        {/* Expiration Date */}
        <div>
          <Label htmlFor="expires_at">Expiration Date (Optional)</Label>
          <Input
            id="expires_at"
            type="date"
            value={expiresAt}
            onChange={(e) => setExpiresAt(e.target.value)}
            min={today}
            disabled={isLoading}
          />
          <p className="text-xs text-muted-foreground mt-1">
            Leave empty for no expiration
          </p>
        </div>

        {/* Permissions */}
        <div>
          <Label>Permissions (Optional)</Label>
          <div className="space-y-2 mt-2">
            {AVAILABLE_PERMISSIONS.map((permission) => (
              <div key={permission.id} className="flex items-center gap-2">
                <Checkbox
                  id={permission.id}
                  checked={selectedPermissions.includes(permission.id)}
                  onChange={() => togglePermission(permission.id)}
                  disabled={isLoading}
                />
                <Label
                  htmlFor={permission.id}
                  className="font-normal cursor-pointer"
                >
                  {permission.label}
                </Label>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Leave empty for full access
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading} className="flex-1">
            {isLoading ? (
              <>
                <Spinner size="sm" />
                Creating...
              </>
            ) : (
              "Create API Key"
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
