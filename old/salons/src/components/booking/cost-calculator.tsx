/**
 * CostCalculator Component
 * Calculates and displays booking cost with breakdown
 * Validates: Requirements 3.2, 13.4
 * Property 4: Cost Calculation Accuracy
 * Property 20: Service Variant Cost Update
 * Property 21: Add-On Cost Accumulation
 */
import React, { useMemo } from "react";
import { Card } from "@/components/ui/card";
import { DollarSignIcon } from "@/components/icons";
import { CostBreakdownItem } from "./cost-breakdown-item";
import { CostSummaryTotal } from "./cost-summary-total";
import { SavingsIndicator } from "./savings-indicator";

interface CostCalculatorProps {
  subtotal: number;
  variantCost?: number;
  addOnsCost?: number;
  discount?: number;
  creditsApplied?: number;
  showBreakdown?: boolean;
  loading?: boolean;
  onTotalChange?: (total: number) => void;
}

/**
 * Component for displaying cost calculation with detailed breakdown
 * Validates: Requirements 3.2, 13.4
 * Property 4: Cost Calculation Accuracy - Total should equal sum of components
 * Property 20: Service Variant Cost Update - Variant cost should update total
 * Property 21: Add-On Cost Accumulation - Add-ons should accumulate in total
 */
export const CostCalculator: React.FC<CostCalculatorProps> = ({
  subtotal,
  variantCost = 0,
  addOnsCost = 0,
  discount = 0,
  creditsApplied = 0,
  showBreakdown = true,
  onTotalChange,
}) => {
  const total = useMemo(() => {
    const calculated = Math.max(
      0,
      subtotal + variantCost + addOnsCost - discount - creditsApplied,
    );
    onTotalChange?.(calculated);
    return calculated;
  }, [
    subtotal,
    variantCost,
    addOnsCost,
    discount,
    creditsApplied,
    onTotalChange,
  ]);

  const hasBreakdown =
    variantCost > 0 || addOnsCost > 0 || discount > 0 || creditsApplied > 0;

  return (
    <Card className="p-4 space-y-4">
      <h3 className="flex items-center gap-2 text-lg font-semibold text-foreground">
        <DollarSignIcon size={20} />
        Cost Summary
      </h3>

      {/* Breakdown */}
      {showBreakdown && hasBreakdown && (
        <div className="space-y-2 border-b border-border pb-4 text-sm">
          <CostBreakdownItem label="Service" amount={subtotal} />

          {variantCost > 0 && (
            <CostBreakdownItem
              label="Variant"
              amount={variantCost}
              type="positive"
            />
          )}

          {addOnsCost > 0 && (
            <CostBreakdownItem
              label="Add-ons"
              amount={addOnsCost}
              type="positive"
            />
          )}

          {discount > 0 && (
            <CostBreakdownItem
              label="Discount"
              amount={discount}
              type="negative"
            />
          )}

          {creditsApplied > 0 && (
            <CostBreakdownItem
              label="Package Credits"
              amount={creditsApplied}
              type="negative"
            />
          )}
        </div>
      )}

      {/* Total */}
      <CostSummaryTotal subtotal={subtotal} total={total} />

      {/* Savings indicator */}
      <SavingsIndicator discount={discount} creditsApplied={creditsApplied} />
    </Card>
  );
};

export default CostCalculator;
