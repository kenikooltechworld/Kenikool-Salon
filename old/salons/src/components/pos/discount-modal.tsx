import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { useValidateDiscount } from "@/lib/api/hooks/usePOS";
import { formatCurrency } from "@/lib/utils/currency";

interface DiscountModalProps {
  open: boolean;
  onClose: () => void;
  cartSubtotal: number;
  clientId?: string;
  serviceIds: string[];
  onApplyDiscount: (discount: {
    amount: number;
    type: string;
    reason: string;
  }) => void;
}

export function DiscountModal({
  open,
  onClose,
  cartSubtotal,
  clientId,
  serviceIds,
  onApplyDiscount,
}: DiscountModalProps) {
  const [discountType, setDiscountType] = useState<
    "promo_code" | "manual" | "member"
  >("manual");
  const [promoCode, setPromoCode] = useState("");
  const [manualType, setManualType] = useState<"amount" | "percentage">(
    "amount"
  );
  const [discountAmount, setDiscountAmount] = useState("");
  const [discountPercentage, setDiscountPercentage] = useState("");
  const [reason, setReason] = useState("");

  const validateDiscount = useValidateDiscount();

  const handleApply = async () => {
    if (discountType === "promo_code") {
      if (!promoCode.trim()) {
        toast.error("Please enter a promo code");
        return;
      }

      if (!clientId) {
        toast.error("Please select a client to apply promo code");
        return;
      }

      try {
        const result = await validateDiscount.mutateAsync({
          discount_type: "promo_code",
          promo_code: promoCode.toUpperCase(),
          cart_total: cartSubtotal,
          client_id: clientId,
          service_ids: serviceIds.join(","),
        });

        if (result.valid) {
          onApplyDiscount({
            amount: result.discount_amount,
            type: "promo_code",
            reason: result.reason || `Promo: ${promoCode}`,
          });
          toast.success(
            `Promo code applied! Discount: ${formatCurrency(
              result.discount_amount
            )}`
          );
          handleClose();
        } else {
          toast.error(result.error || "Invalid promo code");
        }
      } catch (error) {
        toast.error("Failed to validate promo code");
      }
    } else if (discountType === "manual") {
      if (manualType === "amount") {
        const amount = parseFloat(discountAmount);
        if (isNaN(amount) || amount <= 0) {
          toast.error("Please enter a valid discount amount");
          return;
        }
        if (amount > cartSubtotal) {
          toast.error("Discount cannot exceed cart total");
          return;
        }

        try {
          const result = await validateDiscount.mutateAsync({
            discount_type: "manual",
            discount_amount: amount,
            reason: reason || "Manual discount",
            cart_total: cartSubtotal,
          });

          if (result.valid) {
            onApplyDiscount({
              amount: result.discount_amount,
              type: "manual",
              reason: result.reason || "Manual discount",
            });
            toast.success(`Discount applied: ${formatCurrency(amount)}`);
            handleClose();
          } else {
            toast.error(result.error || "Invalid discount");
          }
        } catch (error) {
          toast.error("Failed to apply discount");
        }
      } else {
        const percentage = parseFloat(discountPercentage);
        if (isNaN(percentage) || percentage <= 0 || percentage > 100) {
          toast.error("Please enter a valid percentage (1-100)");
          return;
        }

        try {
          const result = await validateDiscount.mutateAsync({
            discount_type: "manual",
            discount_percentage: percentage,
            reason: reason || `${percentage}% discount`,
            cart_total: cartSubtotal,
          });

          if (result.valid) {
            onApplyDiscount({
              amount: result.discount_amount,
              type: "manual",
              reason: result.reason || `${percentage}% discount`,
            });
            toast.success(
              `Discount applied: ${percentage}% (${formatCurrency(
                result.discount_amount
              )})`
            );
            handleClose();
          } else {
            toast.error(result.error || "Invalid discount");
          }
        } catch (error) {
          toast.error("Failed to apply discount");
        }
      }
    } else {
      toast.error("Member discounts not yet implemented");
    }
  };

  const handleClose = () => {
    setPromoCode("");
    setDiscountAmount("");
    setDiscountPercentage("");
    setReason("");
    setManualType("amount");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Apply Discount</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Discount Type Selection */}
          <div className="space-y-2">
            <Label>Discount Type</Label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant={discountType === "promo_code" ? "default" : "outline"}
                size="sm"
                onClick={() => setDiscountType("promo_code")}
                className="flex-1"
              >
                Promo Code
              </Button>
              <Button
                type="button"
                variant={discountType === "manual" ? "default" : "outline"}
                size="sm"
                onClick={() => setDiscountType("manual")}
                className="flex-1"
              >
                Manual
              </Button>
            </div>
          </div>

          {/* Promo Code Input */}
          {discountType === "promo_code" && (
            <div className="space-y-2">
              <Label htmlFor="promo-code">Promo Code</Label>
              <Input
                id="promo-code"
                placeholder="Enter promo code"
                value={promoCode}
                onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                className="uppercase"
              />
              {!clientId && (
                <p className="text-xs text-[var(--accent)]">
                  ⚠️ Please select a client to apply promo code
                </p>
              )}
            </div>
          )}

          {/* Manual Discount */}
          {discountType === "manual" && (
            <>
              <div className="space-y-2">
                <Label>Manual Discount Type</Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={manualType === "amount" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setManualType("amount")}
                    className="flex-1"
                  >
                    Fixed Amount
                  </Button>
                  <Button
                    type="button"
                    variant={
                      manualType === "percentage" ? "default" : "outline"
                    }
                    size="sm"
                    onClick={() => setManualType("percentage")}
                    className="flex-1"
                  >
                    Percentage
                  </Button>
                </div>
              </div>

              {manualType === "amount" && (
                <div className="space-y-2">
                  <Label htmlFor="discount-amount">Discount Amount</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="discount-amount"
                      type="number"
                      min="0"
                      max={cartSubtotal}
                      step="0.01"
                      placeholder="0.00"
                      value={discountAmount}
                      onChange={(e) => setDiscountAmount(e.target.value)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Max: {formatCurrency(cartSubtotal)}
                  </p>
                </div>
              )}

              {manualType === "percentage" && (
                <div className="space-y-2">
                  <Label htmlFor="discount-percentage">
                    Discount Percentage
                  </Label>
                  <div className="flex items-center gap-2">
                    <Input
                      id="discount-percentage"
                      type="number"
                      min="0"
                      max="100"
                      step="1"
                      placeholder="0"
                      value={discountPercentage}
                      onChange={(e) => setDiscountPercentage(e.target.value)}
                    />
                    <span className="text-muted-foreground">%</span>
                  </div>
                  {discountPercentage && (
                    <p className="text-xs text-muted-foreground">
                      Discount:{" "}
                      {formatCurrency(
                        cartSubtotal * (parseFloat(discountPercentage) / 100)
                      )}
                    </p>
                  )}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="reason">Reason (Optional)</Label>
                <Textarea
                  id="reason"
                  placeholder="e.g., Customer loyalty, Price match, etc."
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  maxLength={200}
                  className="min-h-[60px] resize-none"
                />
                <p className="text-xs text-muted-foreground text-right">
                  {reason.length}/200
                </p>
              </div>
            </>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={validateDiscount.isPending}>
            {validateDiscount.isPending ? "Validating..." : "Apply Discount"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
