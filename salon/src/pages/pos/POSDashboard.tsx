import { useState } from "react";
import { useTransactions } from "@/hooks/useCheckout";
import { usePOSStore } from "@/stores/pos";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ChevronDownIcon,
  DollarSignIcon,
  BarChartIcon,
  UsersIcon,
  TagIcon,
  PercentIcon,
  CreditCardIcon,
  HistoryIcon,
} from "@/components/icons";
import TransactionEntry from "@/components/pos/TransactionEntry";
import ReceiptDisplay from "@/components/pos/ReceiptDisplay";
import RefundProcessor from "@/components/pos/RefundProcessor";
import OfflineQueue from "@/components/pos/OfflineQueue";
import POSReports from "./POSReports";
import CommissionDashboard from "./CommissionDashboard";
import DiscountManagement from "./DiscountManagement";
import ReceiptHistory from "./ReceiptHistory";

export default function POSDashboard() {
  const [activeTab, setActiveTab] = useState("transaction");
  const [selectedTransactionId, setSelectedTransactionId] = useState<string>();
  const [showMoreMenu, setShowMoreMenu] = useState(false);
  const { data: transactionsData, isLoading } = useTransactions({
    pageSize: 10,
  });
  const { isOffline, pendingTransactions, syncStatus } = usePOSStore();

  const transactions = transactionsData?.transactions || [];
  const todaysSales = transactions
    .filter(
      (t) => new Date(t.createdAt).toDateString() === new Date().toDateString(),
    )
    .reduce((sum, t) => sum + t.total, 0);
  const avgTransaction =
    transactions.length > 0 ? todaysSales / transactions.length : 0;

  // Primary workflow tabs (most used)
  const primaryTabs = [
    {
      id: "transaction",
      label: "New Transaction",
      icon: DollarSignIcon,
      description: "Create new sale",
    },
    {
      id: "receipts",
      label: "Receipts",
      icon: CreditCardIcon,
      description: "View receipts",
    },
  ];

  // Secondary operations tabs
  const operationsTabs = [
    {
      id: "refunds",
      label: "Refunds",
      icon: PercentIcon,
      description: "Process refunds",
    },
    {
      id: "discounts",
      label: "Discounts",
      icon: TagIcon,
      description: "Manage discounts",
    },
  ];

  // Analytics tabs
  const analyticsTabs = [
    {
      id: "receipt-history",
      label: "History",
      icon: HistoryIcon,
      description: "Receipt history",
    },
    {
      id: "commissions",
      label: "Commissions",
      icon: UsersIcon,
      description: "Staff commissions",
    },
    {
      id: "reports",
      label: "Reports",
      icon: BarChartIcon,
      description: "Analytics & reports",
    },
  ];

  const renderTabButton = (tab: any, showLabel = true, expand = false) => {
    const Icon = tab.icon;
    const isActive = activeTab === tab.id;
    return (
      <button
        key={tab.id}
        onClick={() => {
          setActiveTab(tab.id);
          setShowMoreMenu(false);
        }}
        className={`flex items-center justify-center gap-1.5 px-2 py-2 md:px-3 md:py-2.5 lg:px-4 lg:py-2.5 rounded-lg transition-all cursor-pointer ${
          expand ? "flex-1" : "whitespace-nowrap min-w-fit"
        } ${
          isActive
            ? "bg-primary text-primary-foreground shadow-md"
            : "text-muted-foreground hover:text-foreground hover:bg-muted"
        }`}
        title={tab.description}
      >
        <Icon size={16} className="md:size-[18px]" />
        {showLabel && (
          <span className="hidden md:inline text-xs md:text-sm font-medium">
            {tab.label}
          </span>
        )}
      </button>
    );
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {isLoading ? (
          <>
            <Card className="p-6">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-32" />
            </Card>
            <Card className="p-6">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-32" />
            </Card>
            <Card className="p-6">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-32" />
            </Card>
          </>
        ) : (
          <>
            <Card className="p-6">
              <p className="text-sm text-muted-foreground mb-2">
                Today's Sales
              </p>
              <p className="text-3xl font-bold text-foreground">
                ₦
                {todaysSales.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-muted-foreground mb-2">Transactions</p>
              <p className="text-3xl font-bold text-foreground">
                {transactions.length}
              </p>
            </Card>
            <Card className="p-6">
              <p className="text-sm text-muted-foreground mb-2">
                Average Transaction
              </p>
              <p className="text-3xl font-bold text-foreground">
                ₦
                {avgTransaction.toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </p>
            </Card>
          </>
        )}
      </div>

      {/* Status Badges */}
      <div className="flex items-center gap-3 flex-wrap">
        {isOffline && (
          <Badge variant="destructive" className="flex items-center gap-2">
            <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
            Offline Mode
          </Badge>
        )}
        {syncStatus === "syncing" && (
          <Badge variant="secondary" className="flex items-center gap-2">
            <Spinner className="w-3 h-3" />
            Syncing...
          </Badge>
        )}
        {pendingTransactions.length > 0 && (
          <Badge variant="outline">{pendingTransactions.length} pending</Badge>
        )}
      </div>

      {/* Offline Queue Display */}
      {pendingTransactions.length > 0 && <OfflineQueue />}

      {/* Professional Tab Navigation */}
      <div className="space-y-2 md:space-y-3">
        {/* Primary Tabs - Always visible */}
        <div className="flex gap-1 md:gap-2">
          {primaryTabs.map((tab) => renderTabButton(tab, true, true))}
        </div>

        {/* Secondary Tabs - Visible on md and up, icons only on mobile */}
        <div className="flex gap-1 md:gap-2">
          {operationsTabs.map((tab) => renderTabButton(tab, true, true))}
        </div>

        {/* Analytics Tabs + More Menu - Responsive layout */}
        <div className="flex gap-1 md:gap-2">
          {/* Show first 2 analytics tabs on md and up, hide on mobile */}
          <div className="hidden md:flex gap-1 md:gap-2 flex-1">
            {analyticsTabs
              .slice(0, 2)
              .map((tab) => renderTabButton(tab, true, true))}
          </div>

          {/* More Menu - Always visible, contains all analytics on mobile */}
          <div className="relative flex-1 md:flex-none">
            <button
              onClick={() => setShowMoreMenu(!showMoreMenu)}
              className={`w-full md:w-auto flex items-center justify-center gap-1 px-2 py-2 md:px-3 md:py-2.5 lg:px-4 lg:py-2.5 rounded-lg transition-all cursor-pointer ${
                showMoreMenu
                  ? "bg-primary text-primary-foreground shadow-md"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              <span className="text-xs md:text-sm font-medium">More</span>
              <ChevronDownIcon
                size={14}
                className={`md:size-[16px] transition-transform ${
                  showMoreMenu ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* Dropdown Menu */}
            {showMoreMenu && (
              <div className="absolute top-full left-0 right-0 md:left-0 md:right-auto mt-2 bg-background border border-border rounded-lg shadow-lg z-50 min-w-44 md:min-w-48">
                {/* On mobile, show all analytics tabs. On md+, show only the 3rd tab */}
                {analyticsTabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => {
                        setActiveTab(tab.id);
                        setShowMoreMenu(false);
                      }}
                      className={`w-full flex items-center gap-2 md:gap-3 px-3 md:px-4 py-2 md:py-3 text-left transition-colors cursor-pointer ${
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "text-foreground hover:bg-muted"
                      }`}
                    >
                      <Icon size={16} className="md:size-[18px]" />
                      <div>
                        <p className="text-xs md:text-sm font-medium">
                          {tab.label}
                        </p>
                        <p className="text-xs text-muted-foreground hidden md:block">
                          {tab.description}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="mt-8">
        {/* Transaction Tab */}
        {activeTab === "transaction" && <TransactionEntry />}

        {/* Receipts Tab */}
        {activeTab === "receipts" && (
          <div className="space-y-4">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : transactions.length === 0 ? (
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">No transactions yet</p>
              </Card>
            ) : (
              <div className="space-y-3">
                {transactions.map((transaction) => (
                  <Card
                    key={transaction.id}
                    className="p-4 cursor-pointer hover:bg-muted transition"
                    onClick={() => setSelectedTransactionId(transaction.id)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-foreground">
                          {transaction.customerId}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(transaction.createdAt).toLocaleString(
                            "en-NG",
                            {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            },
                          )}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-foreground">
                          ₦
                          {transaction.total.toLocaleString("en-NG", {
                            maximumFractionDigits: 2,
                          })}
                        </p>
                        <Badge
                          variant={
                            transaction.paymentStatus === "completed"
                              ? "default"
                              : "secondary"
                          }
                        >
                          {transaction.paymentStatus}
                        </Badge>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
            {selectedTransactionId && (
              <ReceiptDisplay transactionId={selectedTransactionId} />
            )}
          </div>
        )}

        {/* Refunds Tab */}
        {activeTab === "refunds" && <RefundProcessor />}

        {/* Discounts Tab */}
        {activeTab === "discounts" && <DiscountManagement />}

        {/* Commissions Tab */}
        {activeTab === "commissions" && <CommissionDashboard />}

        {/* Receipt History Tab */}
        {activeTab === "receipt-history" && <ReceiptHistory />}

        {/* Reports Tab */}
        {activeTab === "reports" && <POSReports />}
      </div>
    </div>
  );
}
