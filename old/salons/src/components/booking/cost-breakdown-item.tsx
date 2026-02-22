/**
 * CostBreakdownItem Component
 * Displays a single line item in the cost breakdown
 */
import React from "react";

interface CostBreakdownItemProps {
  label: string;
  amount: number;
  type?: "normal" | "positive" | "negative";
}

export const CostBreakdownItem: React.FC<CostBreakdownItemProps> = ({
  label,
  amount,
  type = "normal",
}) => {
  const getAmountColor = () => {
    switch (type) {
      case "positive":
        return "text-green-600";
      case "negative":
        return "text-green-600";
      default:
        return "text-muted-foreground";
    }
  };

  const getAmountPrefix = () => {
    switch (type) {
      case "positive":
        return "+";
      case "negative":
        return "-";
      default:
        return "";
    }
  };

  return (
    <div className="flex justify-between text-muted-foreground">
      <span>{label}</span>
      <span className={getAmountColor()}>
        {getAmountPrefix()}${amount.toFixed(2)}
      </span>
    </div>
  );
};

export default CostBreakdownItem;
