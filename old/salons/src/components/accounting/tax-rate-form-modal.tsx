import { useState, useEffect } from "react";
import {
  TaxRate,
  TaxRateCreate,
  TaxRateUpdate,
  useCreateTaxRate,
  useUpdateTaxRate,
} from "@/lib/api/hooks/useAccounting";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { showToast } from "@/lib/utils/toast";

interface TaxRateFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  taxRate?: TaxRate | null;
}

export function TaxRateFormModal({
  isOpen,
  onClose,
  taxRate,
}: TaxRateFormModalProps) {
  const createMutation = useCreateTaxRate();
  const updateMutation = useUpdateTaxRate();
  const [formData, setFormData] = useState<TaxRateCreate>({
    name: "",
    rate: 0,
    description: "",
    active: true,
  });

  useEffect(() => {
    if (taxRate) {
      setFormData({
        name: taxRate.name,
        rate: taxRate.rate,
        description: taxRate.description || "",
        active: taxRate.active,
      });
    } else {
      setFormData({
        name: "",
        rate: 0,
        description: "",
        active: true,
      });
    }
  }, [taxRate, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (taxRate) {
        const updateData: TaxRateUpdate = {
          name: formData.name,
          rate: formData.rate,
          description: formData.description,
          active: formData.active,
        };
        await updateMutation.mutateAsync({ id: taxRate.id, data: updateData });
        showToast("Tax rate updated successfully", "success");
      } else {
        await createMutation.mutateAsync(formData);
        showToast("Tax rate created successfully", "success");
      }
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to save tax rate",
        "error"
      );
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={taxRate ? "Edit Tax Rate" : "Create Tax Rate"}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Tax Rate Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., VAT, Sales Tax"
            required
          />
        </div>

        <div>
          <Label htmlFor="rate">Tax Rate (%)</Label>
          <Input
            id="rate"
            type="number"
            step="0.01"
            min="0"
            max="100"
            value={formData.rate}
            onChange={(e) =>
              setFormData({ ...formData, rate: parseFloat(e.target.value) || 0 })
            }
            placeholder="e.g., 7.5"
            required
          />
          <p className="text-sm text-[var(--muted-foreground)] mt-1">
            Enter as percentage (e.g., 7.5 for 7.5%)
          </p>
        </div>

        <div>
          <Label htmlFor="description">Description (Optional)</Label>
          <Input
            id="description"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="Tax rate description"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="active"
            checked={formData.active}
            onCheckedChange={(checked) =>
              setFormData({ ...formData, active: checked as boolean })
            }
          />
          <Label htmlFor="active">Active</Label>
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
            {taxRate ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}