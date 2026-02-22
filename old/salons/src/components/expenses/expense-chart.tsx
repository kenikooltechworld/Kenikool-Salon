import { Expense } from "@/lib/api/hooks/useExpenses";
import { ChartIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";

interface ExpenseChartProps {
  expenses: Expense[];
}

export function ExpenseChart({ expenses }: ExpenseChartProps) {
  // Group expenses by category
  const categoryTotals = expenses.reduce((acc, expense) => {
    const category = expense.category || "Uncategorized";
    acc[category] = (acc[category] || 0) + expense.amount;
    return acc;
  }, {} as Record<string, number>);

  const categories = Object.entries(categoryTotals).sort(
    ([, a], [, b]) => b - a
  );
  const maxAmount = Math.max(...Object.values(categoryTotals), 1);

  const totalExpenses = expenses.reduce(
    (sum, expense) => sum + expense.amount,
    0
  );

  if (expenses.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center py-12">
          <ChartIcon
            size={48}
            className="mx-auto text-[var(--muted-foreground)] mb-4"
          />
          <h3 className="text-lg font-semibold mb-2">No expense data</h3>
          <p className="text-[var(--muted-foreground)]">
            Add expenses to see category breakdown
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Expenses by Category</h3>
          <div className="text-right">
            <p className="text-sm text-[var(--muted-foreground)]">Total</p>
            <p className="text-2xl font-bold text-[var(--primary)]">
              ₦{totalExpenses.toFixed(2)}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {categories.map(([category, amount]) => {
            const percentage = (amount / maxAmount) * 100;
            const sharePercentage = (amount / totalExpenses) * 100;

            return (
              <div key={category} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{category}</span>
                  <span className="text-[var(--muted-foreground)]">
                    ₦{amount.toFixed(2)} ({sharePercentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-[var(--muted)] rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-[var(--primary)] h-full rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
