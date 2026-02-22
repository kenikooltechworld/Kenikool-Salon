import { useState } from "react";
import {
  JournalEntryCreate,
  JournalLineItem,
  useCreateJournalEntry,
  useGetAccounts,
} from "@/lib/api/hooks/useAccounting";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { PlusIcon, TrashIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

export function JournalEntryForm({ onSuccess }: { onSuccess?: () => void }) {
  const createMutation = useCreateJournalEntry();
  const { data: accounts = [] } = useGetAccounts();
  const [formData, setFormData] = useState<JournalEntryCreate>({
    date: new Date().toISOString().split("T")[0],
    description: "",
    line_items: [
      { account_id: "", debit: 0, credit: 0 },
      { account_id: "", debit: 0, credit: 0 },
    ],
  });

  const addLine = () => {
    setFormData({
      ...formData,
      line_items: [...formData.line_items, { account_id: "", debit: 0, credit: 0 }],
    });
  };

  const removeLine = (index: number) => {
    if (formData.line_items.length <= 2) {
      showToast("Must have at least 2 lines", "error");
      return;
    }
    setFormData({
      ...formData,
      line_items: formData.line_items.filter((_, i) => i !== index),
    });
  };

  const updateLine = (index: number, field: keyof JournalLineItem, value: any) => {
    const newLines = [...formData.line_items];
    newLines[index] = { ...newLines[index], [field]: value };
    setFormData({ ...formData, line_items: newLines });
  };

  const totalDebit = formData.line_items.reduce(
    (sum, line) => sum + (line.debit || 0),
    0
  );
  const totalCredit = formData.line_items.reduce(
    (sum, line) => sum + (line.credit || 0),
    0
  );
  const isBalanced = totalDebit === totalCredit && totalDebit > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isBalanced) {
      showToast("Debits must equal credits", "error");
      return;
    }
    try {
      await createMutation.mutateAsync(formData);
      showToast("Journal entry created successfully", "success");
      setFormData({
        date: new Date().toISOString().split("T")[0],
        description: "",
        line_items: [
          { account_id: "", debit: 0, credit: 0 },
          { account_id: "", debit: 0, credit: 0 },
        ],
      });
      onSuccess?.();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to create journal entry",
        "error"
      );
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">New Journal Entry</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="date">Date</Label>
            <Input
              id="date"
              type="date"
              value={formData.date}
              onChange={(e) =>
                setFormData({ ...formData, date: e.target.value })
              }
              required
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Entry description"
              required
            />
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Lines</Label>
            <Button type="button" size="sm" onClick={addLine}>
              <PlusIcon size={16} />
              Add Line
            </Button>
          </div>

          {formData.line_items.map((line, index) => (
            <div key={index} className="grid grid-cols-12 gap-2 items-end">
              <div className="col-span-5">
                <Select
                  value={line.account_id}
                  onChange={(e) =>
                    updateLine(index, "account_id", e.target.value)
                  }
                  required
                >
                  <option value="">Select account</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>
                      {account.code} - {account.name}
                    </option>
                  ))}
                </Select>
              </div>
              <div className="col-span-3">
                <Input
                  type="number"
                  step="0.01"
                  value={line.debit || ""}
                  onChange={(e) =>
                    updateLine(index, "debit", parseFloat(e.target.value) || 0)
                  }
                  placeholder="Debit"
                />
              </div>
              <div className="col-span-3">
                <Input
                  type="number"
                  step="0.01"
                  value={line.credit || ""}
                  onChange={(e) =>
                    updateLine(index, "credit", parseFloat(e.target.value) || 0)
                  }
                  placeholder="Credit"
                />
              </div>
              <div className="col-span-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeLine(index)}
                  disabled={formData.line_items.length <= 2}
                >
                  <TrashIcon size={16} />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between p-4 bg-[var(--muted)] rounded-[var(--radius-md)]">
          <div className="flex gap-6">
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">
                Total Debit
              </p>
              <p className="text-lg font-bold">₦{totalDebit.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">
                Total Credit
              </p>
              <p className="text-lg font-bold">₦{totalCredit.toFixed(2)}</p>
            </div>
          </div>
          <div>
            {isBalanced ? (
              <p className="font-semibold">✓ Balanced</p>
            ) : (
              <p className="font-semibold">✗ Not Balanced</p>
            )}
          </div>
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={!isBalanced || createMutation.isPending}
        >
          Create Entry
        </Button>
      </form>
    </Card>
  );
}
