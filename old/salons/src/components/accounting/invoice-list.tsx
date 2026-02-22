import { Invoice } from "@/lib/api/hooks/useAccounting";
import { DollarSignIcon, EditIcon, CalendarIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface InvoiceListProps {
  invoices: Invoice[];
  onEdit: (invoice: Invoice) => void;
  onRecordPayment: (invoice: Invoice) => void;
}

export function InvoiceList({
  invoices,
  onEdit,
  onRecordPayment,
}: InvoiceListProps) {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case "paid":
        return "success";
      case "partial":
        return "warning";
      case "overdue":
        return "destructive";
      default:
        return "secondary";
    }
  };

  if (invoices.length === 0) {
    return (
      <div className="text-center py-12">
        <DollarSignIcon
          size={48}
          className="mx-auto text-[var(--muted-foreground)] mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No invoices yet</h3>
        <p className="text-[var(--muted-foreground)]">
          Create your first invoice to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {invoices.map((invoice) => (
        <Card
          key={invoice.id}
          className="p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="p-2 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
                <DollarSignIcon size={20} className="text-[var(--primary)]" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold">{invoice.invoice_number}</p>
                  <Badge variant={getStatusVariant(invoice.status)}>
                    {invoice.status}
                  </Badge>
                </div>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {invoice.client_name || `Client ID: ${invoice.client_id}`}
                </p>
                <div className="flex items-center gap-4 mt-1">
                  <p className="text-sm text-[var(--muted-foreground)] flex items-center gap-1">
                    <CalendarIcon size={14} />
                    Due: {new Date(invoice.due_date).toLocaleDateString()}
                  </p>
                  {invoice.amount_due > 0 && (
                    <p className="text-sm font-semibold">
                      Balance: ₦{invoice.amount_due.toFixed(2)}
                    </p>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-lg font-bold text-[var(--primary)]">
                  ₦{invoice.total.toFixed(2)}
                </p>
                {invoice.amount_paid > 0 && (
                  <p className="text-sm">
                    Paid: ₦{invoice.amount_paid.toFixed(2)}
                  </p>
                )}
              </div>
              {invoice.status !== "paid" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRecordPayment(invoice)}
                >
                  Record Payment
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={() => onEdit(invoice)}>
                <EditIcon size={16} />
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
