import { useState, useEffect } from "react";
import {
  InvoiceCreate,
  InvoiceUpdate,
  InvoiceLineItem,
  useCreateInvoice,
  useUpdateInvoice,
  useGetTaxRates,
  TaxRate,
  Invoice,
} from "@/lib/api/hooks/useAccounting";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { PlusIcon, TrashIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface InvoiceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  invoice?: Invoice; // Optional invoice for editing
}

export function InvoiceFormModal({ isOpen, onClose, invoice }: InvoiceFormModalProps) {
  const createMutation = useCreateInvoice();
  const updateMutation = useUpdateInvoice();
  const { data: taxRates = [] } = useGetTaxRates(true);
  
  const isEditing = !!invoice;
  
  const [formData, setFormData] = useState<InvoiceCreate | InvoiceUpdate>({
    client_id: "",
    invoice_date: new Date().toISOString().split("T")[0],
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0],
    line_items: [{ description: "", quantity: 1, unit_price: 0, amount: 0 }],
    tax_rate_id: undefined,
    tax_exempt: false,
    notes: "",
  });

  const [selectedTaxRate, setSelectedTaxRate] = useState<TaxRate | null>(null);

  // Initialize form data when editing
  useEffect(() => {
    if (invoice && isOpen) {
      setFormData({
        client_id: invoice.client_id,
        invoice_date: invoice.invoice_date,
        due_date: invoice.due_date,
        line_items: invoice.line_items,
        tax_rate_id: invoice.tax_rate_id,
        tax_exempt: invoice.tax_exempt,
        notes: invoice.notes || "",
      });
    } else if (!isEditing && isOpen) {
      resetForm();
    }
  }, [invoice, isOpen, isEditing]);

  // Update selected tax rate when tax_rate_id changes
  useEffect(() => {
    if (formData.tax_rate_id && taxRates.length > 0) {
      const taxRate = taxRates.find(rate => rate.id === formData.tax_rate_id);
      setSelectedTaxRate(taxRate || null);
    } else {
      setSelectedTaxRate(null);
    }
  }, [formData.tax_rate_id, taxRates]);

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

  const resetForm = () => {
    setFormData({
      client_id: "",
      invoice_date: new Date().toISOString().split("T")[0],
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0],
      line_items: [{ description: "", quantity: 1, unit_price: 0, amount: 0 }],
      tax_rate_id: undefined,
      tax_exempt: false,
      notes: "",
    });
    setSelectedTaxRate(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEditing && invoice) {
        await updateMutation.mutateAsync({ 
          id: invoice.id, 
          data: formData as InvoiceUpdate 
        });
        showToast("Invoice updated successfully", "success");
      } else {
        await createMutation.mutateAsync(formData as InvoiceCreate);
        showToast("Invoice created successfully", "success");
      }
      resetForm();
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || `Failed to ${isEditing ? 'update' : 'create'} invoice`,
        "error"
      );
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={isEditing ? "Edit Invoice" : "Create Invoice"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="client_id">Client ID</Label>
          <Input
            id="client_id"
            value={formData.client_id || ""}
            onChange={(e) =>
              setFormData({ ...formData, client_id: e.target.value })
            }
            placeholder="Client ID"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="invoice_date">Invoice Date</Label>
            <Input
              id="invoice_date"
              type="date"
              value={formData.invoice_date || ""}
              onChange={(e) =>
                setFormData({ ...formData, invoice_date: e.target.value })
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
            {isEditing ? 'Update Invoice' : 'Create Invoice'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
