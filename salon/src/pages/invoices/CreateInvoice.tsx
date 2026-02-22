import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCreateInvoice } from "@/hooks/useInvoices";
import { useCustomers, type Customer } from "@/hooks/useCustomers";
import { Button } from "@/components/ui/button";
import {
  AlertCircleIcon,
  CheckCircleIcon,
  PlusIcon,
  TrashIcon,
} from "@/components/icons";

export default function CreateInvoice() {
  const navigate = useNavigate();
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    customer_id: "",
    line_items: [
      { id: "1", service_id: "", service_name: "", quantity: 1, unit_price: 0 },
    ],
    tax: 0,
    discount: 0,
    notes: "",
    due_date: "",
  });

  const { data: customersData, isLoading: isLoadingCustomers } = useCustomers();
  const customers = Array.isArray(customersData?.customers)
    ? customersData.customers
    : [];
  const createInvoice = useCreateInvoice();

  const calculateTotals = () => {
    const subtotal = formData.line_items.reduce(
      (sum, item) => sum + item.quantity * item.unit_price,
      0,
    );
    const total = subtotal + formData.tax - formData.discount;
    return { subtotal, total };
  };

  const { subtotal, total } = calculateTotals();

  const handleAddLineItem = () => {
    const newId = String(
      Math.max(...formData.line_items.map((i) => parseInt(i.id) || 0)) + 1,
    );
    setFormData((prev) => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          id: newId,
          service_id: "",
          service_name: "",
          quantity: 1,
          unit_price: 0,
        },
      ],
    }));
  };

  const handleRemoveLineItem = (id: string) => {
    if (formData.line_items.length === 1) {
      setError("Invoice must have at least one line item");
      return;
    }
    setFormData((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((item) => item.id !== id),
    }));
  };

  const handleLineItemChange = (id: string, field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      line_items: prev.line_items.map((item) =>
        item.id === id ? { ...item, [field]: value } : item,
      ),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.customer_id) {
      setError("Please select a customer");
      return;
    }

    if (
      formData.line_items.some(
        (item) => !item.service_name || item.unit_price <= 0,
      )
    ) {
      setError("All line items must have description and rate");
      return;
    }

    if (!formData.due_date) {
      setError("Please set a due date");
      return;
    }

    try {
      await createInvoice.mutateAsync({
        customer_id: formData.customer_id,
        line_items: formData.line_items.map((item) => ({
          service_id: item.service_id || item.service_name,
          service_name: item.service_name,
          quantity: item.quantity,
          unit_price: item.unit_price,
        })),
        tax: formData.tax,
        discount: formData.discount,
        notes: formData.notes,
        due_date: formData.due_date,
      });

      setShowSuccess(true);
      setTimeout(() => {
        navigate("/invoices");
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create invoice");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6">
      <h1 className="text-3xl font-bold text-foreground mb-6">
        Create Invoice
      </h1>

      {showSuccess && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircleIcon
            size={20}
            className="text-green-600 flex-shrink-0 mt-0.5"
          />
          <p className="text-sm text-green-800 dark:text-green-200">
            Invoice created successfully!
          </p>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircleIcon
            size={20}
            className="text-red-600 flex-shrink-0 mt-0.5"
          />
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <form className="space-y-6">
        {/* Customer Selection */}
        <div className="bg-card border border-border rounded-lg p-6">
          <label className="block text-sm font-medium text-foreground mb-2">
            Customer *
          </label>
          <select
            value={formData.customer_id}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, customer_id: e.target.value }))
            }
            disabled={isLoadingCustomers}
            className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">
              {isLoadingCustomers
                ? "Loading customers..."
                : "Select a customer..."}
            </option>
            {customers.map((customer: Customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.firstName} {customer.lastName}
              </option>
            ))}
          </select>
        </div>

        {/* Line Items */}
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="p-6 border-b border-border flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">
              Line Items
            </h2>
            <Button
              type="button"
              onClick={handleAddLineItem}
              size="sm"
              className="gap-2"
            >
              <PlusIcon size={16} />
              Add Item
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted">
                  <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground">
                    Description
                  </th>
                  <th className="px-4 md:px-6 py-3 text-right text-sm font-semibold text-foreground">
                    Quantity
                  </th>
                  <th className="px-4 md:px-6 py-3 text-right text-sm font-semibold text-foreground">
                    Rate
                  </th>
                  <th className="px-4 md:px-6 py-3 text-right text-sm font-semibold text-foreground">
                    Amount
                  </th>
                  <th className="px-4 md:px-6 py-3 text-center text-sm font-semibold text-foreground">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {formData.line_items.map((item) => (
                  <tr key={item.id} className="border-b border-border">
                    <td className="px-4 md:px-6 py-4">
                      <input
                        type="text"
                        value={item.service_name}
                        onChange={(e) =>
                          handleLineItemChange(
                            item.id,
                            "service_name",
                            e.target.value,
                          )
                        }
                        placeholder="Service description"
                        className="w-full px-3 py-2 rounded border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </td>
                    <td className="px-4 md:px-6 py-4">
                      <input
                        type="number"
                        value={item.quantity}
                        onChange={(e) =>
                          handleLineItemChange(
                            item.id,
                            "quantity",
                            parseInt(e.target.value) || 1,
                          )
                        }
                        min="1"
                        className="w-full px-3 py-2 rounded border border-border bg-background text-foreground text-sm text-right focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </td>
                    <td className="px-4 md:px-6 py-4">
                      <input
                        type="number"
                        value={item.unit_price}
                        onChange={(e) =>
                          handleLineItemChange(
                            item.id,
                            "unit_price",
                            parseFloat(e.target.value) || 0,
                          )
                        }
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 rounded border border-border bg-background text-foreground text-sm text-right focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </td>
                    <td className="px-4 md:px-6 py-4 text-right text-sm font-medium text-foreground">
                      {(item.quantity * item.unit_price).toFixed(2)}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-center">
                      <button
                        type="button"
                        onClick={() => handleRemoveLineItem(item.id)}
                        className="p-2 text-destructive hover:bg-destructive/10 rounded-lg transition"
                      >
                        <TrashIcon size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Totals */}
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="space-y-4 max-w-xs ml-auto">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Subtotal</span>
              <span className="text-foreground font-medium">
                {subtotal.toFixed(2)}
              </span>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Tax
              </label>
              <input
                type="number"
                value={formData.tax}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    tax: parseFloat(e.target.value) || 0,
                  }))
                }
                min="0"
                step="0.01"
                className="w-full px-3 py-2 rounded border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Discount
              </label>
              <input
                type="number"
                value={formData.discount}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    discount: parseFloat(e.target.value) || 0,
                  }))
                }
                min="0"
                step="0.01"
                className="w-full px-3 py-2 rounded border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div className="border-t border-border pt-4 flex justify-between">
              <span className="font-semibold text-foreground">Total</span>
              <span className="text-lg font-bold text-foreground">
                {total.toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        {/* Due Date */}
        <div className="bg-card border border-border rounded-lg p-6">
          <label className="block text-sm font-medium text-foreground mb-2">
            Due Date *
          </label>
          <input
            type="date"
            value={formData.due_date}
            onChange={(e) =>
              setFormData((prev) => ({ ...prev, due_date: e.target.value }))
            }
            className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
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
              setFormData((prev) => ({ ...prev, notes: e.target.value }))
            }
            placeholder="Additional notes for the invoice"
            rows={3}
            className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <Button
            type="submit"
            onClick={handleSubmit}
            disabled={createInvoice.isPending}
            variant="outline"
            className="flex-1"
          >
            {createInvoice.isPending ? "Saving..." : "Save as Draft"}
          </Button>
          <Button
            type="submit"
            onClick={handleSubmit}
            disabled={createInvoice.isPending}
            className="flex-1"
          >
            {createInvoice.isPending ? "Creating..." : "Create & Issue"}
          </Button>
        </div>
      </form>
    </div>
  );
}
