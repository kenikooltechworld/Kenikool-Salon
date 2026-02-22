import { Expense } from "@/lib/api/hooks/useExpenses";
import {
  DollarSignIcon,
  EditIcon,
  TrashIcon,
  CalendarIcon,
} from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface ExpenseListProps {
  expenses: Expense[];
  onEdit: (expense: Expense) => void;
  onDelete: (id: string) => void;
}

export function ExpenseList({ expenses, onEdit, onDelete }: ExpenseListProps) {
  if (expenses.length === 0) {
    return (
      <div className="text-center py-12">
        <DollarSignIcon
          size={48}
          className="mx-auto text-[var(--muted-foreground)] mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No expenses yet</h3>
        <p className="text-[var(--muted-foreground)]">
          Start tracking your business expenses
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {expenses.map((expense) => (
        <Card
          key={expense._id}
          className="p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="p-2 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
                <DollarSignIcon size={20} className="text-[var(--primary)]" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold">{expense.description}</p>
                  <Badge variant="secondary">{expense.category}</Badge>
                </div>
                <div className="flex items-center gap-4 mt-1">
                  <p className="text-sm text-[var(--muted-foreground)] flex items-center gap-1">
                    <CalendarIcon size={14} />
                    {new Date(expense.expense_date).toLocaleDateString()}
                  </p>
                  {expense.payment_method && (
                    <p className="text-sm text-[var(--muted-foreground)]">
                      {expense.payment_method}
                    </p>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <p className="text-lg font-bold text-[var(--primary)]">
                ₦{expense.amount.toFixed(2)}
              </p>
              <Button variant="ghost" size="sm" onClick={() => onEdit(expense)}>
                <EditIcon size={16} />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(expense._id)}
              >
                <TrashIcon size={16} />
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
