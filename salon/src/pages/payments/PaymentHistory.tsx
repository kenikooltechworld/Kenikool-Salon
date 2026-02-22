import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PaymentHistory as PaymentHistoryComponent } from "@/components/payments/PaymentHistory";
import { usePayments } from "@/hooks/usePayments";
import { formatCurrency } from "@/lib/utils";
import {
  CreditCardIcon,
  TrendingUpIcon,
  CheckCircleIcon,
} from "@/components/icons";

export default function PaymentHistoryPage() {
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>();

  const { data: payments = [] } = usePayments({
    status: selectedStatus,
  });

  // Calculate statistics
  const totalAmount = payments.reduce((sum, p) => sum + p.amount, 0);
  const successfulPayments = payments.filter((p) => p.status === "completed");
  const successAmount = successfulPayments.reduce(
    (sum, p) => sum + p.amount,
    0,
  );
  const failedPayments = payments.filter((p) => p.status === "failed");

  const statuses = [
    { value: undefined, label: "All", count: payments.length },
    {
      value: "completed",
      label: "Successful",
      count: successfulPayments.length,
    },
    { value: "failed", label: "Failed", count: failedPayments.length },
    {
      value: "pending",
      label: "Pending",
      count: payments.filter((p) => p.status === "pending").length,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Payment History
          </h1>
          <p className="text-muted-foreground mt-1">
            View and manage your payment transactions
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Payments</p>
              <p className="text-2xl font-bold text-foreground mt-2">
                {formatCurrency(totalAmount, "NGN")}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {payments.length} transactions
              </p>
            </div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <CreditCardIcon size={24} className="text-primary" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Successful</p>
              <p className="text-2xl font-bold text-green-600 mt-2">
                {formatCurrency(successAmount, "NGN")}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {successfulPayments.length} transactions
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircleIcon size={24} className="text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Success Rate</p>
              <p className="text-2xl font-bold text-foreground mt-2">
                {payments.length > 0
                  ? Math.round(
                      (successfulPayments.length / payments.length) * 100,
                    )
                  : 0}
                %
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {failedPayments.length} failed
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <TrendingUpIcon size={24} className="text-blue-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Status Filter */}
      <div className="flex flex-wrap gap-2">
        {statuses.map((status) => (
          <Button
            key={status.value || "all"}
            variant={selectedStatus === status.value ? "primary" : "outline"}
            onClick={() => setSelectedStatus(status.value)}
            className="gap-2"
          >
            {status.label}
            <Badge variant="secondary">{status.count}</Badge>
          </Button>
        ))}
      </div>

      {/* Payment History Table */}
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Recent Transactions
        </h2>
        <PaymentHistoryComponent limit={20} />
      </div>
    </div>
  );
}
