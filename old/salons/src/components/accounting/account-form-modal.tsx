import { useState, useEffect } from "react";
import {
  Account,
  AccountCreate,
  AccountUpdate,
  useCreateAccount,
  useUpdateAccount,
} from "@/lib/api/hooks/useAccounting";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { showToast } from "@/lib/utils/toast";

interface AccountFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  account?: Account | null;
}

export function AccountFormModal({
  isOpen,
  onClose,
  account,
}: AccountFormModalProps) {
  const createMutation = useCreateAccount();
  const updateMutation = useUpdateAccount();
  const [formData, setFormData] = useState<AccountCreate>({
    code: "",
    name: "",
    account_type: "asset",
    sub_type: "cash",
  });

  useEffect(() => {
    if (account) {
      setFormData({
        code: account.code,
        name: account.name,
        account_type: account.account_type,
        sub_type: account.sub_type,
        description: account.description,
        parent_account_id: account.parent_account_id,
      });
    } else {
      setFormData({
        code: "",
        name: "",
        account_type: "asset",
        sub_type: "cash",
      });
    }
  }, [account, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (account) {
        const updateData: AccountUpdate = {
          name: formData.name,
          description: formData.description,
        };
        await updateMutation.mutateAsync({ id: account.id, data: updateData });
        showToast("Account updated successfully", "success");
      } else {
        await createMutation.mutateAsync(formData);
        showToast("Account created successfully", "success");
      }
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to save account",
        "error"
      );
    }
  };

  const accountTypes = [
    { value: "asset", label: "Asset" },
    { value: "liability", label: "Liability" },
    { value: "equity", label: "Equity" },
    { value: "revenue", label: "Revenue" },
    { value: "expense", label: "Expense" },
  ];

  const subTypesByType: Record<string, { value: string; label: string }[]> = {
    asset: [
      { value: "cash", label: "Cash" },
      { value: "bank", label: "Bank" },
      { value: "accounts_receivable", label: "Accounts Receivable" },
      { value: "inventory", label: "Inventory" },
      { value: "fixed_assets", label: "Fixed Assets" },
    ],
    liability: [
      { value: "accounts_payable", label: "Accounts Payable" },
      { value: "credit_card", label: "Credit Card" },
      { value: "loans", label: "Loans" },
    ],
    equity: [
      { value: "owners_equity", label: "Owner's Equity" },
      { value: "retained_earnings", label: "Retained Earnings" },
    ],
    revenue: [
      { value: "service_revenue", label: "Service Revenue" },
      { value: "product_revenue", label: "Product Revenue" },
      { value: "other_revenue", label: "Other Revenue" },
    ],
    expense: [
      { value: "cost_of_goods", label: "Cost of Goods Sold" },
      { value: "operating_expenses", label: "Operating Expenses" },
      { value: "payroll", label: "Payroll" },
      { value: "rent", label: "Rent" },
      { value: "utilities", label: "Utilities" },
      { value: "marketing", label: "Marketing" },
    ],
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={account ? "Edit Account" : "Create Account"}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="code">Account Code</Label>
          <Input
            id="code"
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            placeholder="e.g., 1000"
            required
            disabled={!!account} // Don't allow editing code for existing accounts
          />
        </div>

        <div>
          <Label htmlFor="name">Account Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Cash"
            required
          />
        </div>

        <div>
          <Label htmlFor="description">Description (Optional)</Label>
          <Input
            id="description"
            value={formData.description || ""}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Account description"
          />
        </div>

        <div>
          <Label htmlFor="account_type">Account Type</Label>
          <Select
            id="account_type"
            value={formData.account_type}
            onChange={(e) =>
              setFormData({
                ...formData,
                account_type: e.target.value,
                sub_type: subTypesByType[e.target.value][0].value,
              })
            }
            required
            disabled={!!account} // Don't allow editing type for existing accounts
          >
            {accountTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <Label htmlFor="sub_type">Sub Type</Label>
          <Select
            id="sub_type"
            value={formData.sub_type}
            onChange={(e) =>
              setFormData({ ...formData, sub_type: e.target.value })
            }
            required
            disabled={!!account} // Don't allow editing sub_type for existing accounts
          >
            {subTypesByType[formData.account_type]?.map((subType) => (
              <option key={subType.value} value={subType.value}>
                {subType.label}
              </option>
            ))}
          </Select>
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
            {account ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
