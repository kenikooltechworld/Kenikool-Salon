/**
 * CreditBalanceDisplay Component
 * Displays current package credit balance and expiration info
 * Validates: Requirements 5.1
 */
import React from "react";
import { Card } from "@/components/ui/card";
import { GiftIcon, AlertTriangleIcon, CalendarIcon } from "@/components/icons";

interface CreditBalanceDisplayProps {
  balance: number;
  totalPurchased: number;
  expirationDate: string;
  daysUntilExpiration?: number;
  loading?: boolean;
}

/**
 * Component for displaying package credit balance and expiration information
 */
export const CreditBalanceDisplay: React.FC<CreditBalanceDisplayProps> = ({
  balance,
  totalPurchased,
  expirationDate,
  daysUntilExpiration,
  loading = false,
}) => {
  const isExpiringSoon =
    daysUntilExpiration !== undefined && daysUntilExpiration <= 30;
  const isExpired =
    daysUntilExpiration !== undefined && daysUntilExpiration < 0;

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <Card className="p-4 space-y-4 border-primary/20 bg-primary/5">
      <div className="flex items-center gap-2">
        <GiftIcon size={20} className="text-primary" />
        <h3 className="font-semibold text-foreground">Package Credits</h3>
      </div>

      {loading ? (
        <div className="text-center text-sm text-muted-foreground">
          Loading...
        </div>
      ) : (
        <>
          {/* Balance Display */}
          <Card className="p-4 bg-background">
            <div className="text-sm text-muted-foreground">Current Balance</div>
            <div className="mt-1 text-3xl font-bold text-primary">
              ${balance.toFixed(2)}
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Total Purchased: ${totalPurchased.toFixed(2)}
            </div>
          </Card>

          {/* Expiration Info */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CalendarIcon size={16} />
              <span>Expires: {formatDate(expirationDate)}</span>
            </div>

            {isExpired && (
              <div className="flex items-start gap-2 rounded p-2 bg-destructive/10 border border-destructive">
                <AlertTriangleIcon
                  size={16}
                  className="text-destructive flex-shrink-0 mt-0.5"
                />
                <span className="text-sm text-destructive">
                  Your credits have expired
                </span>
              </div>
            )}

            {isExpiringSoon && !isExpired && (
              <div className="flex items-start gap-2 rounded p-2 bg-accent/10 border border-accent">
                <AlertTriangleIcon
                  size={16}
                  className="text-accent flex-shrink-0 mt-0.5"
                />
                <span className="text-sm text-accent-foreground">
                  {daysUntilExpiration === 0
                    ? "Credits expire today"
                    : `Credits expire in ${daysUntilExpiration} days`}
                </span>
              </div>
            )}
          </div>

          {/* Usage Progress */}
          {totalPurchased > 0 && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Used</span>
                <span>
                  ${(totalPurchased - balance).toFixed(2)} / $
                  {totalPurchased.toFixed(2)}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full bg-primary transition-all"
                  style={{
                    width: `${((totalPurchased - balance) / totalPurchased) * 100}%`,
                  }}
                />
              </div>
            </div>
          )}
        </>
      )}
    </Card>
  );
};

export default CreditBalanceDisplay;
