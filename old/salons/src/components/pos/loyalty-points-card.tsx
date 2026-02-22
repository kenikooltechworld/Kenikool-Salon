import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { StarIcon } from "@/components/icons";
import type { LoyaltyBalance } from "@/lib/api/hooks/useLoyalty";
import { formatCurrency } from "@/lib/utils/currency";

interface LoyaltyPointsCardProps {
  loyaltyBalance: LoyaltyBalance;
  pointsToRedeem: number;
  onPointsChange: (points: number) => void;
}

export function LoyaltyPointsCard({
  loyaltyBalance,
  pointsToRedeem,
  onPointsChange,
}: LoyaltyPointsCardProps) {
  const [showPanel, setShowPanel] = useState(false);

  return (
    <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-[var(--muted)] flex items-center justify-center">
              <StarIcon className="h-6 w-6 text-[var(--primary)]" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Loyalty Points</p>
              <p className="text-2xl font-bold text-[var(--foreground)]">
                {loyaltyBalance.points_balance.toLocaleString()}
              </p>
              <p className="text-xs text-[var(--muted-foreground)]">
                {loyaltyBalance.tier.toUpperCase()} Tier
              </p>
            </div>
          </div>
          <div className="text-right">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowPanel(!showPanel)}
              className="mb-2"
            >
              {showPanel ? "Hide" : "Redeem"} Points
            </Button>
            {loyaltyBalance.tier_progress.next_tier && (
              <p className="text-xs text-[var(--muted-foreground)]">
                {loyaltyBalance.tier_progress.points_to_next} pts to{" "}
                {loyaltyBalance.tier_progress.next_tier}
              </p>
            )}
          </div>
        </div>

        {showPanel && (
          <div className="mt-4 pt-4 border-t border-purple-200">
            <Label className="text-sm">Redeem Points for Discount</Label>
            <div className="flex gap-2 mt-2">
              <Input
                type="number"
                min="0"
                max={loyaltyBalance.points_balance}
                value={pointsToRedeem}
                onChange={(e) =>
                  onPointsChange(
                    Math.min(
                      parseInt(e.target.value) || 0,
                      loyaltyBalance.points_balance
                    )
                  )
                }
                placeholder="Points to redeem"
                className="flex-1"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPointsChange(loyaltyBalance.points_balance)}
              >
                Max
              </Button>
            </div>
            {pointsToRedeem > 0 && (
              <p className="text-sm text-[var(--muted-foreground)] mt-2">
                Discount: {formatCurrency(pointsToRedeem * 0.01)} (100 points =
                ₦1)
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
