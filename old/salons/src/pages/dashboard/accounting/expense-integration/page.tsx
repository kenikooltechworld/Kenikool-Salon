import { useState } from "react";
import {
  useGetExpenseMappings,
  useCreateExpenseMapping,
  useGetExpenses,
  useApproveExpense,
  useRejectExpense,
  useGetExpenseReconciliation,
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { format } from "date-fns";
import { Plus } from "@/components/icons";

export default function ExpenseIntegrationPage() {
  const [activeTab, setActiveTab] = useState("mappings");
  const [showMappingDialog, setShowMappingDialog] = useState(false);
  const [reconciliationDates, setReconciliationDates] = useState({
    start_date: "",
    end_date: "",
  });

  // Form states
  const [mappingForm, setMappingForm] = useState({
    category: "",
    account_id: "",
    description: "",
  });

  // Queries
  const mappingsQuery = useGetExpenseMappings();
  const expensesQuery = useGetExpenses();
  const accountsQuery = useGetAccounts();
  const expenseReconciliationQuery = useGetExpenseReconciliation(
    reconciliationDates.start_date,
    reconciliationDates.end_date,
  );

  // Mutations
  const createMappingMutation = useCreateExpenseMapping();
  const approveMutation = useApproveExpense();
  const rejectMutation = useRejectExpense();

  const handleCreateMapping = async () => {
    if (!mappingForm.category || !mappingForm.account_id) {
      showToast("Please fill in all required fields", "warning");
      return;
    }

    try {
      await createMappingMutation.mutateAsync(mappingForm);
      setMappingForm({ category: "", account_id: "", description: "" });
      setShowMappingDialog(false);
    } catch (error) {
      console.error("Error creating mapping:", error);
      showToast("Failed to create mapping", "error");
    }
  };

  const handleApproveExpense = async (expense_id: string) => {
    try {
      await approveMutation.mutateAsync(expense_id);
    } catch (error) {
      console.error("Error approving expense:", error);
      showToast("Failed to approve expense", "error");
    }
  };

  const handleRejectExpense = async (expense_id: string) => {
    const reason = prompt("Enter rejection reason:");
    if (reason === null) return;

    try {
      await rejectMutation.mutateAsync({ expense_id, reason });
    } catch (error) {
      console.error("Error rejecting expense:", error);
      showToast("Failed to reject expense", "error");
    }
  };

  const handleLoadReconciliation = () => {
    if (!reconciliationDates.start_date || !reconciliationDates.end_date) {
      showToast("Please select both start and end dates", "warning");
      return;
    }
    expenseReconciliationQuery.refetch();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Expense Integration
          </h1>
          <p className="mt-2">
            Manage expense categories and sync to accounting
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      {expensesQuery.data && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Total Expenses
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {expensesQuery.data.length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Approved</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {
                  expensesQuery.data.filter(
                    (e) => e.approval_status === "approved",
                  ).length
                }
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {
                  expensesQuery.data.filter(
                    (e) => e.approval_status === "pending",
                  ).length
                }
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {
                  expensesQuery.data.filter(
                    (e) => e.approval_status === "rejected",
                  ).length
                }
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="mappings"
      >
        <TabsList>
          <TabsTrigger value="mappings">Category Mappings</TabsTrigger>
          <TabsTrigger value="expenses">Expenses</TabsTrigger>
          <TabsTrigger value="reconciliation">Reconciliation</TabsTrigger>
        </TabsList>

        {/* Mappings Tab */}
        <TabsContent value="mappings" className="space-y-4">
          <div className="flex justify-end">
            <Dialog
              open={showMappingDialog}
              onOpenChange={setShowMappingDialog}
            >
              <DialogTrigger>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  New Mapping
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Expense Mapping</DialogTitle>
                  <DialogDescription>
                    Map expense category to GL account
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Category
                    </label>
                    <Input
                      value={mappingForm.category}
                      onChange={(e) =>
                        setMappingForm((prev) => ({
                          ...prev,
                          category: e.target.value,
                        }))
                      }
                      placeholder="e.g., Office Supplies"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      GL Account
                    </label>
                    <select
                      value={mappingForm.account_id}
                      onChange={(e) =>
                        setMappingForm((prev) => ({
                          ...prev,
                          account_id: e.target.value,
                        }))
                      }
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="">Select account...</option>
                      {Array.isArray(accountsQuery.data) &&
                        accountsQuery.data
                          .filter(
                            (account: any) =>
                              account.account_type === "expense",
                          )
                          .map((account: any) => (
                            <option key={account.id} value={account.id}>
                              {account.code} - {account.name}
                            </option>
                          ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Description (Optional)
                    </label>
                    <Input
                      value={mappingForm.description}
                      onChange={(e) =>
                        setMappingForm((prev) => ({
                          ...prev,
                          description: e.target.value,
                        }))
                      }
                      placeholder="Enter description"
                    />
                  </div>
                  <Button
                    onClick={handleCreateMapping}
                    disabled={createMappingMutation.isPending}
                    className="w-full"
                  >
                    {createMappingMutation.isPending
                      ? "Creating..."
                      : "Create Mapping"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Category Mappings</CardTitle>
              <CardDescription>
                Expense categories mapped to GL accounts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mappingsQuery.data?.map((mapping) => (
                  <div key={mapping.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{mapping.category}</h3>
                        <p className="text-sm mt-1">
                          {mapping.account_code} - {mapping.account_name}
                        </p>
                        {mapping.description && (
                          <p className="text-xs mt-1">{mapping.description}</p>
                        )}
                      </div>
                      <Badge variant={mapping.active ? "default" : "secondary"}>
                        {mapping.active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>

              {mappingsQuery.isLoading && (
                <div className="text-center py-8">Loading mappings...</div>
              )}

              {!mappingsQuery.isLoading && mappingsQuery.data?.length === 0 && (
                <div className="text-center py-8">No mappings found</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Expenses Tab */}
        <TabsContent value="expenses" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Expenses</CardTitle>
              <CardDescription>View and manage expenses</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-4">Date</th>
                      <th className="text-left py-2 px-4">Category</th>
                      <th className="text-left py-2 px-4">Description</th>
                      <th className="text-right py-2 px-4">Amount</th>
                      <th className="text-left py-2 px-4">Status</th>
                      <th className="text-left py-2 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {expensesQuery.data?.map((expense) => (
                      <tr key={expense.id} className="border-b">
                        <td className="py-2 px-4 text-xs">
                          {format(
                            new Date(expense.expense_date),
                            "MMM dd, yyyy",
                          )}
                        </td>
                        <td className="py-2 px-4 text-xs font-medium">
                          {expense.category}
                        </td>
                        <td className="py-2 px-4 text-xs">
                          {expense.description}
                        </td>
                        <td className="py-2 px-4 text-right text-xs font-medium">
                          ${expense.amount.toFixed(2)}
                        </td>
                        <td className="py-2 px-4">
                          <Badge
                            variant={
                              expense.approval_status === "approved"
                                ? "default"
                                : expense.approval_status === "rejected"
                                  ? "destructive"
                                  : "secondary"
                            }
                          >
                            {expense.approval_status}
                          </Badge>
                        </td>
                        <td className="py-2 px-4">
                          {expense.approval_status === "pending" && (
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleApproveExpense(expense.id)}
                                disabled={approveMutation.isPending}
                              >
                                ✓ Approve
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleRejectExpense(expense.id)}
                                disabled={rejectMutation.isPending}
                              >
                                ✕ Reject
                              </Button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {expensesQuery.isLoading && (
                <div className="text-center py-8">Loading expenses...</div>
              )}

              {!expensesQuery.isLoading && expensesQuery.data?.length === 0 && (
                <div className="text-center py-8">No expenses found</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reconciliation Tab */}
        <TabsContent value="reconciliation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Expense Reconciliation</CardTitle>
              <CardDescription>
                Compare expenses with accounting records
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
                    disabled={expenseReconciliationQuery.isLoading}
                    className="w-full"
                  >
                    Load Reconciliation
                  </Button>
                </div>
              </div>

              {expenseReconciliationQuery.data && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Approved
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {expenseReconciliationQuery.data.approved_expenses.total.toFixed(
                            2,
                          )}
                        </div>
                        <p className="text-xs mt-1">
                          {
                            expenseReconciliationQuery.data.approved_expenses
                              .count
                          }{" "}
                          expenses
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Pending
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {expenseReconciliationQuery.data.pending_expenses.total.toFixed(
                            2,
                          )}
                        </div>
                        <p className="text-xs mt-1">
                          {
                            expenseReconciliationQuery.data.pending_expenses
                              .count
                          }{" "}
                          expenses
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Total
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          $
                          {expenseReconciliationQuery.data.total_expenses.toFixed(
                            2,
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}

              {expenseReconciliationQuery.isLoading && (
                <div className="text-center py-8">
                  Loading reconciliation...
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
