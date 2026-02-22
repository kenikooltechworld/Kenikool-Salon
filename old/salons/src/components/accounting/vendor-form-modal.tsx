import { useState, useEffect } from "react";
import {
  VendorCreate,
  VendorUpdate,
  useCreateVendor,
  useUpdateVendor,
  Vendor,
} from "@/lib/api/hooks/useAccounting";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { showToast } from "@/lib/utils/toast";

interface VendorFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  vendor?: Vendor; // Optional vendor for editing
}

export function VendorFormModal({ isOpen, onClose, vendor }: VendorFormModalProps) {
  const createMutation = useCreateVendor();
  const updateMutation = useUpdateVendor();
  
  const isEditing = !!vendor;
  
  const [formData, setFormData] = useState<VendorCreate | VendorUpdate>({
    name: "",
    contact_person: "",
    email: "",
    phone: "",
    address: "",
    tax_id: "",
    payment_terms: "",
    notes: "",
  });

  // Initialize form data when editing
  useEffect(() => {
    if (vendor && isOpen) {
      setFormData({
        name: vendor.name,
        contact_person: vendor.contact_person || "",
        email: vendor.email || "",
        phone: vendor.phone || "",
        address: vendor.address || "",
        tax_id: vendor.tax_id || "",
        payment_terms: vendor.payment_terms || "",
        notes: vendor.notes || "",
        status: vendor.status,
      });
    } else if (!isEditing && isOpen) {
      resetForm();
    }
  }, [vendor, isOpen, isEditing]);

  const resetForm = () => {
    setFormData({
      name: "",
      contact_person: "",
      email: "",
      phone: "",
      address: "",
      tax_id: "",
      payment_terms: "",
      notes: "",
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditing && vendor) {
        await updateMutation.mutateAsync({ 
          id: vendor.id, 
          data: formData as VendorUpdate 
        });
        showToast("Vendor updated successfully", "success");
      } else {
        await createMutation.mutateAsync(formData as VendorCreate);
        showToast("Vendor created successfully", "success");
      }
      resetForm();
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} vendor`,
        "error"
      );
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? "Edit Vendor" : "Create Vendor"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Vendor Name *</Label>
          <Input
            id="name"
            value={formData.name || ""}
            onChange={(e) =>
              setFormData({ ...formData, name: e.target.value })
            }
            placeholder="Vendor name"
            required
          />
        </div>

        <div>
          <Label htmlFor="contact_person">Contact Person</Label>
          <Input
            id="contact_person"
            value={formData.contact_person || ""}
            onChange={(e) =>
              setFormData({ ...formData, contact_person: e.target.value })
            }
            placeholder="Contact person name"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email || ""}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="vendor@example.com"
            />
          </div>
          <div>
            <Label htmlFor="phone">Phone</Label>
            <Input
              id="phone"
              value={formData.phone || ""}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
              placeholder="Phone number"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="address">Address</Label>
          <Input
            id="address"
            value={formData.address || ""}
            onChange={(e) =>
              setFormData({ ...formData, address: e.target.value })
            }
            placeholder="Business address"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="tax_id">Tax ID</Label>
            <Input
              id="tax_id"
              value={formData.tax_id || ""}
              onChange={(e) =>
                setFormData({ ...formData, tax_id: e.target.value })
              }
              placeholder="Tax identification number"
            />
          </div>
          <div>
            <Label htmlFor="payment_terms">Payment Terms</Label>
            <Input
              id="payment_terms"
              value={formData.payment_terms || ""}
              onChange={(e) =>
                setFormData({ ...formData, payment_terms: e.target.value })
              }
              placeholder="e.g., Net 30"
            />
          </div>
        </div>

        {isEditing && (
          <div>
            <Label htmlFor="status">Status</Label>
            <Select
              value={(formData as VendorUpdate).status || "active"}
              onValueChange={(value) =>
                setFormData({ ...formData, status: value as "active" | "inactive" | "suspended" })
              }
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
            </Select>
          </div>
        )}

        <div>
          <Label htmlFor="notes">Notes</Label>
          <Input
            id="notes"
            value={formData.notes || ""}
            onChange={(e) =>
              setFormData({ ...formData, notes: e.target.value })
            }
            placeholder="Additional notes"
          />
        </div>

        <div className="flex gap-3 pt-4">
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
            className="flex-1"
            disabled={createMutation.isPending || updateMutation.isPending}
          >
            {isEditing ? 'Update Vendor' : 'Create Vendor'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}