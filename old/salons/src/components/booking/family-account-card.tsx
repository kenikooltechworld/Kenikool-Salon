import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { FamilyAccount } from "@/lib/api/types";

interface FamilyAccountCardProps {
  account: FamilyAccount;
  onClick?: () => void;
}

export function FamilyAccountCard({
  account,
  onClick,
}: FamilyAccountCardProps) {
  return (
    <Card
      className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      <div className="space-y-3">
        <div>
          <h3 className="font-semibold text-foreground">
            {account.account_name}
          </h3>
          <p className="text-sm text-muted-foreground">
            {account.family_account_id}
          </p>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground">Members</p>
            <p className="text-lg font-bold">{account.members.length}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Balance</p>
            <p className="text-lg font-bold">
              ₦{account.outstanding_balance.toLocaleString()}
            </p>
          </div>
        </div>

        {account.outstanding_balance > 0 && (
          <Badge variant="destructive">Outstanding Balance</Badge>
        )}
      </div>
    </Card>
  );
}
