/**
 * PackageCreditRedemption Component
 * Allows redemption of package credits for bookings
 * Validates: Requirements 3.3, 5.2, 5.3
 * Property 5: Credit Redemption Round Trip
 */
import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { GiftIcon, CheckCircleIcon } from "@/components/icons";
import { CreditBalanceCard } from "./credit-balance-card";
import { CreditSlider } from "./credit-slider";
import { CreditSummary } from "./credit-summary";

interface PackageCreditRedemptionProps {
  availableCredits: number;
  bookingTotal: number;
  onCreditsApply: (amount: number) => void;
  loading?: boolean;
  maxRedeemable?: number;
  onCreditsChange?: (amount: number) => void;
}

/**
 * Component for redeeming package credits toward a booking
 * Validates: Requirements 3.3, 5.2, 5.3
 * Property 5: Credit Redemption Round Trip - Balance should decrease and total should decrease by same amount
 */
export const PackageCreditRedemption: React.FC<
  PackageCreditRedemptionProps
> = ({
  availableCredits,
  bookingTotal,
  onCreditsApply,
  loading = false,
  maxRedeemable,
  onCreditsChange,
}) => {
  const [creditsToApply, setCreditsToApply] = useState(0);
  const [useFullCredits, setUseFullCredits] = useState(false);

  const maxApplicable = Math.min(
    availableCredits,
    bookingTotal,
    maxRedeemable || availableCredits,
  );

  const remainingBalance = availableCredits - creditsToApply;

  useEffect(() => {
    if (useFullCredits) {
      setCreditsToApply(maxApplicable);
      onCreditsChange?.(maxApplicable);
    }
  }, [useFullCredits, maxApplicable, onCreditsChange]);

  const handleApply = () => {
    onCreditsApply(creditsToApply);
  };

  const handleSliderChange = (value: number) => {
    setCreditsToApply(value);
    setUseFullCredits(false);
    onCreditsChange?.(value);
  };

  const handleFullCredits = () => {
    setUseFullCredits(!useFullCredits);
  };

  if (availableCredits === 0) {
    return (
      <Card className="p-4 bg-muted border-border">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>No package credits available</span>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 space-y-4 border-primary/20 bg-primary/5">
      <div className="flex items-center gap-2">
        <GiftIcon size={20} className="text-primary" />
        <h3 className="font-semibold text-foreground">Package Credits</h3>
      </div>

      {/* Available Balance */}
      <CreditBalanceCard availableCredits={availableCredits} />

      {/* Credit Slider */}
      <CreditSlider
        creditsToApply={creditsToApply}
        maxApplicable={maxApplicable}
        onSliderChange={handleSliderChange}
        loading={loading}
      />

      {/* Use Full Credits Button */}
      <Button
        onClick={handleFullCredits}
        disabled={loading}
        variant="outline"
        className="w-full"
      >
        {useFullCredits ? "Clear" : "Use Full Credits"}
      </Button>

      {/* Summary */}
      <CreditSummary
        bookingTotal={bookingTotal}
        creditsApplied={creditsToApply}
        remainingBalance={remainingBalance}
      />

      {/* Apply Button */}
      <Button
        onClick={handleApply}
        disabled={loading || creditsToApply === 0}
        className="w-full"
      >
        {loading ? "Applying..." : "Apply Credits"}
      </Button>

      {/* Success Message */}
      {creditsToApply > 0 && (
        <div className="flex items-center gap-2 rounded p-2 bg-green-50 border border-green-200">
          <CheckCircleIcon size={16} className="text-green-600" />
          <span className="text-sm text-green-900">
            You'll save ${creditsToApply.toFixed(2)} with these credits
          </span>
        </div>
      )}
    </Card>
  );
};

export default PackageCreditRedemption;
