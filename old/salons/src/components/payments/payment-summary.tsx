import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DollarIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
} from "@/components/icons";

interface PaymentSummaryProps {
  totalAmount: number;
  depositPaid?: number;
  amountPaid?: number;
  status?: "pending" | "partial" | "paid" | "refunded";
}

export function PaymentSummary({
  totalAmount,
  depositPaid = 0,
  amountPaid = 0,
  status = "pending",
}: PaymentSummaryProps) {
  const remainingBalance = totalAmount - depositPaid - amountPaid;

  const getStatusColor = () => {
    switch (status) {
      case "paid":
        return "bg-[var(--success)] text-white";
      case "partial":
        return "bg-[var(--warning)] text-white";
      case "refunded":
        return "bg-[var(--error)] text-white";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case "paid":
        return "Paid";
      case "partial":
        return "Partially Paid";
      case "refunded":
        return "Refunded";
      default:
        return "Pending";
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <DollarIcon size={20} className="text-muted-foreground" />
          <h3 className="font-semibold text-foreground">Payment Summary</h3>
        </div>
        <Badge className={getStatusColor()}>{getStatusLabel()}</Badge>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Total Amount</span>
          <span className="font-medium text-foreground">
            ₦{totalAmount.toLocaleString()}
          </span>
        </div>

        {depositPaid > 0 && (
          <div className="flex justify-between text-sm text-[var(--success)]">
            <span>Deposit Paid</span>
            <span>₦{depositPaid.toLocaleString()}</span>
          </div>
        )}

        {amountPaid > 0 && (
          <div className="flex justify-between text-sm text-[var(--success)]">
            <span>Amount Paid</span>
            <span>₦{amountPaid.toLocaleString()}</span>
          </div>
        )}

        <div className="border-t border-[var(--border)] pt-2">
          <div className="flex justify-between">
            <span className="font-semibold text-foreground">Balance</span>
            <span
              className={`font-bold ${
                remainingBalance === 0
                  ? "text-[var(--success)]"
                  : "text-foreground"
              }`}
            >
              ₦{remainingBalance.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {remainingBalance > 0 && (
        <div className="mt-3 flex items-center gap-2 text-sm text-[var(--warning)]">
          <AlertTriangleIcon size={16} />
          <span>Payment incomplete</span>
        </div>
      )}

      {remainingBalance === 0 && status === "paid" && (
        <div className="mt-3 flex items-center gap-2 text-sm text-[var(--success)]">
          <CheckCircleIcon size={16} />
          <span>Payment complete</span>
        </div>
      )}
    </Card>
  );
}
