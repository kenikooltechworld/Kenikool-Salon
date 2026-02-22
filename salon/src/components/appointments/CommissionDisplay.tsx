import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface CommissionDisplayProps {
  servicePrice: number;
  commissionPercentage: number;
  commissionAmount: number;
  staffName?: string;
}

export function CommissionDisplay({
  servicePrice,
  commissionPercentage,
  commissionAmount,
  staffName,
}: CommissionDisplayProps) {
  return (
    <Card className="p-4 md:p-6 bg-gradient-to-br from-success/5 to-success/10 dark:from-success/20 dark:to-success/30 border-success/20 dark:border-success/40">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground">Commission Earned</h3>
          <Badge variant="secondary">{commissionPercentage}%</Badge>
        </div>

        {staffName && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Staff Member</span>
            <span className="font-medium text-foreground">{staffName}</span>
          </div>
        )}

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Service Price</span>
          <span className="font-medium text-foreground">
            ₦
            {servicePrice.toLocaleString("en-NG", { maximumFractionDigits: 2 })}
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Commission Rate</span>
          <span className="font-medium text-foreground">
            {commissionPercentage}%
          </span>
        </div>

        <div className="border-t border-success/20 dark:border-success/40 pt-3 flex items-center justify-between">
          <span className="font-semibold text-foreground">
            Commission Amount
          </span>
          <span className="text-lg font-bold text-success dark:text-success/80">
            ₦
            {commissionAmount.toLocaleString("en-NG", {
              maximumFractionDigits: 2,
            })}
          </span>
        </div>

        <p className="text-xs text-muted-foreground pt-2">
          Commission will be marked as pending and can be paid out later.
        </p>
      </div>
    </Card>
  );
}
