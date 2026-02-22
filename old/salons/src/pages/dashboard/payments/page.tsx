import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DollarSignIcon,
  SearchIcon,
  FilterIcon,
  DownloadIcon,
  CheckCircleIcon,
  ClockIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import {
  usePayments,
  type AdvancedPaymentFilters,
} from "@/lib/api/hooks/usePayments";
import { Payment } from "@/lib/api/types";
import {
  exportPaymentsToCSV,
  exportPaymentsToExcel,
  exportPaymentsToPDF,
} from "@/lib/utils/export-payments";
import { ManualPaymentModal } from "@/components/payments/ManualPaymentModal";
import {
  AdvancedFiltersPanel,
  type AdvancedFilters,
} from "@/components/payments/AdvancedFiltersPanel";

type PaymentStatus = "all" | "completed" | "pending" | "failed";

export default function PaymentsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Initialize state from URL query parameters
  const [searchQuery, setSearchQuery] = useState(
    searchParams.get("search") || "",
  );
  const [statusFilter, setStatusFilter] = useState<PaymentStatus>(
    (searchParams.get("status") as PaymentStatus) || "all",
  );
  const [dateRange, setDateRange] = useState<
    "all" | "today" | "week" | "month"
  >((searchParams.get("dateRange") as any) || "all");
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showManualPaymentModal, setShowManualPaymentModal] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Parse advanced filters from URL
  const parseAdvancedFilters = (): AdvancedFilters => {
    return {
      paymentTypes:
        searchParams.get("paymentTypes")?.split(",").filter(Boolean) || [],
      minAmount: searchParams.get("minAmount")
        ? parseFloat(searchParams.get("minAmount")!)
        : undefined,
      maxAmount: searchParams.get("maxAmount")
        ? parseFloat(searchParams.get("maxAmount")!)
        : undefined,
      customerEmail: searchParams.get("customerEmail") || undefined,
      statuses: searchParams.get("statuses")?.split(",").filter(Boolean) || [],
      gateways: searchParams.get("gateways")?.split(",").filter(Boolean) || [],
    };
  };

  const [advancedFilters, setAdvancedFilters] = useState<AdvancedFilters>(
    parseAdvancedFilters(),
  );

  const { data: payments, isLoading, error } = usePayments();

  // Update URL query parameters when filters change
  const updateQueryParams = (
    newFilters: Partial<{
      search: string;
      status: PaymentStatus;
      dateRange: string;
      advancedFilters: AdvancedFilters;
    }>,
  ) => {
    const params = new URLSearchParams(searchParams.toString());

    if (newFilters.search !== undefined) {
      if (newFilters.search) {
        params.set("search", newFilters.search);
      } else {
        params.delete("search");
      }
    }

    if (newFilters.status !== undefined) {
      if (newFilters.status !== "all") {
        params.set("status", newFilters.status);
      } else {
        params.delete("status");
      }
    }

    if (newFilters.dateRange !== undefined) {
      if (newFilters.dateRange !== "all") {
        params.set("dateRange", newFilters.dateRange);
      } else {
        params.delete("dateRange");
      }
    }

    if (newFilters.advancedFilters) {
      const filters = newFilters.advancedFilters;
      if (filters.paymentTypes?.length) {
        params.set("paymentTypes", filters.paymentTypes.join(","));
      } else {
        params.delete("paymentTypes");
      }
      if (filters.minAmount !== undefined) {
        params.set("minAmount", filters.minAmount.toString());
      } else {
        params.delete("minAmount");
      }
      if (filters.maxAmount !== undefined) {
        params.set("maxAmount", filters.maxAmount.toString());
      } else {
        params.delete("maxAmount");
      }
      if (filters.customerEmail) {
        params.set("customerEmail", filters.customerEmail);
      } else {
        params.delete("customerEmail");
      }
      if (filters.statuses?.length) {
        params.set("statuses", filters.statuses.join(","));
      } else {
        params.delete("statuses");
      }
      if (filters.gateways?.length) {
        params.set("gateways", filters.gateways.join(","));
      } else {
        params.delete("gateways");
      }
    }

    router.push(`?${params.toString()}`);
  };

  const handleExport = async (format: "csv" | "excel" | "pdf") => {
    if (!filteredPayments || filteredPayments.length === 0) {
      showToast("No payments to export", "warning");
      return;
    }

    try {
      const filename = `payments-${new Date().toISOString().split("T")[0]}`;

      if (format === "csv") {
        await exportPaymentsToCSV(filteredPayments, filename);
      } else if (format === "excel") {
        await exportPaymentsToExcel(filteredPayments, filename);
      } else if (format === "pdf") {
        await exportPaymentsToPDF(filteredPayments, filename);
      }

      setShowExportMenu(false);
    } catch (error) {
      console.error("Export failed:", error);
      showToast("Failed to export payments", "error");
    }
  };

  // Filter payments based on search and filters
  const filteredPayments = payments?.filter((payment) => {
    const matchesSearch =
      searchQuery === "" ||
      payment.reference?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payment.booking_id?.toString().includes(searchQuery);

    const matchesStatus =
      statusFilter === "all" || payment.status === statusFilter;

    // Date filtering logic
    let matchesDate = true;
    if (dateRange !== "all" && payment.created_at) {
      const paymentDate = new Date(payment.created_at);
      const now = new Date();
      const daysDiff = Math.floor(
        (now.getTime() - paymentDate.getTime()) / (1000 * 60 * 60 * 24),
      );

      if (dateRange === "today") matchesDate = daysDiff === 0;
      else if (dateRange === "week") matchesDate = daysDiff <= 7;
      else if (dateRange === "month") matchesDate = daysDiff <= 30;
    }

    // Advanced filters logic
    let matchesAdvancedFilters = true;

    // Payment type filter
    if (advancedFilters.paymentTypes.length > 0) {
      matchesAdvancedFilters =
        matchesAdvancedFilters &&
        advancedFilters.paymentTypes.includes(payment.payment_type || "");
    }

    // Amount range filter
    if (advancedFilters.minAmount !== undefined) {
      matchesAdvancedFilters =
        matchesAdvancedFilters &&
        (payment.amount || 0) >= advancedFilters.minAmount;
    }
    if (advancedFilters.maxAmount !== undefined) {
      matchesAdvancedFilters =
        matchesAdvancedFilters &&
        (payment.amount || 0) <= advancedFilters.maxAmount;
    }

    // Customer email filter
    if (advancedFilters.customerEmail) {
      // This would require customer data from the payment detail
      // For now, we'll skip this filter as it requires additional data
    }

    // Status filter (advanced)
    if (advancedFilters.statuses.length > 0) {
      matchesAdvancedFilters =
        matchesAdvancedFilters &&
        advancedFilters.statuses.includes(payment.status || "");
    }

    // Gateway filter
    if (advancedFilters.gateways.length > 0) {
      matchesAdvancedFilters =
        matchesAdvancedFilters &&
        advancedFilters.gateways.includes(payment.gateway || "");
    }

    return (
      matchesSearch && matchesStatus && matchesDate && matchesAdvancedFilters
    );
  });

  // Calculate statistics
  const stats = {
    total: filteredPayments?.reduce((sum, p) => sum + (p.amount || 0), 0) || 0,
    completed:
      filteredPayments?.filter((p) => p.status === "completed").length || 0,
    pending:
      filteredPayments?.filter((p) => p.status === "pending").length || 0,
    failed: filteredPayments?.filter((p) => p.status === "failed").length || 0,
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon size={20} className="text-green-500" />;
      case "pending":
        return <ClockIcon size={20} className="text-yellow-500" />;
      case "failed":
        return <AlertTriangleIcon size={20} className="text-red-500" />;
      default:
        return <ClockIcon size={20} className="text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600 bg-green-50 dark:bg-green-900/20";
      case "pending":
        return "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20";
      case "failed":
        return "text-red-600 bg-red-50 dark:bg-red-900/20";
      default:
        return "text-gray-600 bg-gray-50 dark:bg-gray-900/20";
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-NG", {
      style: "currency",
      currency: "NGN",
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Payments</h1>
          <p className="text-muted-foreground">
            Track and manage all payment transactions
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setShowManualPaymentModal(true)}
            variant="primary"
          >
            Record Payment
          </Button>
          <div className="relative">
            <Button
              variant="outline"
              onClick={() => setShowExportMenu(!showExportMenu)}
            >
              <DownloadIcon size={20} />
              Export
            </Button>
            {showExportMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-[var(--border)] rounded-lg shadow-lg z-10">
                <button
                  onClick={() => handleExport("csv")}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-foreground"
                >
                  Export as CSV
                </button>
                <button
                  onClick={() => handleExport("excel")}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-foreground"
                >
                  Export as Excel
                </button>
                <button
                  onClick={() => handleExport("pdf")}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-foreground"
                >
                  Export as PDF
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Revenue</p>
              <p className="text-2xl font-bold text-foreground">
                {formatCurrency(stats.total)}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
              <DollarSignIcon size={24} className="text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold text-foreground">
                {stats.completed}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
              <CheckCircleIcon size={24} className="text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Pending</p>
              <p className="text-2xl font-bold text-foreground">
                {stats.pending}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/20 flex items-center justify-center">
              <ClockIcon size={24} className="text-yellow-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Failed</p>
              <p className="text-2xl font-bold text-foreground">
                {stats.failed}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
              <AlertTriangleIcon size={24} className="text-red-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <SearchIcon
                size={20}
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
              />
              <Input
                placeholder="Search by reference or booking ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="flex gap-2">
            <Button
              variant={statusFilter === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setStatusFilter("all")}
            >
              All
            </Button>
            <Button
              variant={statusFilter === "completed" ? "default" : "outline"}
              size="sm"
              onClick={() => setStatusFilter("completed")}
            >
              Completed
            </Button>
            <Button
              variant={statusFilter === "pending" ? "default" : "outline"}
              size="sm"
              onClick={() => setStatusFilter("pending")}
            >
              Pending
            </Button>
            <Button
              variant={statusFilter === "failed" ? "default" : "outline"}
              size="sm"
              onClick={() => setStatusFilter("failed")}
            >
              Failed
            </Button>
          </div>

          {/* Date Range Filter */}
          <div className="flex gap-2">
            <Button
              variant={dateRange === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("all")}
            >
              All Time
            </Button>
            <Button
              variant={dateRange === "today" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("today")}
            >
              Today
            </Button>
            <Button
              variant={dateRange === "week" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("week")}
            >
              Week
            </Button>
            <Button
              variant={dateRange === "month" ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange("month")}
            >
              Month
            </Button>
          </div>

          {/* Advanced Filters Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          >
            <FilterIcon size={16} className="mr-2" />
            Advanced Filters
          </Button>
        </div>

        {/* Advanced Filters Panel */}
        {showAdvancedFilters && (
          <div className="mt-4 pt-4 border-t">
            <AdvancedFiltersPanel
              filters={advancedFilters}
              onFiltersChange={setAdvancedFilters}
              onClose={() => setShowAdvancedFilters(false)}
            />
          </div>
        )}
      </Card>

      {/* Payments List */}
      <Card>
        {isLoading ? (
          <div className="flex justify-center items-center p-12">
            <Spinner size="lg" />
          </div>
        ) : error ? (
          <div className="p-6">
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="font-medium">Error loading payments</p>
                <p className="text-sm">
                  {error.response?.data?.detail || error.message}
                </p>
              </div>
            </Alert>
          </div>
        ) : filteredPayments && filteredPayments.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Reference
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Booking ID
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Amount
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Gateway
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Status
                  </th>
                  <th className="text-left p-4 text-sm font-medium text-muted-foreground">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredPayments.map((payment) => (
                  <tr
                    key={payment.id}
                    className="hover:bg-muted/30 transition-colors"
                  >
                    <td className="p-4">
                      <p className="font-mono text-sm text-foreground">
                        {payment.reference || "N/A"}
                      </p>
                    </td>
                    <td className="p-4">
                      <p className="text-sm text-foreground">
                        #{payment.booking_id || "N/A"}
                      </p>
                    </td>
                    <td className="p-4">
                      <p className="font-semibold text-foreground">
                        {formatCurrency(payment.amount || 0)}
                      </p>
                    </td>
                    <td className="p-4">
                      <p className="text-sm text-muted-foreground capitalize">
                        {payment.gateway || "N/A"}
                      </p>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(payment.status || "")}
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                            payment.status || "",
                          )}`}
                        >
                          {payment.status || "Unknown"}
                        </span>
                      </div>
                    </td>
                    <td className="p-4">
                      <p className="text-sm text-muted-foreground">
                        {payment.created_at
                          ? formatDate(payment.created_at)
                          : "N/A"}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center p-12">
            <DollarSignIcon
              size={48}
              className="mx-auto mb-4 text-muted-foreground"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No payments found
            </h3>
            <p className="text-muted-foreground">
              {searchQuery || statusFilter !== "all" || dateRange !== "all"
                ? "Try adjusting your filters"
                : "Payments will appear here once customers make bookings"}
            </p>
          </div>
        )}
      </Card>

      {/* Manual Payment Modal */}
      <ManualPaymentModal
        isOpen={showManualPaymentModal}
        onClose={() => setShowManualPaymentModal(false)}
        onSuccess={() => {
          setShowManualPaymentModal(false);
          // Payments will be refetched automatically via React Query
        }}
      />
    </div>
  );
}
