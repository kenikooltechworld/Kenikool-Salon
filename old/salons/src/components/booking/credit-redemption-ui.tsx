/**
 * CreditRedemptionUI Component
 * Shows available credits during payment and allows partial/full redemption
 * Validates: Requirements 5.2, 5.3, 5.4
 */
import React, { useState } from "react";
import { Gift, ChevronDown, ChevronUp } from "lucide-react";

interface CreditRedemptionUIProps {
  availableCredits: number;
  bookingTotal: number;
  onRedemptionChange: (amount: number) => void;
  loading?: boolean;
  disabled?: boolean;
}

/**
 * Component for redeeming package credits during payment
 */
export const CreditRedemptionUI: React.FC<CreditRedemptionUIProps> = ({
  availableCredits,
  bookingTotal,
  onRedemptionChange,
  loading = false,
  disabled = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [redemptionAmount, setRedemptionAmount] = useState(0);
  const [redemptionMode, setRedemptionMode] = useState<
    "none" | "partial" | "full"
  >("none");

  // Calculate max redeemable amount
  const maxRedeemable = Math.min(availableCredits, bookingTotal);
  const remainingBalance = availableCredits - redemptionAmount;
  const finalTotal = bookingTotal - redemptionAmount;

  // Handle full redemption
  const handleFullRedemption = () => {
    const amount = maxRedeemable;
    setRedemptionAmount(amount);
    setRedemptionMode("full");
    onRedemptionChange(amount);
  };

  // Handle no redemption
  const handleNoRedemption = () => {
    setRedemptionAmount(0);
    setRedemptionMode("none");
    onRedemptionChange(0);
  };

  // Handle partial redemption slider change
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const amount = parseFloat(e.target.value);
    setRedemptionAmount(amount);
    setRedemptionMode(amount > 0 ? "partial" : "none");
    onRedemptionChange(amount);
  };

  // Handle manual input
  const handleManualInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    let amount = parseFloat(e.target.value) || 0;
    amount = Math.max(0, Math.min(amount, maxRedeemable));
    setRedemptionAmount(amount);
    setRedemptionMode(amount > 0 ? "partial" : "none");
    onRedemptionChange(amount);
  };

  if (availableCredits <= 0) {
    return null;
  }

  return (
    <div className="space-y-3 rounded-lg border border-blue-200 bg-blue-50 p-4">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        disabled={disabled || loading}
        className="flex w-full items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <Gift className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-blue-900">
            Use Package Credits
          </span>
          <span className="text-sm text-blue-700">
            (${availableCredits.toFixed(2)} available)
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-blue-600" />
        ) : (
          <ChevronDown className="h-5 w-5 text-blue-600" />
        )}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="space-y-4 border-t border-blue-200 pt-4">
          {/* Quick Actions */}
          <div className="flex gap-2">
            <button
              onClick={handleNoRedemption}
              disabled={disabled || loading}
              className={`flex-1 rounded px-3 py-2 text-sm font-medium transition-colors ${
                redemptionMode === "none"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-blue-600 hover:bg-blue-100"
              }`}
            >
              Don't Use
            </button>
            <button
              onClick={handleFullRedemption}
              disabled={disabled || loading || maxRedeemable === 0}
              className={`flex-1 rounded px-3 py-2 text-sm font-medium transition-colors ${
                redemptionMode === "full"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-blue-600 hover:bg-blue-100 disabled:opacity-50"
              }`}
            >
              Use All
            </button>
          </div>

          {/* Slider for Partial Redemption */}
          {maxRedeemable > 0 && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Custom Amount
              </label>
              <input
                type="range"
                min="0"
                max={maxRedeemable}
                step="0.01"
                value={redemptionAmount}
                onChange={handleSliderChange}
                disabled={disabled || loading}
                className="w-full"
              />
              <div className="flex gap-2">
                <div className="flex-1">
                  <label className="text-xs text-gray-600">Amount</label>
                  <input
                    type="number"
                    min="0"
                    max={maxRedeemable}
                    step="0.01"
                    value={redemptionAmount.toFixed(2)}
                    onChange={handleManualInput}
                    disabled={disabled || loading}
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-xs text-gray-600">Remaining</label>
                  <div className="rounded border border-gray-300 bg-gray-50 px-2 py-1 text-sm font-medium">
                    ${remainingBalance.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="space-y-2 rounded bg-white p-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Booking Total</span>
              <span className="font-medium">${bookingTotal.toFixed(2)}</span>
            </div>
            {redemptionAmount > 0 && (
              <div className="flex justify-between text-sm text-blue-600">
                <span>Credits Applied</span>
                <span className="font-medium">
                  -${redemptionAmount.toFixed(2)}
                </span>
              </div>
            )}
            <div className="border-t border-gray-200 pt-2">
              <div className="flex justify-between text-sm font-semibold">
                <span>Amount Due</span>
                <span className="text-lg text-blue-600">
                  ${finalTotal.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Info */}
          {redemptionAmount > 0 && (
            <div className="text-xs text-blue-700">
              ✓ {redemptionAmount === maxRedeemable ? "Full" : "Partial"} credit
              redemption applied
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CreditRedemptionUI;
