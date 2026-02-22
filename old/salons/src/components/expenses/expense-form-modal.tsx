import { useState, useEffect, useMemo } from "react";
import {
  useCreateExpense,
  useUpdateExpense,
  Expense,
  ExpenseCreate,
} from "@/lib/api/hooks/useExpenses";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { showToast } from "@/lib/utils/toast";

interface ExpenseFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  expense?: Expense | null;
}

const EXPENSE_CATEGORIES = [
  "Rent",
  "Utilities",
  "Supplies",
  "Salaries",
  "Marketing",
  "Equipment",
  "Maintenance",
  "Insurance",
  "Other",
];

const PAYMENT_METHODS = ["Cash", "Card", "Bank Transfer", "Mobile Money"];

const getDefaultFormData = (): ExpenseCreate => ({
  category: "Other",
  amount: 0,
  description: "",
  expense_date: new Date().toISOString().split("T")[0],
  payment_method: "Cash",
  receipt_url: "",
  vendor: "",
  notes: "",
});

const getFormDataFromExpense = (expense: Expense): ExpenseCreate => ({
  category: expense.category,
  amount: expense.amount,
  description: expense.description,
  expense_date: expense.expense_date.split("T")[0],
  payment_method: expense.payment_method,
  receipt_url: expense.receipt_url,
  vendor: expense.vendor || "",
  notes: expense.notes || "",
});

export function ExpenseFormModal({
  isOpen,
  onClose,
  expense,
}: ExpenseFormModalProps) {
  const createMutation = useCreateExpense();
  const updateMutation = useUpdateExpense();

  const initialFormData = useMemo(
    () => (expense ? getFormDataFromExpense(expense) : getDefaultFormData()),
    [expense]
  );

  const [formData, setFormData] = useState<ExpenseCreate>(initialFormData);

  useEffect(() => {
    setFormData(initialFormData);
  }, [initialFormData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (expense) {
        await updateMutation.mutateAsync({ id: expense._id, data: formData });
      } else {
        await createMutation.mutateAsync(formData);
      }
      showToast(
        `Expense ${expense ? "updated" : "created"} successfully`,
        "success"
      );
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to save expense",
        "error"
      );
    }
  };

  return (
    <Modal
      open={isOpen}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="mb-4">
          <h2 className="text-2xl font-semibold">{`${expense ? "Edit" : "Add"} Expense`}</h2>
        </div>
        <div>
          <Label htmlFor="description">Description *</Label>
          <Input
            id="description"
            type="text"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="Office supplies"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="category">Category *</Label>
            <Select
              id="category"
              value={formData.category}
              onValueChange={(value) =>
                setFormData({ ...formData, category: value })
              }
              required
            >
              {EXPENSE_CATEGORIES.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </Select>
          </div>

          <div>
            <Label htmlFor="amount">Amount (₦) *</Label>
            <Input
              id="amount"
              type="number"
              value={formData.amount}
              onChange={(e) =>
                setFormData({ ...formData, amount: parseFloat(e.target.value) })
              }
              min="0"
              step="0.01"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="expense_date">Date *</Label>
            <Input
              id="expense_date"
              type="date"
              value={formData.expense_date}
              onChange={(e) =>
                setFormData({ ...formData, expense_date: e.target.value })
              }
              required
            />
          </div>

          <div>
            <Label htmlFor="payment_method">Payment Method</Label>
            <Select
              id="payment_method"
              value={formData.payment_method || "Cash"}
              onValueChange={(value) =>
                setFormData({ ...formData, payment_method: value })
              }
            >
              {PAYMENT_METHODS.map((method) => (
                <SelectItem key={method} value={method}>
                  {method}
                </SelectItem>
              ))}
            </Select>
          </div>
        </div>

        <div>
          <Label htmlFor="receipt_url">Receipt URL</Label>
          <Input
            id="receipt_url"
            type="url"
            value={formData.receipt_url || ""}
            onChange={(e) =>
              setFormData({ ...formData, receipt_url: e.target.value })
            }
            placeholder="https://..."
          />
        </div>

        <div>
          <Label htmlFor="vendor">Vendor</Label>
          <Input
            id="vendor"
            type="text"
            value={formData.vendor || ""}
            onChange={(e) =>
              setFormData({ ...formData, vendor: e.target.value })
            }
            placeholder="Vendor name"
            maxLength={200}
          />
        </div>

        <div>
          <Label htmlFor="notes">Notes</Label>
          <Textarea
            id="notes"
            value={formData.notes || ""}
            onChange={(e) =>
              setFormData({ ...formData, notes: e.target.value })
            }
            placeholder="Additional notes about this expense"
            maxLength={1000}
            rows={3}
          />
        </div>

        <div className="flex gap-3 pt-4 border-t border-[var(--border)]">
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
            disabled={createMutation.isPending || updateMutation.isPending}
            className="flex-1"
          >
            {createMutation.isPending || updateMutation.isPending
              ? "Saving..."
              : expense
              ? "Update Expense"
              : "Add Expense"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
