import { useState } from "react";
import {
  useGetPeriodCloses,
  useCreatePeriodClose,
  useLockPeriod,
  useUnlockPeriod,
  usePerformYearEndClose,
  useGetYearEndReport,
  useGetAccounts,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { format } from "date-fns";
import { AlertCircle, Plus, Calendar } from "@/components/icons";

export default function PeriodClosePage() {
  const [activeTab, setActiveTab] = useState("period-closes");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showYearEndDialog, setShowYearEndDialog] = useState(false);
  const [selectedFiscalYear, setSelectedFiscalYear] = useState<number | null>(
    null,
  );

  // Form states
  const [periodForm, setPeriodForm] = useState({
    period_start: "",
    period_end: "",
    period_type: "monthly",
    description: "",
  });

  const [yearEndForm, setYearEndForm] = useState({
    fiscal_year: new Date().getFullYear(),
    close_date: format(new Date(), "yyyy-MM-dd"),
    retained_earnings_account_id: "",
    create_closing_entries: true,
    notes: "",
  });

  // Queries
  const periodClosesQuery = useGetPeriodCloses();
  const accountsQuery = useGetAccounts();
  const yearEndReportQuery = useGetYearEndReport(selectedFiscalYear || 0);

  // Mutations
  const createPeriodCloseMutation = useCreatePeriodClose();
  const lockPeriodMutation = useLockPeriod();
  const unlockPeriodMutation = useUnlockPeriod();
  const yearEndCloseMutation = usePerformYearEndClose();

  const handleCreatePeriodClose = async () => {
    if (!periodForm.period_start || !periodForm.period_end) {
      showToast("Please fill in all required fields", "warning");
      return;
    }

    try {
      await createPeriodCloseMutation.mutateAsync(periodForm);
      setPeriodForm({
        period_start: "",
        period_end: "",
        period_type: "monthly",
        description: "",
      });
      setShowCreateDialog(false);
    } catch (error) {
      console.error("Error creating period close:", error);
      showToast("Failed to create period close", "error");
    }
  };

  const handleLockPeriod = async (period_close_id: string) => {
    try {
      await lockPeriodMutation.mutateAsync(period_close_id);
    } catch (error) {
      console.error("Error locking period:", error);
      showToast("Failed to lock period", "error");
    }
  };

  const handleUnlockPeriod = async (period_close_id: string) => {
    const reason = prompt("Enter reason for reopening period:");
    if (reason === null) return;

    try {
      await unlockPeriodMutation.mutateAsync({
        period_close_id,
        reopen_reason: reason,
      });
    } catch (error) {
      console.error("Error unlocking period:", error);
      showToast("Failed to unlock period", "error");
    }
  };

  const handlePerformYearEndClose = async () => {
    if (!yearEndForm.retained_earnings_account_id) {
      showToast("Please select a retained earnings account", "warning");
      return;
    }

    try {
      await yearEndCloseMutation.mutateAsync(yearEndForm);
      setShowYearEndDialog(false);
      setYearEndForm({
        fiscal_year: new Date().getFullYear(),
        close_date: format(new Date(), "yyyy-MM-dd"),
        retained_earnings_account_id: "",
        create_closing_entries: true,
        notes: "",
      });
    } catch (error) {
      console.error("Error performing year-end close:", error);
      showToast("Failed to perform year-end close", "error");
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "open":
        return "default";
      case "closed":
        return "success";
      case "year_end_closed":
        return "accent";
      case "reopened":
        return "warning";
      default:
        return "secondary";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Period Close & Year-End
          </h1>
          <p className="text-muted-foreground mt-2">
            Manage accounting periods and year-end close process
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                New Period
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Period Close</DialogTitle>
                <DialogDescription>
                  Create a new accounting period
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Period Start Date
                  </label>
                  <Input
                    type="date"
                    value={periodForm.period_start}
                    onChange={(e) =>
                      setPeriodForm((prev) => ({
                        ...prev,
                        period_start: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Period End Date
                  </label>
                  <Input
                    type="date"
                    value={periodForm.period_end}
                    onChange={(e) =>
                      setPeriodForm((prev) => ({
                        ...prev,
                        period_end: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Period Type
                  </label>
                  <select
                    value={periodForm.period_type}
                    onChange={(e) =>
                      setPeriodForm((prev) => ({
                        ...prev,
                        period_type: e.target.value,
                      }))
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Description (Optional)
                  </label>
                  <Input
                    value={periodForm.description}
                    onChange={(e) =>
                      setPeriodForm((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                    placeholder="Enter description"
                  />
                </div>
                <Button
                  onClick={handleCreatePeriodClose}
                  disabled={createPeriodCloseMutation.isPending}
                  className="w-full"
                >
                  {createPeriodCloseMutation.isPending
                    ? "Creating..."
                    : "Create Period"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={showYearEndDialog} onOpenChange={setShowYearEndDialog}>
            <DialogTrigger>
              <Button variant="outline">
                <Calendar className="w-4 h-4 mr-2" />
                Year-End Close
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Perform Year-End Close</DialogTitle>
                <DialogDescription>
                  Close the fiscal year and create closing entries
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Fiscal Year
                  </label>
                  <Input
                    type="number"
                    value={yearEndForm.fiscal_year}
                    onChange={(e) =>
                      setYearEndForm((prev) => ({
                        ...prev,
                        fiscal_year: parseInt(e.target.value),
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Close Date
                  </label>
                  <Input
                    type="date"
                    value={yearEndForm.close_date}
                    onChange={(e) =>
                      setYearEndForm((prev) => ({
                        ...prev,
                        close_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Retained Earnings Account
                  </label>
                  <select
                    value={yearEndForm.retained_earnings_account_id}
                    onChange={(e) =>
                      setYearEndForm((prev) => ({
                        ...prev,
                        retained_earnings_account_id: e.target.value,
                      }))
                    }
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="">Select account...</option>
                    {Array.isArray(accountsQuery.data) &&
                      accountsQuery.data
                        .filter(
                          (account: any) => account.account_type === "equity",
                        )
                        .map((account: any) => (
                          <option key={account.id} value={account.id}>
                            {account.code} - {account.name}
                          </option>
                        ))}
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="create_entries"
                    checked={yearEndForm.create_closing_entries}
                    onChange={(e) =>
                      setYearEndForm((prev) => ({
                        ...prev,
                        create_closing_entries: e.target.checked,
                      }))
                    }
                  />
                  <label htmlFor="create_entries" className="text-sm">
                    Create closing entries automatically
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Notes (Optional)
                  </label>
                  <Input
                    value={yearEndForm.notes}
                    onChange={(e) =>
                      setYearEndForm((prev) => ({
                        ...prev,
                        notes: e.target.value,
                      }))
                    }
                    placeholder="Enter notes"
                  />
                </div>
                <Button
                  onClick={handlePerformYearEndClose}
                  disabled={yearEndCloseMutation.isPending}
                  className="w-full"
                >
                  {yearEndCloseMutation.isPending
                    ? "Processing..."
                    : "Perform Year-End Close"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="period-closes"
      >
        <TabsList>
          <TabsTrigger value="period-closes">Period Closes</TabsTrigger>
          <TabsTrigger value="year-end-reports">Year-End Reports</TabsTrigger>
        </TabsList>

        {/* Period Closes Tab */}
        <TabsContent value="period-closes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Accounting Periods</CardTitle>
              <CardDescription>
                Manage and lock accounting periods
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {periodClosesQuery.data?.map((period) => (
                  <div
                    key={period.id}
                    className="border rounded-lg p-4 hover:bg-muted"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium">
                            {format(
                              new Date(period.period_start),
                              "MMM dd, yyyy",
                            )}{" "}
                            -{" "}
                            {format(
                              new Date(period.period_end),
                              "MMM dd, yyyy",
                            )}
                          </h3>
                          <Badge variant={getStatusBadgeVariant(period.status)}>
                            {period.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {period.description}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        {!period.locked ? (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleLockPeriod(period.id)}
                            disabled={lockPeriodMutation.isPending}
                          >
                            🔒 Lock
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUnlockPeriod(period.id)}
                            disabled={unlockPeriodMutation.isPending}
                          >
                            🔓 Unlock
                          </Button>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">
                          Period Type:
                        </span>
                        <p className="font-medium capitalize">
                          {period.period_type}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Locked:</span>
                        <p className="font-medium">
                          {period.locked ? "Yes" : "No"}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">
                          Created By:
                        </span>
                        <p className="font-medium">{period.created_by}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Created:</span>
                        <p className="font-medium">
                          {format(new Date(period.created_at), "MMM dd, yyyy")}
                        </p>
                      </div>
                    </div>

                    {period.locked && period.closed_at && (
                      <div className="mt-3 pt-3 border-t text-xs text-muted-foreground">
                        Closed on{" "}
                        {format(
                          new Date(period.closed_at),
                          "MMM dd, yyyy HH:mm:ss",
                        )}
                      </div>
                    )}
                  </div>
                ))}

                {periodClosesQuery.isLoading && (
                  <div className="text-center py-8 text-muted-foreground">
                    Loading periods...
                  </div>
                )}

                {!periodClosesQuery.isLoading &&
                  periodClosesQuery.data?.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      No periods found
                    </div>
                  )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Year-End Reports Tab */}
        <TabsContent value="year-end-reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Year-End Reports</CardTitle>
              <CardDescription>
                View year-end close reports and closing entries
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select Fiscal Year
                </label>
                <div className="flex gap-2">
                  <Input
                    type="number"
                    value={selectedFiscalYear || ""}
                    onChange={(e) =>
                      setSelectedFiscalYear(
                        e.target.value ? parseInt(e.target.value) : null,
                      )
                    }
                    placeholder="Enter fiscal year"
                    min={2000}
                    max={new Date().getFullYear()}
                  />
                  <Button
                    onClick={() => yearEndReportQuery.refetch()}
                    disabled={
                      !selectedFiscalYear || yearEndReportQuery.isLoading
                    }
                  >
                    Load Report
                  </Button>
                </div>
              </div>

              {yearEndReportQuery.data && (
                <div className="space-y-4">
                  {/* Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Net Income
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {yearEndReportQuery.data.net_income.toLocaleString(
                            "en-US",
                            {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            },
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Retained Earnings (Beginning)
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {yearEndReportQuery.data.retained_earnings_beginning.toLocaleString(
                            "en-US",
                            {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            },
                          )}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Retained Earnings (Ending)
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {yearEndReportQuery.data.retained_earnings_ending.toLocaleString(
                            "en-US",
                            {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            },
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Closing Entries */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Closing Entries</CardTitle>
                      <CardDescription>
                        {yearEndReportQuery.data.closing_entries.length} entries
                        created
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="border-b">
                            <tr>
                              <th className="text-left py-2 px-4">Account</th>
                              <th className="text-left py-2 px-4">Type</th>
                              <th className="text-right py-2 px-4">Debit</th>
                              <th className="text-right py-2 px-4">Credit</th>
                            </tr>
                          </thead>
                          <tbody>
                            {yearEndReportQuery.data.closing_entries.map(
                              (entry) => (
                                <tr
                                  key={entry.id}
                                  className="border-b hover:bg-muted"
                                >
                                  <td className="py-2 px-4">
                                    <div className="text-xs">
                                      <div className="font-medium">
                                        {entry.account_name}
                                      </div>
                                      <div className="text-muted-foreground">
                                        {entry.account_id}
                                      </div>
                                    </div>
                                  </td>
                                  <td className="py-2 px-4 text-xs capitalize">
                                    {entry.closing_type}
                                  </td>
                                  <td className="py-2 px-4 text-right text-xs">
                                    {entry.debit > 0
                                      ? `$${entry.debit.toFixed(2)}`
                                      : "-"}
                                  </td>
                                  <td className="py-2 px-4 text-right text-xs">
                                    {entry.credit > 0
                                      ? `$${entry.credit.toFixed(2)}`
                                      : "-"}
                                  </td>
                                </tr>
                              ),
                            )}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {yearEndReportQuery.isLoading && (
                <div className="text-center py-8 text-muted-foreground">
                  Loading report...
                </div>
              )}

              {yearEndReportQuery.error && (
                <Alert variant="error">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>
                    No year-end report found for this fiscal year
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
