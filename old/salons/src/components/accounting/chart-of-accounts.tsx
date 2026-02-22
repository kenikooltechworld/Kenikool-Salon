import { Account } from "@/lib/api/hooks/useAccounting";
import { DollarSignIcon, EditIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface ChartOfAccountsProps {
  accounts: Account[];
  onEdit: (account: Account) => void;
}

export function ChartOfAccounts({ accounts, onEdit }: ChartOfAccountsProps) {
  const groupedAccounts = accounts.reduce((acc, account) => {
    if (!acc[account.account_type]) {
      acc[account.account_type] = [];
    }
    acc[account.account_type].push(account);
    return acc;
  }, {} as Record<string, Account[]>);

  const accountTypeLabels: Record<string, string> = {
    asset: "Assets",
    liability: "Liabilities",
    equity: "Equity",
    revenue: "Revenue",
    expense: "Expenses",
  };

  if (accounts.length === 0) {
    return (
      <div className="text-center py-12">
        <DollarSignIcon
          size={48}
          className="mx-auto text-[var(--muted-foreground)] mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No accounts yet</h3>
        <p className="text-[var(--muted-foreground)]">
          Create your first account to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {Object.entries(groupedAccounts).map(([type, typeAccounts]) => (
        <div key={type}>
          <h3 className="text-lg font-semibold mb-3">
            {accountTypeLabels[type] || type}
          </h3>
          <div className="space-y-2">
            {typeAccounts.map((account) => (
              <Card
                key={account.id}
                className="p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="p-2 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
                      <DollarSignIcon
                        size={20}
                        className="text-[var(--primary)]"
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold">{account.name}</p>
                        <Badge variant="secondary">{account.code}</Badge>
                        <Badge variant="outline">{account.sub_type}</Badge>
                        {!account.active && (
                          <Badge variant="destructive">Inactive</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <p
                      className={`text-lg font-bold`}
                    >
                      ₦{Math.abs(account.balance).toFixed(2)}
                    </p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEdit(account)}
                    >
                      <EditIcon size={16} />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
