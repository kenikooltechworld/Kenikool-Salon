import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface Supplier {
  _id?: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  contact_person?: string;
  payment_terms?: string;
}

interface SupplierFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  supplier?: Supplier | null;
}

export function SupplierFormModal({
  isOpen,
  onClose,
  supplier,
}: SupplierFormModalProps) {
  const { toast } = useToast();
  const [formData, setFormData] = useState<Supplier>({
    name: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    country: "",
    contact_person: "",
    payment_terms: "",
  });

  useEffect(() => {
    if (supplier) {
      setFormData(supplier);
    } else {
      setFormData({
        name: "",
        email: "",
        phone: "",
        address: "",
        city: "",
        country: "",
        contact_person: "",
        payment_terms: "",
      });
    }
  }, [supplier, isOpen]);

  const createMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post("/api/inventory/suppliers", formData);
      return res.data;
    },
    onSuccess: () => {
      toast("Supplier created successfully", "success");
      onClose();
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to create supplier",
        "error"
      );
    },
  });

  const updateMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.patch(
        `/api/inventory/suppliers/${supplier?._id}`,
        formData
      );
      return res.data;
    },
    onSuccess: () => {
      toast("Supplier updated successfully", "success");
      onClose();
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to update supplier",
        "error"
      );
    },
  });

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      toast("Supplier name is required", "error");
      return;
    }

    if (supplier?._id) {
      await updateMutation.mutateAsync();
    } else {
      await createMutation.mutateAsync();
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>
          {supplier ? "Edit Supplier" : "Add New Supplier"}
        </ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-4">
        <div>
          <Label required>Supplier Name</Label>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Enter supplier name"
            className="mt-1"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>Email</Label>
            <Input
              type="email"
              value={formData.email || ""}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="supplier@example.com"
              className="mt-1"
            />
          </div>
          <div>
            <Label>Phone</Label>
            <Input
              type="tel"
              value={formData.phone || ""}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+1-555-0123"
              className="mt-1"
            />
          </div>
        </div>

        <div>
          <Label>Contact Person</Label>
          <Input
            value={formData.contact_person || ""}
            onChange={(e) =>
              setFormData({ ...formData, contact_person: e.target.value })
            }
            placeholder="John Doe"
            className="mt-1"
          />
        </div>

        <div>
          <Label>Address</Label>
          <Input
            value={formData.address || ""}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            placeholder="123 Supply Street"
            className="mt-1"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>City</Label>
            <Input
              value={formData.city || ""}
              onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              placeholder="New York"
              className="mt-1"
            />
          </div>
          <div>
            <Label>Country</Label>
            <Input
              value={formData.country || ""}
              onChange={(e) => setFormData({ ...formData, country: e.target.value })}
              placeholder="USA"
              className="mt-1"
            />
          </div>
        </div>

        <div>
          <Label>Payment Terms</Label>
          <Input
            value={formData.payment_terms || ""}
            onChange={(e) =>
              setFormData({ ...formData, payment_terms: e.target.value })
            }
            placeholder="e.g., Net 30"
            className="mt-1"
          />
        </div>
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={
            createMutation.isPending || updateMutation.isPending
          }
        >
          {createMutation.isPending || updateMutation.isPending
            ? "Saving..."
            : "Save Supplier"}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
