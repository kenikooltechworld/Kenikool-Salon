import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useGetTransactions } from "@/lib/api/hooks/usePOS";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { useClients } from "@/lib/api/hooks/useClients";
import { TransactionDetailModal } from "@/components/pos/transaction-detail-modal";
import { SearchIcon, FilterIcon, EyeIcon, RefreshCwIcon } from "@/components/icons";
import { format } from "date-fns";

export default function TransactionsPage() {
  const [selectedTransaction, setSelectedTransaction] = useState<string | null>(
    null
  );
  const [filters, setFilters] = useState({
    date_from: "",
    date_to: "",
    stylist_id: "",
    client_id: "",
    status: "",
  });
  const [searchQuery, setSearchQuery] = useState("");

  const {
    data: transactions = [],
    isLoading,
    refetch,
  } = useGetTransactions(filters);
  const { data: stylistsData } = useStylists();
  const stylists = Array.isArray(stylistsData) ? stylistsData : [];
  const { data: clientsData } = useClients();
  const clients = clientsData?.items || [];

  const filteredTransactions = transactions.filter((t: any) => {
    if (!searchQuery) return true;
    return (
      t.transaction_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.client_id?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<
      string,
      "default" | "secondary" | "destructive" | "outline"
    > = {
      pending: "secondary",
      completed: "default",
      refunded: "destructive",
      partially_refunded: "outline",
      voided: "destructive",
    };
    const labels: Record<string, string> = {
      pending: "PENDING",
      completed: "COMPLETED",
      refunded: "REFUNDED",
      partially_refunded: "PARTIAL REFUND",
      voided: "VOIDED",
    };
    return (
      <Badge variant={variants[status] || "default"}>
        {labels[status] || status.toUpperCase()}
      </Badge>
    );
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Transaction History</h1>
          <p className="text-muted-foreground">
            View and manage all POS transactions
          </p>
        </div>
        <Button onClick={() => refetch()} variant="outline" size="sm">
          <RefreshCwIcon className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FilterIcon className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {/* Search */}
            <div>
              <Label>Search</Label>
              <div className="relative">
                <SearchIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Transaction #..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Date From */}
            <div>
              <Label>From Date</Label>
              <Input
                type="date"
                value={filters.date_from}
                onChange={(e) =>
                  handleFilterChange("date_from", e.target.value)
                }
              />
            </div>

            {/* Date To */}
            <div>
              <Label>To Date</Label>
              <Input
                type="date"
                value={filters.date_to}
                onChange={(e) => handleFilterChange("date_to", e.target.value)}
              />
            </div>

            {/* Stylist */}
            <div>
              <Label>Stylist</Label>
              <Select
                value={filters.stylist_id}
                onValueChange={(value) =>
                  handleFilterChange("stylist_id", value)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Stylists" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Stylists</SelectItem>
                  {stylists.map((stylist: any) => (
                    <SelectItem key={stylist.id} value={stylist.id}>
                      {stylist.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Status */}
            <div>
              <Label>Status</Label>
              <Select
                value={filters.status}
                onValueChange={(value) => handleFilterChange("status", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="refunded">Refunded</SelectItem>
                  <SelectItem value="partially_refunded">
                    Partially Refunded
                  </SelectItem>
                  <SelectItem value="voided">Voided</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Clear Filters */}
          <div className="mt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setFilters({
                  date_from: "",
                  date_to: "",
                  stylist_id: "",
                  client_id: "",
                  status: "",
                });
                setSearchQuery("");
              }}
            >
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Transactions ({filteredTransactions.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">Loading transactions...</div>
          ) : filteredTransactions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No transactions found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction #</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Client</TableHead>
                    <TableHead>Stylist</TableHead>
                    <TableHead>Items</TableHead>
                    <TableHead>Total</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTransactions.map((transaction: any) => (
                    <TableRow key={transaction.id}>
                      <TableCell className="font-medium">
                        {transaction.transaction_number}
                      </TableCell>
                      <TableCell>
                        {format(
                          new Date(transaction.created_at),
                          "MMM dd, yyyy HH:mm"
                        )}
                      </TableCell>
                      <TableCell>
                        {transaction.client_id
                          ? clients.find(
                              (c: any) => c.id === transaction.client_id
                            )?.name || "Unknown"
                          : "Walk-in"}
                      </TableCell>
                      <TableCell>
                        {transaction.stylist_id
                          ? stylists.find(
                              (s: any) => s.id === transaction.stylist_id
                            )?.name || "Unknown"
                          : "-"}
                      </TableCell>
                      <TableCell>{transaction.items.length}</TableCell>
                      <TableCell className="font-bold">
                        ${transaction.total.toFixed(2)}
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(transaction.status)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedTransaction(transaction.id)}
                        >
                          <EyeIcon className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Transaction Detail Modal */}
      <TransactionDetailModal
        transactionId={selectedTransaction}
        open={!!selectedTransaction}
        onClose={() => setSelectedTransaction(null)}
      />
    </div>
  );
}
