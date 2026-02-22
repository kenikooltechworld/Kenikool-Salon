import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { Badge } from "@/components/ui/badge";
import { AlertTriangleIcon } from "@/components/icons";
import { useCreateClient, useUpdateClient } from "@/lib/api/hooks/useClients";
import { useGetClientSubscriptions } from "@/lib/api/hooks/useMemberships";

interface ClientFormData {
  name: string;
  phone: string;
  email: string;
  notes: string;
  birthday?: string;
  segment?: string;
  tags?: string[];
}

interface ClientFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  client?: {
    id: string;
    name: string;
    phone: string;
    email?: string;
    notes?: string;
    birthday?: string;
    segment?: string;
    tags?: string[];
  };
}

export function ClientFormModal({
  isOpen,
  onClose,
  onSuccess,
  client,
}: ClientFormModalProps) {
  const isEdit = !!client;

  // Fetch client subscriptions if editing
  const { data: subscriptions = [] } = useGetClientSubscriptions(
    isEdit && client ? client.id : ""
  );

  // Initialize form data based on client prop
  const getInitialFormData = (): ClientFormData => ({
    name: client?.name || "",
    phone: client?.phone || "",
    email: client?.email || "",
    notes: client?.notes || "",
    birthday: client?.birthday || "",
    segment: client?.segment || "",
    tags: client?.tags || [],
  });

  const [formData, setFormData] = useState<ClientFormData>(
    getInitialFormData()
  );

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Reset form when modal opens/closes or client changes
  useEffect(() => {
    if (isOpen) {
      setFormData(getInitialFormData());
      setErrors({});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, client?.id]); // Only reset when modal opens or client changes

  const createClientMutation = useCreateClient({
    onSuccess: () => {
      onSuccess();
      onClose();
    },
    onError: (error) => {
      setErrors({ submit: error.message });
    },
  });

  const updateClientMutation = useUpdateClient(client?.id || "", {
    onSuccess: () => {
      onSuccess();
      onClose();
    },
    onError: (error) => {
      setErrors({ submit: error.message });
    },
  });

  const loading =
    createClientMutation.isPending || updateClientMutation.isPending;

  const handleChange = (field: keyof ClientFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Client name is required";
    }
    if (!formData.phone.trim()) {
      newErrors.phone = "Phone number is required";
    }
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Invalid email address";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    const input = {
      name: formData.name,
      phone: formData.phone,
      email: formData.email || undefined,
      notes: formData.notes || undefined,
      birthday: formData.birthday || undefined,
      segment: formData.segment || undefined,
      tags: formData.tags || undefined,
    };

    if (isEdit && client) {
      updateClientMutation.mutate(input);
    } else {
      createClientMutation.mutate(input);
    }
  };

  const activeSubscription = subscriptions.find(
    (sub) => sub.status === "active" || sub.status === "trial"
  );

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">
            {isEdit ? "Edit Client" : "Add Client"}
          </h2>
          {activeSubscription && (
            <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
              ✓ Member
            </Badge>
          )}
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.submit && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm">{errors.submit}</p>
              </div>
            </Alert>
          )}

          {/* Client Name */}
          <div>
            <Label htmlFor="name">Full Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleChange("name", e.target.value)}
              placeholder="e.g., John Doe"
              error={!!errors.name}
            />
            {errors.name && (
              <p className="text-sm text-error mt-1">{errors.name}</p>
            )}
          </div>

          {/* Phone */}
          <div>
            <Label htmlFor="phone">Phone Number *</Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => handleChange("phone", e.target.value)}
              placeholder="e.g., +234 800 000 0000"
              error={!!errors.phone}
            />
            {errors.phone && (
              <p className="text-sm text-error mt-1">{errors.phone}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange("email", e.target.value)}
              placeholder="e.g., john@example.com"
              error={!!errors.email}
            />
            {errors.email && (
              <p className="text-sm text-error mt-1">{errors.email}</p>
            )}
          </div>

          {/* Notes */}
          <div>
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              placeholder="Add any notes about this client..."
              rows={3}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? (
                <>
                  <Spinner size="sm" />
                  {isEdit ? "Updating..." : "Creating..."}
                </>
              ) : (
                <>{isEdit ? "Update Client" : "Create Client"}</>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
