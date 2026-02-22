import { useState, useEffect } from "react";
import {
  BillCreate,
  BillUpdate,
  InvoiceLineItem,
  useCreateBill,
  useUpdateBill,
  useGetTaxRates,
  useGetVendors,
  TaxRate,
  Bill,
  Vendor,
} from "@/lib/api/hooks/useAccounting";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { PlusIcon, TrashIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface BillFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  bill?: Bill; // Optional bill for editing
}

export function BillFormModal({ isOpen, onClose, bill }: BillFormModalProps) {
  const createMutation = useCreateBill();
  const updateMutation = useUpdateBill();
  const { data: taxRates = [] } = useGetTaxRates(true);
  const { data: vendors = [] } = useGetVendors("active");
  
  const isEditing = !!bill;
  
  const [formData, setFormData] = useState<BillCreate | BillUpdate>({
    vendor_id: "",
    bill_date: new Date().toISOString().split("T")[0],
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0],
    reference_number: "",
    line_items: [{ description: "", quantity: 1, unit_price: 0, amount: 0 }],
    tax_rate_id: undefined,
    tax_exempt: false,
    notes: "",
  });

  const [selectedTaxRate, setSelectedTaxRate] = useState<TaxRate | null>(null);

  // Initialize form data when editing
  useEffect(() => {
    if (bill && isOpen) {
      setFormData({
        vendor_id: bill.vendor_id,
        bill_date: bill.bill_date,
        due_date: bill.due_date,
        reference_number: bill.reference_number || "",
        line_items: bill.line_items,
        tax_rate_id: bill.tax_rate_id,
        tax_exempt: bill.tax_exempt,
        notes: bill.notes || "",
      });
    } else if (!isEditing && isOpen) {
      resetForm();
    }
  }, [bill, isOpen, isEditing]);

  // Update selected tax rate when tax_rate_id changes
  useEffect(() => {
    if (formData.tax_rate_id && taxRates.length > 0) {
      const taxRate = taxRates.find(rate => rate.id === formData.tax_rate_id);
      setSelectedTaxRate(taxRate || null);
    } else {
      setSelectedTaxRate(null);
    }
  }, [formData.tax_rate_id, taxRates]);

  const resetForm = () => {
    setFormData({
      vendor_id: "",
      bill_date: new Date().toISOString().split("T")[0],
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0],
      reference_number: "",
      line_items: [{ description: "", quantity: 1, unit_price: 0, amount: 0 }],
      tax_rate_id: undefined,
      tax_exempt: false,
      notes: "",
    });
    setSelectedTaxRate(null);
  };

  const addItem = () => {
    const currentItems = formData.line_items || [];
    setFormData({
      ...formData,
      line_items: [
        ...currentItems,
        { description: "", quantity: 1, unit_price: 0, amount: 0 },
      ],
    });
  };

  const removeItem = (index: number) => {
    const currentItems = formData.line_items || [];
    if (currentItems.length <= 1) {
      showToast("Must have at least 1 item", "error");
      return;
    }
    setFormData({
      ...formData,
      line_items: currentItems.filter((_, i) => i !== index),
    });
  };

  const updateItem = (index: number, field: keyof InvoiceLineItem, value: any) => {
    const currentItems = [...(formData.line_items || [])];
    currentItems[index] = { ...currentItems[index], [field]: value };

    // Calculate amount
    if (field === "quantity" || field === "unit_price") {
      currentItems[index].amount =
        currentItems[index].quantity * currentItems[index].unit_price;
    }

    setFormData({ ...formData, line_items: currentItems });
  };

  const subtotal = (formData.line_items || []).reduce((sum, item) => sum + item.amount, 0);
  
  // Calculate tax amount
  const taxAmount = formData.tax_exempt || !selectedTaxRate 
    ? 0 
    : subtotal * (selectedTaxRate.rate / 100);
  
  const total = subtotal + taxAmount;

  const handleTaxExemptChange = (checked: boolean) => {
    setFormData({
      ...formData,
      tax_exempt: checked,
      tax_rate_id: checked ? undefined : formData.tax_rate_id,
    });
  };

  const handleTaxRateChange = (taxRateId: string) => {
    setFormData({
      ...formData,
      tax_rate_id: taxRateId === "" ? undefined : taxRateId,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditing && bill) {
        await updateMutation.mutateAsync({ 
          id: bill.id, 
          data: formData as BillUpdate 
        });
        showToast("Bill updated successfully", "success");
      } else {
        await createMutation.mutateAsync(formData as BillCreate);
        showToast("Bill created successfully", "success");
      }
      resetForm();
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} bill`,
        "error"
      );
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? "Edit Bill" : "Create Bill"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="vendor_id">Vendor *</Label>
          <Select
            value={formData.vendor_id || ""}
            onValueChange={(value) =>
              setFormData({ ...formData, vendor_id: value })
            }
            required
          >
            <option value="">Select a vendor</option>
            {vendors.map((vendor) => (
              <option key={vendor.id} value={vendor.id}>
                {vendor.name} ({vendor.vendor_number})
              </option>
            ))}
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="bill_date">Bill Date</Label>
            <Input
              id="bill_date"
              type="date"
              value={formData.bill_date || ""}
              onChange={(e) =>
                setFormData({ ...formData, bill_date: e.target.value })
              }
              required
            />
          </div>
          <div>
            <Label htmlFor="due_date">Due Date</Label>
            <Input
              id="due_date"
              type="date"
              value={formData.due_date || ""}
              onChange={(e) =>
                setFormData({ ...formData, due_date: e.target.value })
              }
              required
            />
          </div>
        </div>

        <div>
          <Label htmlFor="reference_number">Reference Number</Label>
          <Input
            id="reference_number"
            value={formData.reference_number || ""}
            onChange={(e) =>
              setFormData({ ...formData, reference_number: e.target.value })
            }
            placeholder="Vendor's invoice/reference number"
          />
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Items</Label>
            <Button type="button" size="sm" onClick={addItem}>
              <PlusIcon size={16} />
              Add Item
            </Button>
          </div>

          {(formData.line_items || []).map((item, index) => (
            <div key={index} className="grid grid-cols-12 gap-2 items-end">
              <div className="col-span-5">
                <Input
                  value={item.description}
                  onChange={(e) =>
                    updateItem(index, "description", e.target.value)
                  }
                  placeholder="Description"
                  required
                />
              </div>
              <div className="col-span-2">
                <Input
                  type="number"
                  step="1"
                  value={item.quantity}
                  onChange={(e) =>
                    updateItem(index, "quantity", parseInt(e.target.value) || 0)
                  }
                  placeholder="Qty"
                  required
                />
              </div>
              <div className="col-span-2">
                <Input
                  type="number"
                  step="0.01"
                  value={item.unit_price}
                  onChange={(e) =>
                    updateItem(
                      index,
                      "unit_price",
                      parseFloat(e.target.value) || 0
                    )
                  }
                  placeholder="Price"
                  required
                />
              </div>
              <div className="col-span-2">
                <Input
                  type="number"
                  value={item.amount.toFixed(2)}
                  disabled
                  placeholder="Amount"
                />
              </div>
              <div className="col-span-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeItem(index)}
                  disabled={(formData.line_items || []).length <= 1}
                >
                  <TrashIcon size={16} />
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Tax Configuration Section */}
        <div className="space-y-3">
          <Label>Tax Configuration</Label>
          
          <div className="flex items-center space-x-2">
            <Checkbox
              id="tax_exempt"
              checked={formData.tax_exempt || false}
              onCheckedChange={handleTaxExemptChange}
            />
            <Label htmlFor="tax_exempt" className="text-sm font-normal">
              Tax Exempt
            </Label>
          </div>

          {!formData.tax_exempt && (
            <div>
              <Label htmlFor="tax_rate">Tax Rate</Label>
              <Select
                value={formData.tax_rate_id || ""}
                onValueChange={handleTaxRateChange}
              >
                <option value="">No Tax</option>
                {taxRates.map((rate) => (
                  <option key={rate.id} value={rate.id}>
                    {rate.name} ({rate.rate}%)
                  </option>
                ))}
              </Select>
            </div>
          )}
        </div>

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

        <div className="p-4 bg-[var(--muted)] rounded-[var(--radius-md)] space-y-2">
          <div className="flex justify-between">
            <span>Subtotal:</span>
            <span>₦{subtotal.toFixed(2)}</span>
          </div>
          
          {!formData.tax_exempt && selectedTaxRate && (
            <div className="flex justify-between text-sm text-[var(--muted-foreground)]">
              <span>Tax ({selectedTaxRate.name} - {selectedTaxRate.rate}%):</span>
              <span>₦{taxAmount.toFixed(2)}</span>
            </div>
          )}
          
          {formData.tax_exempt && (
            <div className="flex justify-between text-sm text-[var(--muted-foreground)]">
              <span>Tax (Exempt):</span>
              <span>₦0.00</span>
            </div>
          )}
          
          <div className="flex justify-between text-lg font-bold border-t pt-2">
            <span>Total:</span>
            <span>₦{total.toFixed(2)}</span>
          </div>
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
            {isEditing ? 'Update Bill' : 'Create Bill'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}