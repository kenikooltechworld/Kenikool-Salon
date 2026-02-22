import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useCommissionTransactions } from "@/lib/api/hooks/useMarketplaceQueries";
import { ChevronLeftIcon, ChevronRightIcon, FilterIcon } from "@/components/icons";

interface CommissionFilter {
  tenantId?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
}

export function CommissionTransactions() {
  const [filters, setFilters] = useState<CommissionFilter>({});
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const { data: transactionsData, isLoading } = useCommissionTransactions({
    ...filters,
    skip: (page - 1) * 50,
    limit: 50,
  });

  const transactions = transactionsData?.transactions || [];
  const total = transactionsData?.total || 0;
  const totalPages = Math.ceil(total / 50);

  const handleFilterChange = (key: keyof CommissionFilter, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
    setPage(1);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "held":
        return "bg-blue-100 text-blue-800";
      case "refunded":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <motion.div
        className="bg-white rounded-lg border border-[var(--border)] p-4"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-[var(--foreground)]">Filters</h3>
          <motion.button
            onClick={() => setShowFilters(!showFilters)}
            className="p-2 hover:bg-[var(--muted)] rounded-lg transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <FilterIcon size={20} />
          </motion.button>
        </div>

        {showFilters && (
          <motion.div
            className="grid grid-cols-1 md:grid-cols-4 gap-4"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
          >
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                Status
              </label>
              <select
                value={filters.status || ""}
                onChange={(e) => handleFilterChange("status", e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none"
              >
                <option value="">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="pending">Pending</option>
                <option value="held">Held</option>
                <option value="refunded">Refunded</option>
              </select>
            </div>

            {/* Date From */}
            <div>
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                From Date
              </label>
              <input
                type="date"
                value={filters.dateFrom || ""}
                onChange={(e) => handleFilterChange("dateFrom", e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none"
              />
            </div>

            {/* Date To */}
            <div>
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                To Date
              </label>
              <input
                type="date"
                value={filters.dateTo || ""}
                onChange={(e) => handleFilterChange("dateTo", e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none"
              />
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <Button
                onClick={() => {
                  setFilters({});
                  setPage(1);
                }}
                variant="outline"
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Transactions Table */}
      <motion.div
        className="bg-white rounded-lg border border-[var(--border)] overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary)] mx-auto mb-4"></div>
              <p className="text-[var(--muted-foreground)]">Loading transactions...</p>
            </div>
          </div>
        ) : transactions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-[var(--muted-foreground)]">No transactions found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-[var(--muted)] border-b border-[var(--border)]">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-[var(--foreground)]">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-[var(--foreground)]">
                      Salon
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-[var(--foreground)]">
                      Type
                    </th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-[var(--foreground)]">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-[var(--foreground)]">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((transaction: any, index: number) => (
                    <motion.tr
                      key={transaction.id}
                      className="border-b border-[var(--border)] hover:bg-[var(--muted)]/50 transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.2 + index * 0.05 }}
                    >
                      <td className="px-6 py-4 text-sm text-[var(--foreground)]">
                        {formatDate(transaction.created_at)}
                      </td>
                      <td className="px-6 py-4 text-sm text-[var(--foreground)]">
                        {transaction.salon_name}
                      </td>
                      <td className="px-6 py-4 text-sm text-[var(--foreground)]">
                        <span className="capitalize">
                          {transaction.transaction_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-right text-[var(--foreground)]">
                        ₦{transaction.amount.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
                            transaction.status
                          )}`}
                        >
                          {transaction.status.charAt(0).toUpperCase() +
                            transaction.status.slice(1)}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <motion.div
              className="flex items-center justify-between px-6 py-4 border-t border-[var(--border)]"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <p className="text-sm text-[var(--muted-foreground)]">
                Showing {(page - 1) * 50 + 1} to{" "}
                {Math.min(page * 50, total)} of {total} transactions
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                >
                  <ChevronLeftIcon size={16} />
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                >
                  Next
                  <ChevronRightIcon size={16} />
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </motion.div>
    </div>
  );
}
