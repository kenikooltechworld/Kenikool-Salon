import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  PlusIcon,
  SearchIcon,
  TrashIcon,
  EyeIcon,
  EditIcon,
} from "@/components/icons";
import { useInvoices, useDeleteInvoice } from "@/hooks/useInvoices";
import { formatCurrency, formatDate } from "@/lib/utils/format";

interface InvoiceFilters {
  status?: string;
  customer_id?: string;
}

export default function Invoices() {
  const navigate = useNavigate();
  const [filters] = useState<InvoiceFilters>({});
  const [searchTerm, setSearchTerm] = useState("");
  const { data, isLoading, error } = useInvoices(filters);
  const invoices = data || [];
  const deleteInvoiceMutation = useDeleteInvoice();

  const filteredInvoices = invoices.filter(
    (invoice) =>
      !searchTerm ||
      invoice.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (invoice.customer_id &&
        invoice.customer_id.toLowerCase().includes(searchTerm.toLowerCase())),
  );

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to delete this invoice?")) {
      try {
        await deleteInvoiceMutation.mutateAsync(id);
      } catch (error) {
        alert("Failed to delete invoice");
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200";
      case "issued":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200";
      case "draft":
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
      case "cancelled":
        return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
    }
  };

  const totalAmount = filteredInvoices.reduce((sum, inv) => sum + inv.total, 0);
  const paidAmount = filteredInvoices
    .filter((inv) => inv.status === "paid")
    .reduce((sum, inv) => sum + inv.total, 0);
  const pendingAmount = filteredInvoices
    .filter((inv) => inv.status !== "paid" && inv.status !== "cancelled")
    .reduce((sum, inv) => sum + inv.total, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Invoices</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your salon invoices
          </p>
        </div>
        <Button
          onClick={() => navigate("/invoices/create")}
          className="gap-2 w-full sm:w-auto"
        >
          <PlusIcon size={18} />
          Create Invoice
        </Button>
      </div>

      {/* Summary Cards - Responsive */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
      ) : !error ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Total Amount</p>
            <p className="text-2xl font-bold text-foreground mt-2">
              {formatCurrency(totalAmount)}
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Paid</p>
            <p className="text-2xl font-bold text-green-600 mt-2">
              {formatCurrency(paidAmount)}
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Pending</p>
            <p className="text-2xl font-bold text-yellow-600 mt-2">
              {formatCurrency(pendingAmount)}
            </p>
          </div>
        </div>
      ) : null}

      {/* Error State */}
      {error && (
        <div className="bg-destructive/10 border border-destructive rounded-lg p-4">
          <p className="text-destructive text-sm">
            Failed to load invoices. Please try again.
          </p>
        </div>
      )}

      {/* Search Bar */}
      <div className="relative">
        <SearchIcon
          size={18}
          className="absolute left-3 top-3 text-muted-foreground"
        />
        <input
          type="text"
          placeholder="Search invoices..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Invoices Table - Responsive */}
      {isLoading ? (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="space-y-2 p-4">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </div>
      ) : !error ? (
        <div className="bg-card border border-border rounded-lg overflow-x-auto w-full">
          <table className="w-full">
            <thead className="bg-muted border-b border-border">
              <tr>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Invoice #
                </th>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Customer
                </th>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Amount
                </th>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Date
                </th>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Due Date
                </th>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Status
                </th>
                <th className="px-4 md:px-6 py-3 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredInvoices.length > 0 ? (
                filteredInvoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-muted/50 transition">
                    <td className="px-4 md:px-6 py-4 text-sm font-medium text-foreground whitespace-nowrap">
                      {invoice.id}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-sm text-muted-foreground whitespace-nowrap">
                      {invoice.customer_id}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-sm text-foreground whitespace-nowrap">
                      {formatCurrency(invoice.total)}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-sm text-muted-foreground whitespace-nowrap">
                      {formatDate(new Date(invoice.created_at))}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-sm text-muted-foreground whitespace-nowrap">
                      {formatDate(new Date(invoice.due_date))}
                    </td>
                    <td className="px-4 md:px-6 py-4 text-sm whitespace-nowrap">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                          invoice.status,
                        )}`}
                      >
                        {invoice.status.charAt(0).toUpperCase() +
                          invoice.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-4 md:px-6 py-4 text-sm whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => navigate(`/invoices/${invoice.id}`)}
                          className="p-2 hover:bg-muted rounded-lg transition"
                          title="View"
                        >
                          <EyeIcon
                            size={16}
                            className="text-muted-foreground"
                          />
                        </button>
                        {invoice.status === "draft" && (
                          <button
                            onClick={() =>
                              navigate(`/invoices/${invoice.id}/edit`)
                            }
                            className="p-2 hover:bg-muted rounded-lg transition"
                            title="Edit"
                          >
                            <EditIcon
                              size={16}
                              className="text-muted-foreground"
                            />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(invoice.id)}
                          disabled={deleteInvoiceMutation.isPending}
                          className="p-2 hover:bg-destructive/10 rounded-lg transition disabled:opacity-50"
                          title="Delete"
                        >
                          <TrashIcon size={16} className="text-destructive" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 md:px-6 py-8 text-center text-muted-foreground"
                  >
                    No invoices found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
