import { useState } from "react";
import {
  useGetInvoices,
  useGetAgingReport,
} from "@/lib/api/hooks/useAccounting";
import {
  InvoiceList,
  InvoiceFormModal,
  PaymentFormModal,
  AgingReport,
} from "@/components/accounting";
import { DollarSignIcon, PlusIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ReceivablesPage() {
  const { data: invoices = [], isLoading: invoicesLoading } = useGetInvoices();
  const { data: agingData = [], isLoading: agingLoading } = useGetAgingReport();
  const [isInvoiceFormOpen, setIsInvoiceFormOpen] = useState(false);
  const [isPaymentFormOpen, setIsPaymentFormOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  const handleEdit = (invoice: any) => {
    setSelectedInvoice(invoice);
    // For now, we don't support editing invoices, only viewing
  };

  const handleRecordPayment = (invoice: any) => {
    setSelectedInvoice(invoice);
    setIsPaymentFormOpen(true);
  };

  const totalReceivables = invoices.reduce(
    (sum, invoice) => sum + invoice.balance,
    0
  );
  const overdueInvoices = invoices.filter(
    (invoice) => invoice.status === "overdue"
  ).length;

  if (invoicesLoading || agingLoading) {
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
            Accounts Receivable
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Manage invoices and track payments
          </p>
        </div>
        <Button onClick={() => setIsInvoiceFormOpen(true)}>
          <PlusIcon size={20} />
          Create Invoice
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
              <DollarSignIcon size={20} className="text-[var(--primary)]" />
            </div>
            <p className="text-sm text-[var(--muted-foreground)]">
              Total Receivables
            </p>
          </div>
          <p className="text-2xl font-bold">₦{totalReceivables.toFixed(2)}</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary/10 rounded-[var(--radius-md)]">
              <DollarSignIcon size={20} className="text-primary" />
            </div>
            <p className="text-sm text-[var(--muted-foreground)]">
              Total Invoices
            </p>
          </div>
          <p className="text-2xl font-bold">{invoices.length}</p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-destructive/10 rounded-[var(--radius-md)]">
              <DollarSignIcon size={20} className="text-destructive" />
            </div>
            <p className="text-sm text-[var(--muted-foreground)]">
              Overdue Invoices
            </p>
          </div>
          <p className="text-2xl font-bold">{overdueInvoices}</p>
        </Card>
      </div>

      <Tabs defaultValue="invoices" className="space-y-6">
        <TabsList>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="aging">Aging Report</TabsTrigger>
        </TabsList>

        <TabsContent value="invoices">
          <Card className="p-6">
            <InvoiceList
              invoices={invoices}
              onEdit={handleEdit}
              onRecordPayment={handleRecordPayment}
            />
          </Card>
        </TabsContent>

        <TabsContent value="aging">
          <AgingReport data={agingData} />
        </TabsContent>
      </Tabs>

      <InvoiceFormModal
        isOpen={isInvoiceFormOpen}
        onClose={() => setIsInvoiceFormOpen(false)}
      />

      <PaymentFormModal
        isOpen={isPaymentFormOpen}
        onClose={() => {
          setIsPaymentFormOpen(false);
          setSelectedInvoice(null);
        }}
        invoice={selectedInvoice}
      />
    </div>
  );
}
