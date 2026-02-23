import { useParams, useNavigate } from "react-router-dom";
import { useInvoice, useUpdateInvoice } from "@/hooks/useInvoices";
import { useToast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { TrashIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/format";
import { useState, useEffect } from "react";

interface LineItem {
  service_id: string;
  service_name: string;
  quantity: number;
  unit_price: number;
}

export default function EditInvoice() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { data: invoice, isLoading } = useInvoice(id || "");
  const updateMutation = useUpdateInvoice();

  const [formData, setFormData] = useState({
    customer_id: "",
    line_items: [] as LineItem[],
    notes: "",
    due_date: "",
  });

  useEffect(() => {
    if (invoice) {
      if (invoice.status !== "draft") {
        alert("Only draft invoices can be edited");
        navigate("/invoices");
        return;
      }
      setFormData({
        customer_id: invoice.customer_id,
        line_items: invoice.line_items || [],
        notes: invoice.notes || "",
        due_date: invoice.due_date,
      });
    }
  }, [invoice, navigate]);

  const handleAddLineItem = () => {
    setFormData({
      ...formData,
      line_items: [
        ...formData.line_items,
        { service_id: "", service_name: "", quantity: 1, unit_price: 0 },
      ],
    });
  };

  const handleRemoveLineItem = (index: number) => {
    setFormData({
      ...formData,
      line_items: formData.line_items.filter((_, i) => i !== index),
    });
  };

  const handleLineItemChange = (
    index: number,
    field: keyof LineItem,
    value: any,
  ) => {
    const newItems = [...formData.line_items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, line_items: newItems });
  };

  const calculateTotal = () => {
    return formData.line_items.reduce(
      (sum, item) => sum + item.quantity * item.unit_price,
      0,
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;

    try {
      await updateMutation.mutateAsync({
        id,
        line_items: formData.line_items.map((item) => ({
          service_id: item.service_id,
          service_name: item.service_name,
          quantity: item.quantity,
          unit_price: item.unit_price,
          total: item.quantity * item.unit_price,
        })),
        notes: formData.notes,
        due_date: formData.due_date,
      });
      showToast({
        variant: "success",
        title: "Success",
        description: "Invoice updated successfully",
      });
      navigate(`/invoices/${id}`);
    } catch (error) {
      showToast({
        variant: "error",
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to update invoice",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
        <Skeleton className="h-10 w-48" />
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="max-w-4xl mx-auto p-4 sm:p-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground">Invoice not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-foreground">Edit Invoice</h1>
        <Button variant="outline" onClick={() => navigate("/invoices")}>
          Back
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer */}
        <div className="bg-card border border-border rounded-lg p-6">
          <label className="block text-sm font-medium text-foreground mb-2">
            Customer ID
          </label>
          <input
            type="text"
            value={formData.customer_id}
            disabled
            className="w-full px-3 py-2 border border-border rounded-lg bg-muted text-muted-foreground"
          />
        </div>

        {/* Line Items */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">
              Line Items
            </h2>
            <Button
              type="button"
              onClick={handleAddLineItem}
              variant="outline"
              size="sm"
            >
              Add Item
            </Button>
          </div>

          <div className="space-y-4">
            {formData.line_items.map((item, index) => (
              <div key={index} className="flex gap-4 items-end">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-foreground mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    value={item.service_name}
                    onChange={(e) =>
                      handleLineItemChange(
                        index,
                        "service_name",
                        e.target.value,
                      )
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Service description"
                  />
                </div>
                <div className="w-24">
                  <label className="block text-sm font-medium text-foreground mb-1">
                    Qty
                  </label>
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) =>
                      handleLineItemChange(
                        index,
                        "quantity",
                        parseInt(e.target.value),
                      )
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    min="1"
                  />
                </div>
                <div className="w-32">
                  <label className="block text-sm font-medium text-foreground mb-1">
                    Rate
                  </label>
                  <input
                    type="number"
                    value={item.unit_price}
                    onChange={(e) =>
                      handleLineItemChange(
                        index,
                        "unit_price",
                        parseFloat(e.target.value),
                      )
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    min="0"
                    step="0.01"
                  />
                </div>
                <div className="w-32">
                  <label className="block text-sm font-medium text-foreground mb-1">
                    Amount
                  </label>
                  <div className="px-3 py-2 border border-border rounded-lg bg-muted text-muted-foreground text-sm">
                    {formatCurrency(item.quantity * item.unit_price)}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveLineItem(index)}
                  className="p-2 text-destructive hover:bg-destructive/10 rounded-lg transition"
                >
                  <TrashIcon size={16} />
                </button>
              </div>
            ))}
          </div>

          {formData.line_items.length === 0 && (
            <p className="text-muted-foreground text-center py-4">
              No line items. Click "Add Item" to add one.
            </p>
          )}
        </div>

        {/* Totals */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex justify-end">
            <div className="w-64 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal:</span>
                <span className="text-foreground font-medium">
                  {formatCurrency(calculateTotal())}
                </span>
              </div>
              <div className="flex justify-between font-bold text-lg border-t border-border pt-2">
                <span className="text-foreground">Total:</span>
                <span className="text-foreground">
                  {formatCurrency(calculateTotal())}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Due Date */}
        <div className="bg-card border border-border rounded-lg p-6">
          <label className="block text-sm font-medium text-foreground mb-2">
            Due Date
          </label>
          <input
            type="date"
            value={formData.due_date}
            onChange={(e) =>
              setFormData({ ...formData, due_date: e.target.value })
            }
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Notes */}
        <div className="bg-card border border-border rounded-lg p-6">
          <label className="block text-sm font-medium text-foreground mb-2">
            Notes
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) =>
              setFormData({ ...formData, notes: e.target.value })
            }
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            rows={4}
            placeholder="Additional notes for the invoice"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <Button
            type="submit"
            disabled={updateMutation.isPending}
            className="flex-1"
          >
            {updateMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/invoices")}
            className="flex-1"
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
