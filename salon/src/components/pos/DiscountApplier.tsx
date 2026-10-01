import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { TagIcon, XIcon } from "@/components/icons";
import { useValidateDiscount } from "@/hooks/useDiscount";
import { formatCurrency } from "@/lib/utils/format";

interface DiscountApplierProps {
  onClose?: () => void;
  subtotal?: number;
  onDiscountApplied?: (discountAmount: number) => void;
}

export default function DiscountApplier({ onClose, subtotal = 0, onDiscountApplied }: DiscountApplierProps) {
  const [discountCode, setDiscountCode] = useState("");
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [appliedDiscount, setAppliedDiscount] = useState<{ code: string; amount: number } | null>(null);
  const validateDiscount = useValidateDiscount();

  const handleApplyDiscount = async () => {
    if (!discountCode.trim()) {
      setError("Please enter a discount code");
      return;
    }

    setError(undefined);
    setIsApplying(true);

    try {
      const result = await validateDiscount.mutateAsync({
        discountCode: discountCode.toUpperCase(),
        subtotal,
      });

      if (result.valid) {
        setSuccess(true);
        setAppliedDiscount({
          code: discountCode.toUpperCase(),
          amount: result.discountAmount,
        });
        onDiscountApplied?.(result.discountAmount);
        setTimeout(() => {
          setSuccess(false);
          onClose?.();
        }, 2000);
      } else {
        setError(result.message || "Invalid discount code");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to apply discount");
    } finally {
      setIsApplying(false);
    }
  };

  const handleRemoveDiscount = () => {
    setDiscountCode("");
    setSuccess(false);
    setError(undefined);
    setAppliedDiscount(null);
    onDiscountApplied?.(0);
  };

  return (
    <Card className="p-4 md:p-6 border-2 border-primary">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base md:text-lg font-semibold text-foreground flex items-center gap-2">
          <TagIcon size={20} />
          Apply Discount
        </h3>
        {onClose && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <XIcon size={16} />
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}
      {success && (
        <Alert variant="success" className="mb-4">
          Discount applied successfully!
        </Alert>
      )}

      {discountCode && appliedDiscount ? (
        <div className="space-y-4">
          <div className="bg-green-50 dark:bg-green-950 p-3 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-sm text-muted-foreground">Applied Discount</p>
            <p className="font-semibold text-foreground text-lg">
              {appliedDiscount.code}
            </p>
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              -{formatCurrency(appliedDiscount.amount, "NGN")} discount
            </p>
          </div>
          <Button
            variant="outline"
            onClick={handleRemoveDiscount}
            className="w-full text-destructive hover:text-destructive"
          >
            Remove Discount
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <Label htmlFor="discount-code" className="mb-2 block">
              Discount Code
            </Label>
            <Input
              id="discount-code"
              placeholder="Enter discount code"
              value={discountCode}
              onChange={(e) => setDiscountCode(e.target.value.toUpperCase())}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleApplyDiscount();
                }
              }}
              disabled={isApplying}
            />
          </div>
          <Button
            onClick={handleApplyDiscount}
            disabled={isApplying || !discountCode.trim()}
            className="w-full"
          >
            {isApplying ? (
              <>
                <Spinner className="w-4 h-4 mr-2" />
                Validating...
              </>
            ) : (
              "Apply Discount"
            )}
          </Button>
        </div>
      )}
    </Card>
  );
}
