import React, { useState } from "react";
import {
  useGetSMSBalance,
  useGetSMSHistory,
  usePurchaseSMSCredits,
  useSetLowBalanceThreshold,
} from "@/lib/api/hooks/useSMSCredits";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  AlertCircleIcon,
  TrendingDownIcon,
  TrendingUpIcon,
} from "@/components/icons";
import { toast } from "sonner";
import { format } from "date-fns";

export function SMSCreditsManager() {
  const [showPurchaseForm, setShowPurchaseForm] = useState(false);
  const [purchaseAmount, setPurchaseAmount] = useState(100);
  const [showThresholdForm, setShowThresholdForm] = useState(false);
  const [thresholdValue, setThresholdValue] = useState(100);

  const { data: balance, isLoading: balanceLoading } = useGetSMSBalance();
  const { data: history, isLoading: historyLoading } = useGetSMSHistory();
  const purchaseCredits = usePurchaseSMSCredits();
  const setThreshold = useSetLowBalanceThreshold();

  const handlePurchaseCredits = async () => {
    if (purchaseAmount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      await purchaseCredits.mutateAsync({
        amount: purchaseAmount,
        payment_method: "card",
      });
      toast.success(`Successfully purchased ${purchaseAmount} SMS credits`);
      setShowPurchaseForm(false);
      setPurchaseAmount(100);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to purchase credits");
    }
  };

  const handleSetThreshold = async () => {
    if (thresholdValue < 0) {
      toast.error("Please enter a valid threshold");
      return;
    }

    try {
      await setThreshold.mutateAsync(thresholdValue);
      toast.success("Low balance threshold updated");
      setShowThresholdForm(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update threshold");
    }
  };

  return (
    <div className="space-y-6">
      {/* Balance Overview */}
      {balanceLoading ? (
        <p className="text-muted-foreground">Loading balance...</p>
      ) : balance ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Current Balance */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Current Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {balance.current_balance}
              </div>
              <p className="text-xs text-muted-foreground mt-1">SMS Credits</p>
            </CardContent>
          </Card>

          {/* Total Purchased */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingUpIcon className="h-4 w-4 text-green-600" />
                Total Purchased
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {balance.total_purchased}
              </div>
              <p className="text-xs text-muted-foreground mt-1">All time</p>
            </CardContent>
          </Card>

          {/* Total Used */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingDownIcon className="h-4 w-4 text-red-600" />
                Total Used
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {balance.total_used}
              </div>
              <p className="text-xs text-muted-foreground mt-1">All time</p>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Low Balance Alert */}
      {balance && balance.current_balance < balance.low_balance_threshold && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6 flex items-center gap-3">
            <AlertCircleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-semibold text-yellow-900">Low SMS Credits</p>
              <p className="text-sm text-yellow-800">
                Your balance is below the threshold (
                {balance.low_balance_threshold}). Purchase more credits to
                continue sending campaigns.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button onClick={() => setShowPurchaseForm(!showPurchaseForm)}>
          {showPurchaseForm ? "Cancel" : "Purchase Credits"}
        </Button>
        <Button
          variant="outline"
          onClick={() => setShowThresholdForm(!showThresholdForm)}
        >
          {showThresholdForm ? "Cancel" : "Set Alert Threshold"}
        </Button>
      </div>

      {/* Purchase Form */}
      {showPurchaseForm && (
        <Card>
          <CardHeader>
            <CardTitle>Purchase SMS Credits</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Number of Credits</label>
              <Input
                type="number"
                min="1"
                value={purchaseAmount}
                onChange={(e) =>
                  setPurchaseAmount(parseInt(e.target.value) || 0)
                }
                placeholder="Enter amount"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Estimated cost: ₦{(purchaseAmount * 0.5).toFixed(2)} (₦0.50 per
                credit)
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handlePurchaseCredits}
                disabled={purchaseCredits.isPending}
              >
                Proceed to Payment
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowPurchaseForm(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Threshold Form */}
      {showThresholdForm && (
        <Card>
          <CardHeader>
            <CardTitle>Set Low Balance Alert Threshold</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Alert Threshold</label>
              <Input
                type="number"
                min="0"
                value={thresholdValue}
                onChange={(e) =>
                  setThresholdValue(parseInt(e.target.value) || 0)
                }
                placeholder="Enter threshold"
              />
              <p className="text-xs text-muted-foreground mt-1">
                You'll receive an alert when your balance falls below this value
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleSetThreshold}
                disabled={setThreshold.isPending}
              >
                Save Threshold
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowThresholdForm(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Transaction History */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Transaction History</h2>
        {historyLoading ? (
          <p className="text-muted-foreground">Loading history...</p>
        ) : history && history.transactions.length > 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-4">Date</th>
                      <th className="text-left py-2 px-4">Type</th>
                      <th className="text-left py-2 px-4">Reason</th>
                      <th className="text-right py-2 px-4">Amount</th>
                      <th className="text-right py-2 px-4">Balance Before</th>
                      <th className="text-right py-2 px-4">Balance After</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.transactions.map((tx) => (
                      <tr key={tx.id} className="border-b hover:bg-muted/50">
                        <td className="py-2 px-4">
                          {format(
                            new Date(tx.created_at),
                            "MMM dd, yyyy HH:mm",
                          )}
                        </td>
                        <td className="py-2 px-4">
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              tx.transaction_type === "purchase"
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}
                          >
                            {tx.transaction_type}
                          </span>
                        </td>
                        <td className="py-2 px-4 text-muted-foreground">
                          {tx.reason}
                        </td>
                        <td
                          className={`py-2 px-4 text-right font-semibold ${
                            tx.transaction_type === "purchase"
                              ? "text-green-600"
                              : "text-red-600"
                          }`}
                        >
                          {tx.transaction_type === "purchase" ? "+" : "-"}
                          {tx.amount}
                        </td>
                        <td className="py-2 px-4 text-right">
                          {tx.balance_before}
                        </td>
                        <td className="py-2 px-4 text-right">
                          {tx.balance_after}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ) : (
          <p className="text-muted-foreground">No transactions yet</p>
        )}
      </div>
    </div>
  );
}
