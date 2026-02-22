import { type PromoCode } from "@/lib/api/hooks/usePromoCodes";
import { TrendingUpIcon, BarChart3Icon } from "@/components/icons";

interface PromoCodeStatsProps {
  code: PromoCode;
}

export function PromoCodeStats({ code }: PromoCodeStatsProps) {
  // Calculate usage percentage
  const usagePercentage = code.max_uses
    ? Math.round(((code.current_uses || 0) / code.max_uses) * 100)
    : 0;

  // Calculate average discount per use
  const averageDiscountPerUse =
    code.current_uses && code.current_uses > 0
      ? (code.discount_value / code.current_uses).toFixed(2)
      : "0.00";

  // Estimate revenue impact (simplified calculation)
  // This would need actual transaction data from backend for accuracy
  const estimatedRevenueImpact =
    code.current_uses && code.current_uses > 0
      ? (parseFloat(averageDiscountPerUse) * code.current_uses).toFixed(2)
      : "0.00";

  return (
    <div className="space-y-3">
      {/* Total Usage Count */}
      <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
        <div className="flex items-center gap-2">
          <BarChart3Icon size={16} className="text-blue-500" />
          <span className="text-sm font-medium text-gray-700">Total Uses</span>
        </div>
        <span className="text-sm font-semibold text-gray-900">
          {code.current_uses || 0}
          {code.max_uses && ` / ${code.max_uses}`}
        </span>
      </div>

      {/* Usage Percentage */}
      {code.max_uses && (
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
          <div className="flex items-center gap-2">
            <TrendingUpIcon size={16} className="text-green-500" />
            <span className="text-sm font-medium text-gray-700">
              Usage Rate
            </span>
          </div>
          <span className="text-sm font-semibold text-gray-900">
            {usagePercentage}%
          </span>
        </div>
      )}

      {/* Average Discount Per Use */}
      <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
        <span className="text-sm font-medium text-gray-700">
          Avg Discount/Use
        </span>
        <span className="text-sm font-semibold text-gray-900">
          {code.discount_type === "percentage"
            ? `${averageDiscountPerUse}%`
            : `$${averageDiscountPerUse}`}
        </span>
      </div>

      {/* Revenue Impact */}
      <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
        <span className="text-sm font-medium text-gray-700">
          Revenue Impact
        </span>
        <span className="text-sm font-semibold text-gray-900">
          {code.discount_type === "percentage"
            ? `~${estimatedRevenueImpact}%`
            : `$${estimatedRevenueImpact}`}
        </span>
      </div>
    </div>
  );
}
