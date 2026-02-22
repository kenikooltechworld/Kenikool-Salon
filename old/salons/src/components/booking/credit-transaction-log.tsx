/**
 * CreditTransactionLog Component
 * Displays credit transaction history with type, amount, and date
 * Validates: Requirements 5.5
 */
import React, { useState } from "react";
import {
  ArrowUp,
  ArrowDown,
  Trash2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useCreditTransactionHistory } from "../../lib/api/hooks/usePackageCredits";

interface CreditTransactionLogProps {
  limit?: number;
  showExpanded?: boolean;
}

/**
 * Component for displaying credit transaction history
 */
export const CreditTransactionLog: React.FC<CreditTransactionLogProps> = ({
  limit = 10,
  showExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(showExpanded);
  const { data, isLoading, error } = useCreditTransactionHistory({
    limit,
    offset: 0,
  });

  const transactions = data?.items || [];

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case "purchase":
        return <ArrowDown className="h-4 w-4 text-green-600" />;
      case "redemption":
        return <ArrowUp className="h-4 w-4 text-blue-600" />;
      case "expiration":
        return <Trash2 className="h-4 w-4 text-red-600" />;
      case "refund":
        return <ArrowDown className="h-4 w-4 text-purple-600" />;
      default:
        return null;
    }
  };

  const getTransactionLabel = (type: string) => {
    switch (type) {
      case "purchase":
        return "Purchase";
      case "redemption":
        return "Redeemed";
      case "expiration":
        return "Expired";
      case "refund":
        return "Refund";
      default:
        return type;
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type) {
      case "purchase":
        return "text-green-600";
      case "redemption":
        return "text-blue-600";
      case "expiration":
        return "text-red-600";
      case "refund":
        return "text-purple-600";
      default:
        return "text-gray-600";
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="text-center text-sm text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="text-sm text-red-700">Failed to load transactions</div>
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="text-center text-sm text-gray-500">
          No transactions yet
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-white p-4">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between text-left"
      >
        <h3 className="font-semibold text-gray-900">Transaction History</h3>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-600" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-600" />
        )}
      </button>

      {/* Transactions List */}
      {isExpanded && (
        <div className="space-y-2 border-t border-gray-200 pt-3">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between rounded-lg bg-gray-50 p-3"
            >
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-white p-2">
                  {getTransactionIcon(transaction.type)}
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {getTransactionLabel(transaction.type)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatDate(transaction.created_at)}
                  </div>
                  {transaction.description && (
                    <div className="text-xs text-gray-600">
                      {transaction.description}
                    </div>
                  )}
                </div>
              </div>
              <div
                className={`text-right font-semibold ${getTransactionColor(transaction.type)}`}
              >
                {transaction.type === "purchase" ||
                transaction.type === "refund"
                  ? "+"
                  : "-"}
                ${transaction.amount.toFixed(2)}
              </div>
            </div>
          ))}

          {/* Show More Link */}
          {data && data.total > transactions.length && (
            <button className="w-full rounded-lg border border-gray-200 py-2 text-center text-sm text-blue-600 hover:bg-blue-50">
              View All Transactions
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default CreditTransactionLog;
