import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import {
  DollarSignIcon,
  RefreshCwIcon,
  AlertCircleIcon,
  CheckCircleIcon,
  FileTextIcon,
} from "@/components/icons";
import {
  useCustomerBalance,
  useUpdateCustomerBalance,
  useCustomerBookingEligibility,
} from "@/hooks/useCustomers";
import { formatCurrency, formatDate } from "@/lib/utils/format";

interface CustomerBalanceProps {
  customerId: string;
  customerName: string;
}

export function CustomerBalance({ customerId, customerName }: CustomerBalanceProps) {
  const { showToast } = useToast();
  const [isUpdating, setIsUpdating] = useState(false);

  const { data: balance, isLoading, refetch } = useCustomerBalance(customerId);
  const { data: eligibility, refetch: refetchEligibility } = useCustomerBookingEligibility(customerId);
  const updateBalance = useUpdateCustomerBalance();

  const handleUpdateBalance = async () => {
    setIsUpdating(true);
    try {
      await updateBalance.mutateAsync(customerId);
      await refetch();
      await refetchEligibility();
      showToast({
        title: "Balance Updated",
        description: "Customer balance has been recalculated successfully.",
        variant: "success",
      });
    } catch (error: any) {
      showToast({
        title: "Update Failed",
        description: error.message || "Failed to update balance.",
        variant: "error",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <Card className="p-4 sm:p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-9 w-24" />
          </div>
          <div className="space-y-3">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </div>
      </Card>
    );
  }

  if (!balance) {
    return (
      <Card className="p-4 sm:p-6">
        <div className="text-center py-8">
          <AlertCircleIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Failed to load balance information</p>
          <Button variant="outline" onClick={() => refetch()} className="mt-2">
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <DollarSignIcon size={20} className="text-blue-600" />
            <h3 className="text-lg font-semibold text-foreground">Balance</h3>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleUpdateBalance}
            disabled={isUpdating}
            className="gap-2"
          >
            <RefreshCwIcon size={16} className={isUpdating ? "animate-spin" : ""} />
            Recalculate
          </Button>
        </div>

        {/* Balance Summary */}
        <div className="bg-muted rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Outstanding Balance</span>
            {eligibility && (
              <Badge
                variant={eligibility.isEligibleToBook ? "default" : "destructive"}
                className="text-xs"
              >
                {eligibility.isEligibleToBook ? (
                  <>
                    <CheckCircleIcon size={12} className="mr-1" />
                    Can Book
                  </>
                ) : (
                  <>
                    <AlertCircleIcon size={12} className="mr-1" />
                    Cannot Book
                  </>
                )}
              </Badge>
            )}
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-foreground">
              {formatCurrency(balance.outstandingBalance)}
            </span>
            {balance.unpaidInvoiceCount > 0 && (
              <span className="text-sm text-muted-foreground">
                ({balance.unpaidInvoiceCount} unpaid invoice{balance.unpaidInvoiceCount > 1 ? 's' : ''})
              </span>
            )}
          </div>
          {eligibility && !eligibility.isEligibleToBook && (
            <p className="text-xs text-muted-foreground mt-2">
              {eligibility.reason}
            </p>
          )}
        </div>

        {/* Unpaid Invoices */}
        {balance.unpaidInvoices && balance.unpaidInvoices.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
              <FileTextIcon size={16} />
              Unpaid Invoices
            </h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {balance.unpaidInvoices.map((invoice) => (
                <div
                  key={invoice.invoiceId}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-foreground truncate">
                        Invoice #{invoice.invoiceId.slice(-8)}
                      </p>
                      <Badge
                        variant={invoice.status === "overdue" ? "destructive" : "secondary"}
                        className="text-xs"
                      >
                        {invoice.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                      <span>Created: {formatDate(invoice.createdAt)}</span>
                      {invoice.dueDate && (
                        <span>Due: {formatDate(invoice.dueDate)}</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-foreground">
                      {formatCurrency(invoice.amount)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Balance Message */}
        {balance.outstandingBalance === 0 && (
          <div className="text-center py-4">
            <CheckCircleIcon className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              This customer has no outstanding balance
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}