import { Button } from "@/components/ui/button";
import {
  StarIcon,
  ArrowDownIcon,
  ArchiveIcon,
  MonitorIcon,
  ReceiptIcon,
  GiftIcon,
  BarChart3Icon,
  SearchIcon,
  ClipboardListIcon,
} from "@/components/icons";
import { Link } from "react-router-dom";

interface POSHeaderProps {
  cashDrawerStatus?: string;
  onOpenQuickKeys: () => void;
  onOpenCashDrop: () => void;
  onOpenCashDrawer: () => void;
  onCloseCashDrawer: () => void;
  onOpenParkedTransactions?: () => void;
  onOpenCustomerDisplay?: () => void;
  onOpenReceiptCustomization?: () => void;
  onOpenGiftCards?: () => void;
  onOpenTransactionSearch?: () => void;
  onOpenServiceTickets?: () => void;
}

export function POSHeader({
  cashDrawerStatus,
  onOpenQuickKeys,
  onOpenCashDrop,
  onOpenCashDrawer,
  onCloseCashDrawer,
  onOpenParkedTransactions,
  onOpenCustomerDisplay,
  onOpenReceiptCustomization,
  onOpenGiftCards,
  onOpenTransactionSearch,
  onOpenServiceTickets,
}: POSHeaderProps) {
  return (
    <div className="flex items-center justify-between gap-4 flex-wrap">
      <div className="flex-shrink-0">
        <h1 className="text-3xl font-bold">Point of Sale</h1>
        <p className="text-muted-foreground">
          Quick checkout for services and products
        </p>
      </div>
      <div className="flex gap-2 flex-wrap flex-shrink-0">
        <Link to="/dashboard/pos/analytics">
          <Button variant="outline" className="gap-2 whitespace-nowrap">
            <BarChart3Icon className="h-4 w-4 flex-shrink-0" />
            Analytics
          </Button>
        </Link>
        {onOpenGiftCards && (
          <Button
            onClick={onOpenGiftCards}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <GiftIcon className="h-4 w-4 flex-shrink-0" />
            Gift Cards
          </Button>
        )}
        {onOpenTransactionSearch && (
          <Button
            onClick={onOpenTransactionSearch}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <SearchIcon className="h-4 w-4 flex-shrink-0" />
            Search
          </Button>
        )}
        {onOpenServiceTickets && (
          <Button
            onClick={onOpenServiceTickets}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <ClipboardListIcon className="h-4 w-4 flex-shrink-0" />
            Tickets
          </Button>
        )}
        {onOpenReceiptCustomization && (
          <Button
            onClick={onOpenReceiptCustomization}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <ReceiptIcon className="h-4 w-4 flex-shrink-0" />
            Receipt
          </Button>
        )}
        {onOpenCustomerDisplay && (
          <Button
            onClick={onOpenCustomerDisplay}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <MonitorIcon className="h-4 w-4 flex-shrink-0" />
            Display
          </Button>
        )}
        <Button
          onClick={onOpenQuickKeys}
          variant="outline"
          className="gap-2 whitespace-nowrap"
        >
          <StarIcon className="h-4 w-4 flex-shrink-0" />
          Quick Keys
        </Button>
        {onOpenParkedTransactions && (
          <Button
            onClick={onOpenParkedTransactions}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <ArchiveIcon className="h-4 w-4 flex-shrink-0" />
            Parked
          </Button>
        )}
        {cashDrawerStatus === "open" && (
          <Button
            onClick={onOpenCashDrop}
            variant="outline"
            className="gap-2 whitespace-nowrap"
          >
            <ArrowDownIcon className="h-4 w-4 flex-shrink-0" />
            Cash Drop
          </Button>
        )}
        {cashDrawerStatus === "open" ? (
          <Button
            onClick={onCloseCashDrawer}
            variant="outline"
            className="whitespace-nowrap"
          >
            Close Cash Drawer
          </Button>
        ) : (
          <Button
            onClick={onOpenCashDrawer}
            variant="outline"
            className="whitespace-nowrap"
          >
            Open Cash Drawer
          </Button>
        )}
      </div>
    </div>
  );
}
