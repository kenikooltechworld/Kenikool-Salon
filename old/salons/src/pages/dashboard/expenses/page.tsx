import { useState } from "react";
import { useGetExpenses, useDeleteExpense, ExpenseFilters, Expense } from "@/lib/api/hooks/useExpenses";
import {
  ExpenseList,
  ExpenseFormModal,
  ExpenseChart,
  ExpenseFilters as ExpenseFiltersComponent,
  PaginationControls,
  FinancialReports,
} from "@/components/expenses";
import { DollarSignIcon, PlusIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { showToast } from "@/lib/utils/toast";

export default function ExpensesPage() {
  const [filters, setFilters] = useState<ExpenseFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const queryFilters: ExpenseFilters = {
    ...filters,
    skip: (currentPage - 1) * pageSize,
    limit: pageSize,
  };

  const { data: response, isLoading } = useGetExpenses(queryFilters);
  const expenses = response?.expenses || [];
  const total = response?.total || 0;

  const deleteMutation = useDeleteExpense();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);

  const handleEdit = (expense: Expense) => {
    setSelectedExpense(expense);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this expense?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      showToast("Expense deleted successfully", "success");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to delete expense";
      showToast(errorMessage, "error");
    }
  };

  const handleFiltersChange = (newFilters: ExpenseFilters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <DollarSignIcon size={32} className="text-[var(--primary)]" />
            Expenses
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Track and manage your business expenses
          </p>
        </div>
        <Button
          onClick={() => {
            setSelectedExpense(null);
            setIsFormOpen(true);
          }}
        >
          <PlusIcon size={20} />
          Add Expense
        </Button>
      </div>

      <ExpenseFiltersComponent
        filters={filters}
        onFiltersChange={handleFiltersChange}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="p-6">
            <ExpenseList
              expenses={expenses}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          </Card>
        </div>

        <div className="lg:col-span-1">
          <ExpenseChart expenses={expenses} />
        </div>
      </div>

      <PaginationControls
        currentPage={currentPage}
        pageSize={pageSize}
        total={total}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
      />

      <FinancialReports />

      <ExpenseFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedExpense(null);
        }}
        expense={selectedExpense}
      />
    </div>
  );
}
