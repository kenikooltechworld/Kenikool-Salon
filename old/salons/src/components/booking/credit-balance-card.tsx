/**
 * CreditBalanceCard Component
 * Displays available credit balance
 */
import React from "react";
import { Card } from "@/components/ui/card";

interface CreditBalanceCardProps {
  availableCredits: number;
}

export const CreditBalanceCard: React.FC<CreditBalanceCardProps> = ({
  availableCredits,
}) => {
  return (
    <Card className="p-4 bg-background">
      <div className="text-sm text-muted-foreground">Available Balance</div>
      <div className="mt-1 text-2xl font-bold text-primary">
        ${availableCredits.toFixed(2)}
      </div>
    </Card>
  );
};

export default CreditBalanceCard;
