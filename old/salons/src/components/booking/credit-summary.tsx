/**
 * CreditSummary Component
 * Displays summary of credit application
 */
import React from "react";
import { Card } from "@/components/ui/card";

interface CreditSummaryProps {
  bookingTotal: number;
  creditsApplied: number;
  remainingBalance: number;
}

export const CreditSummary: React.FC<CreditSummaryProps> = ({
  bookingTotal,
  creditsApplied,
  remainingBalance,
}) => {
  const finalTotal = Math.max(0, bookingTotal - creditsApplied);

  return (
    <Card className="p-3 bg-muted/50 space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">Booking Total</span>
        <span className="font-medium">${bookingTotal.toFixed(2)}</span>
      </div>
      {creditsApplied > 0 && (
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Credits Applied</span>
          <span className="font-medium text-green-600">
            -${creditsApplied.toFixed(2)}
          </span>
        </div>
      )}
      <div className="border-t pt-2 flex justify-between font-semibold">
        <span>Final Total</span>
        <span className="text-lg">${finalTotal.toFixed(2)}</span>
      </div>
      {remainingBalance > 0 && (
        <div className="text-xs text-muted-foreground">
          Remaining balance: ${remainingBalance.toFixed(2)}
        </div>
      )}
    </Card>
  );
};

export default CreditSummary;
