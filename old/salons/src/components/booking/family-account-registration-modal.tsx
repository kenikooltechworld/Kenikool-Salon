import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { apiClient } from "@/lib/api/client";

interface FamilyAccountRegistrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function FamilyAccountRegistrationModal({
  isOpen,
  onClose,
  onSuccess,
}: FamilyAccountRegistrationModalProps) {
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    account_name: "",
    primary_contact_name: "",
    primary_contact_phone: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await apiClient.post("/api/family-accounts", formData);
      addToast({
        title: "Success",
        description: "Family account registered successfully",
        variant: "success",
      });
      setFormData({
        account_name: "",
        primary_contact_name: "",
        primary_contact_phone: "",
      });
      onSuccess?.();
      onClose();
    } catch (error: any) {
      addToast({
        title: "Error",
        description:
          error?.response?.data?.detail || "Failed to register family account",
        variant: "error",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Register Family Account</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Account Name</label>
            <Input
              type="text"
              placeholder="e.g., Smith Family"
              value={formData.account_name}
              onChange={(e) =>
                setFormData({ ...formData, account_name: e.target.value })
              }
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium">Primary Contact Name</label>
            <Input
              type="text"
              placeholder="Contact person name"
              value={formData.primary_contact_name}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  primary_contact_name: e.target.value,
                })
              }
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium">Primary Contact Phone</label>
            <Input
              type="tel"
              placeholder="Phone number"
              value={formData.primary_contact_phone}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  primary_contact_phone: e.target.value,
                })
              }
              required
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Registering..." : "Register"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
