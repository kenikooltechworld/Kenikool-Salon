import { useState } from "react";
import {
  useGetPOSTransactions,
  useGetPOSReconciliation,
  useGetPOSSyncStatus,
} from "@/lib/api/hooks/useAccounting";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { format } from "date-fns";
import { RefreshCcwIcon, CheckCircle } from "@/components/icons";

export default function POSIntegrationPage() {
  const [activeTab, setActiveTab] = useState("transactions");
  const [reconciliationDates, setReconciliationDates] = useState({
    start_date: "",
    end_date: "",
  });

  // Queries
  const posTransactionsQuery = useGetPOSTransactions();
  const posSyncStatusQuery = useGetPOSSyncStatus();
  const posReconciliationQuery = useGetPOSReconciliation(
    reconciliationDates.start_date,
    reconciliationDates.end_date,
  );

  const handleLoadReconciliation = () => {
    if (!reconciliationDates.start_date || !reconciliationDates.end_date) {
      showToast("Please select both start and end dates", "warning");
      return;
    }
    posReconciliationQuery.refetch();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">POS Integration</h1>
        <p className="mt-2">Sync POS transactions to accounting</p>
      </div>

      {/* Status Cards */}
      {posSyncStatusQuery.data && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Total Synced
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {posSyncStatusQuery.data.total_synced}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Failed Syncs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {posSyncStatusQuery.data.total_failed}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Last Sync</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium">
                {posSyncStatusQuery.data.last_sync_time
                  ? format(
                      new Date(posSyncStatusQuery.data.last_sync_time),
                      "MMM dd, HH:mm",
                    )
                  : "Never"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {posSyncStatusQuery.data.total_failed === 0 ? (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span className="text-sm font-medium">Healthy</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span className="text-sm font-medium">Issues</span>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="transactions"
      >
        <TabsList>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="reconciliation">Reconciliation</TabsTrigger>
          <TabsTrigger value="sync-logs">Sync Logs</TabsTrigger>
        </TabsList>

        {/* Transactions Tab */}
        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>POS Transactions</CardTitle>
              <CardDescription>View synced POS transactions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-4">Date</th>
                      <th className="text-left py-2 px-4">POS ID</th>
                      <th className="text-left py-2 px-4">Type</th>
                      <th className="text-right py-2 px-4">Amount</th>
                      <th className="text-left py-2 px-4">Payment Method</th>
                      <th className="text-left py-2 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {posTransactionsQuery.data?.map((tx) => (
                      <tr key={tx.id} className="border-b">
                        <td className="py-2 px-4 text-xs">
                          {format(
                            new Date(tx.transaction_date),
                            "MMM dd, yyyy",
                          )}
                        </td>
                        <td className="py-2 px-4 text-xs font-medium">
                          {tx.pos_transaction_id}
                        </td>
                        <td className="py-2 px-4 text-xs capitalize">
                          {tx.transaction_type}
                        </td>
                        <td className="py-2 px-4 text-right text-xs font-medium">
                          ${tx.amount.toFixed(2)}
                        </td>
                        <td className="py-2 px-4 text-xs capitalize">
                          {tx.payment_method}
                        </td>
                        <td className="py-2 px-4">
                          <Badge
                            variant={
                              tx.status === "synced"
                                ? "default"
                                : tx.status === "error"
                                  ? "destructive"
                                  : "secondary"
                            }
                          >
                            {tx.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {posTransactionsQuery.isLoading && (
                <div className="text-center py-8">Loading transactions...</div>
              )}

              {!posTransactionsQuery.isLoading &&
                posTransactionsQuery.data?.length === 0 && (
                  <div className="text-center py-8">No transactions found</div>
                )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reconciliation Tab */}
        <TabsContent value="reconciliation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>POS Reconciliation</CardTitle>
              <CardDescription>
                Compare POS totals with accounting records
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Start Date
                  </label>
                  <Input
                    type="date"
                    value={reconciliationDates.start_date}
                    onChange={(e) =>
                      setReconciliationDates((prev) => ({
                        ...prev,
                        start_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    End Date
                  </label>
                  <Input
                    type="date"
                    value={reconciliationDates.end_date}
                    onChange={(e) =>
                      setReconciliationDates((prev) => ({
                        ...prev,
                        end_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={handleLoadReconciliation}
                    disabled={posReconciliationQuery.isLoading}
                    className="w-full"
                  >
                    <RefreshCcwIcon className="w-4 h-4 mr-2" />
                    Load Reconciliation
                  </Button>
                </div>
              </div>

              {posReconciliationQuery.data && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          POS Total
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          ${posReconciliationQuery.data.pos_total.toFixed(2)}
                        </div>
                        <p className="text-xs mt-1">
                          {posReconciliationQuery.data.pos_transaction_count}{" "}
                          transactions
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Accounting Total
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {posReconciliationQuery.data.accounting_total.toFixed(
                            2,
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Variance
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          ${posReconciliationQuery.data.variance.toFixed(2)}
                        </div>
                        <p className="text-xs mt-1">
                          {posReconciliationQuery.data.variance_percent.toFixed(
                            2,
                          )}
                          %
                        </p>
                      </CardContent>
                    </Card>
                  </div>

                  {posReconciliationQuery.data.reconciled ? (
                    <Alert variant="success">
                      <AlertTitle>Reconciled</AlertTitle>
                      <AlertDescription>
                        POS and accounting totals match
                      </AlertDescription>
                    </Alert>
                  ) : (
                    <Alert variant="error">
                      <AlertTitle>Variance Detected</AlertTitle>
                      <AlertDescription>
                        Difference of $
                        {posReconciliationQuery.data.variance.toFixed(2)}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}

              {posReconciliationQuery.isLoading && (
                <div className="text-center py-8 text-muted-foreground">
                  Loading reconciliation...
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sync Logs Tab */}
        <TabsContent value="sync-logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Sync Logs</CardTitle>
              <CardDescription>View recent POS sync activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {posSyncStatusQuery.data?.recent_logs.map((log) => (
                  <div key={log.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-medium text-sm">
                          {log.pos_transaction_id}
                        </p>
                        <p className="text-xs">
                          {format(
                            new Date(log.timestamp),
                            "MMM dd, yyyy HH:mm:ss",
                          )}
                        </p>
                      </div>
                      <Badge
                        variant={
                          log.status === "synced"
                            ? "default"
                            : log.status === "error"
                              ? "destructive"
                              : "secondary"
                        }
                      >
                        {log.status}
                      </Badge>
                    </div>
                    {log.error && (
                      <Alert variant="error" className="mt-2">
                        <AlertDescription>{log.error}</AlertDescription>
                      </Alert>
                    )}
                  </div>
                ))}
              </div>

              {!posSyncStatusQuery.data?.recent_logs.length && (
                <div className="text-center py-8">No sync logs</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
