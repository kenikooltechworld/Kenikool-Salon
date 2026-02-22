/**
 * CreditExpirationWarning Component
 * Displays warning when credits are expiring soon
 * Validates: Requirements 5.6
 */
import React from "react";
import { AlertTriangle, Clock, TrendingDown } from "lucide-react";
import { useCreditExpirationWarning } from "../../lib/api/hooks/usePackageCredits";

interface CreditExpirationWarningProps {
  onDismiss?: () => void;
  compact?: boolean;
}

/**
 * Component for displaying credit expiration warnings
 */
export const CreditExpirationWarning: React.FC<
  CreditExpirationWarningProps
> = ({ onDismiss, compact = false }) => {
  const { data, isLoading, error } = useCreditExpirationWarning();

  if (isLoading || error || !data?.has_expiring_credits) {
    return null;
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const getWarningLevel = (daysUntilExpiration: number) => {
    if (daysUntilExpiration < 0) return "expired";
    if (daysUntilExpiration === 0) return "today";
    if (daysUntilExpiration <= 7) return "critical";
    if (daysUntilExpiration <= 30) return "warning";
    return "info";
  };

  const warningLevel = getWarningLevel(data.days_until_expiration);

  const getStyles = () => {
    switch (warningLevel) {
      case "expired":
        return {
          container: "border-red-300 bg-red-50",
          icon: "text-red-600",
          title: "text-red-900",
          text: "text-red-800",
          button: "bg-red-600 hover:bg-red-700 text-white",
        };
      case "today":
        return {
          container: "border-red-300 bg-red-50",
          icon: "text-red-600",
          title: "text-red-900",
          text: "text-red-800",
          button: "bg-red-600 hover:bg-red-700 text-white",
        };
      case "critical":
        return {
          container: "border-orange-300 bg-orange-50",
          icon: "text-orange-600",
          title: "text-orange-900",
          text: "text-orange-800",
          button: "bg-orange-600 hover:bg-orange-700 text-white",
        };
      case "warning":
        return {
          container: "border-yellow-300 bg-yellow-50",
          icon: "text-yellow-600",
          title: "text-yellow-900",
          text: "text-yellow-800",
          button: "bg-yellow-600 hover:bg-yellow-700 text-white",
        };
      default:
        return {
          container: "border-blue-300 bg-blue-50",
          icon: "text-blue-600",
          title: "text-blue-900",
          text: "text-blue-800",
          button: "bg-blue-600 hover:bg-blue-700 text-white",
        };
    }
  };

  const styles = getStyles();

  const getWarningMessage = () => {
    if (warningLevel === "expired") {
      return `Your credits expired on ${formatDate(data.expiration_date)}`;
    }
    if (warningLevel === "today") {
      return "Your credits expire today!";
    }
    if (warningLevel === "critical") {
      return `Your credits expire in ${data.days_until_expiration} day${data.days_until_expiration === 1 ? "" : "s"}`;
    }
    return `Your credits expire on ${formatDate(data.expiration_date)}`;
  };

  if (compact) {
    return (
      <div
        className={`flex items-center gap-2 rounded-lg border p-3 ${styles.container}`}
      >
        <AlertTriangle className={`h-4 w-4 flex-shrink-0 ${styles.icon}`} />
        <div className="flex-1">
          <p className={`text-sm font-medium ${styles.title}`}>
            {getWarningMessage()}
          </p>
          <p className={`text-xs ${styles.text}`}>
            ${data.expiring_amount.toFixed(2)} at risk
          </p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className={`text-sm font-medium ${styles.button} rounded px-2 py-1`}
          >
            Dismiss
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`space-y-3 rounded-lg border p-4 ${styles.container}`}>
      {/* Header */}
      <div className="flex items-start gap-3">
        <AlertTriangle className={`h-6 w-6 flex-shrink-0 ${styles.icon}`} />
        <div className="flex-1">
          <h3 className={`font-semibold ${styles.title}`}>
            {warningLevel === "expired"
              ? "Credits Expired"
              : "Credits Expiring Soon"}
          </h3>
          <p className={`mt-1 text-sm ${styles.text}`}>{getWarningMessage()}</p>
        </div>
      </div>

      {/* Details */}
      <div className="space-y-2 rounded bg-white/50 p-3">
        <div className="flex items-center gap-2">
          <TrendingDown className={`h-4 w-4 ${styles.icon}`} />
          <span className={`text-sm ${styles.text}`}>
            Amount at Risk:{" "}
            <span className="font-semibold">
              ${data.expiring_amount.toFixed(2)}
            </span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className={`h-4 w-4 ${styles.icon}`} />
          <span className={`text-sm ${styles.text}`}>
            Expiration Date:{" "}
            <span className="font-semibold">
              {formatDate(data.expiration_date)}
            </span>
          </span>
        </div>
      </div>

      {/* Action */}
      {warningLevel !== "expired" && (
        <button
          className={`w-full rounded-lg px-4 py-2 font-medium transition-colors ${styles.button}`}
        >
          Use Credits Now
        </button>
      )}

      {/* Dismiss */}
      {onDismiss && (
        <button
          onClick={onDismiss}
          className={`w-full rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${styles.text} hover:bg-white/50`}
        >
          Dismiss
        </button>
      )}
    </div>
  );
};

export default CreditExpirationWarning;
