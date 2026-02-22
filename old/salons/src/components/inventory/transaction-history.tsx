import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";

interface Transaction {
  _id: string;
  product_id: string;
  transaction_type: string;
  quantity_before: number;
  quantity_after: number;
  quantity_changed: number;
  user_id: string;
  reason?: string;
  reference_id?: string;
  created_at: string;
}

interface TransactionHistoryProps {
  productId?: string;
}

export function TransactionHistory({ productId }: TransactionHistoryProps) {
  const { toast } = useToast();
  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    transactionType: "",
  });
  const [page, setPage] = useState(1);

  const { data: response, isLoading } = useQuery({
    queryKey: ["transactions", productId, filters, page],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (productId) params.append("product_id", productId);
      if (filters.startDate) params.append("start_date", filters.startDate);
      if (filters.endDate) params.append("end_date", filters.endDate);
      if (filters.transactionType) params.append("transaction_type", filters.transactionType);
      params.append("skip", ((page - 1) * 50).toString());
      params.append("limit", "50");

      const endpoint = productId
        ? `/api/inventory/products/${productId}/transactions?${params}`
        : `/api/inventory/transactions?${params}`;

      const res = await apiClient.get(endpoint);
      return res.data;
    },
  });

  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      if (productId) params.append("product_id", productId);
      if (filters.startDate) params.append("start_date", filters.startDate);
      if (filters.endDate) params.append("end_date", filters.endDate);

      const res = await apiClient.post(`/api/inventory/transactions/export?${params}`);
      
      // Create download link
      const element = document.createElement("a");
      element.setAttribute("href", "data:text/csv;charset=utf-8," + encodeURIComponent(res.data.csv));
      element.setAttribute("download", res.data.filename);
      element.style.display = "none";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

      toast("Transactions exported successfully", "success");
    } catch (error) {
      toast("Failed to export transactions", "error");
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type) {
      case "add":
        return "text-green-600";
      case "remove":
      case "service_usage":
      case "pos_sale":
        return "text-red-600";
      case "waste":
        return "text-orange-600";
      case "transfer":
        return "text-blue-600";
      default:
        return "text-gray-600";
    }
  };

  const transactions = response?.transactions || [];
  const totalCount = response?.total_count || 0;
  const totalPages = Math.ceil(totalCount / 50);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-[var(--foreground)]">
                Start Date
              </label>
              <Input
                type="date"
                value={filters.startDate}
                onChange={(e) => {
                  setFilters({ ...filters, startDate: e.target.value });
                  setPage(1);
                }}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[var(--foreground)]">
                End Date
              </label>
              <Input
                type="date"
                value={filters.endDate}
                onChange={(e) => {
                  setFilters({ ...filters, endDate: e.target.value });
                  setPage(1);
                }}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-[var(--foreground)]">
                Transaction Type
              </label>
              <select
                value={filters.transactionType}
                onChange={(e) => {
                  setFilters({ ...filters, transactionType: e.target.value });
                  setPage(1);
                }}
                className="w-full mt-1 p-2 border border-[var(--border)] rounded"
              >
                <option value="">All Types</option>
                <option value="add">Add</option>
                <option value="remove">Remove</option>
                <option value="service_usage">Service Usage</option>
                <option value="pos_sale">POS Sale</option>
                <option value="waste">Waste</option>
                <option value="transfer">Transfer</option>
              </select>
            </div>
          </div>
          <Button onClick={handleExport} variant="secondary">
            Export to CSV
          </Button>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Transaction History</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p className="text-[var(--muted-foreground)]">Loading transactions...</p>
          ) : transactions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    <th className="text-left py-2 px-2">Date</th>
                    <th className="text-left py-2 px-2">Type</th>
                    <th className="text-left py-2 px-2">Before</th>
                    <th className="text-left py-2 px-2">After</th>
                    <th className="text-left py-2 px-2">Changed</th>
                    <th className="text-left py-2 px-2">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx: Transaction) => (
                    <tr key={tx._id} className="border-b border-[var(--border)]">
                      <td className="py-2 px-2 text-xs">
                        {new Date(tx.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-2 px-2">
                        <Badge variant="secondary" className={getTransactionColor(tx.transaction_type)}>
                          {tx.transaction_type}
                        </Badge>
                      </td>
                      <td className="py-2 px-2">{tx.quantity_before}</td>
                      <td className="py-2 px-2">{tx.quantity_after}</td>
                      <td className={`py-2 px-2 font-semibold ${getTransactionColor(tx.transaction_type)}`}>
                        {tx.quantity_changed > 0 ? "+" : ""}{tx.quantity_changed}
                      </td>
                      <td className="py-2 px-2 text-xs text-[var(--muted-foreground)]">
                        {tx.reason || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-[var(--muted-foreground)]">No transactions found</p>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-[var(--border)]">
              <p className="text-sm text-[var(--muted-foreground)]">
                Page {page} of {totalPages} ({totalCount} total)
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  variant="outline"
                  size="sm"
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  variant="outline"
                  size="sm"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
