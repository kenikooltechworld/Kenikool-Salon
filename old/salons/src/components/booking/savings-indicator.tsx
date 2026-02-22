/**
 * SavingsIndicator Component
 * Displays the total savings from discounts and credits
 */
import React from "react";
import { Card } from "@/components/ui/card";

interface SavingsIndicatorProps {
  discount: number;
  creditsApplied: number;
}

export const SavingsIndicator: React.FC<SavingsIndicatorProps> = ({
  discount,
  creditsApplied,
}) => {
  const totalSavings = discount + creditsApplied;

  if (totalSavings <= 0) {
    return null;
  }

  return (
    <Card className="p-3 bg-green-50 border-green-200">
      <div className="text-sm text-green-900">
        <strong>You save:</strong> ${totalSavings.toFixed(2)}
      </div>
    </Card>
  );
};

export default SavingsIndicator;
