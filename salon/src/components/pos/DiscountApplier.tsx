import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { TagIcon, XIcon } from "@/components/icons";

interface DiscountApplierProps {
  onClose?: () => void;
}

export default function DiscountApplier({ onClose }: DiscountApplierProps) {
  const [discountCode, setDiscountCode] = useState("");
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState(false);
  const [isApplying, setIsApplying] = useState(false);

  const handleApplyDiscount = async () => {
    if (!discountCode.trim()) {
      setError("Please enter a discount code");
      return;
    }

    setError(undefined);
    setIsApplying(true);

    try {
      // Simulate discount validation
      await new Promise((resolve) => setTimeout(resolve, 500));

      // In a real app, this would call an API to validate the discount
      if (discountCode.toUpperCase() === "WELCOME10") {
        setSuccess(true);
        setDiscountCode("");
        setTimeout(() => {
          setSuccess(false);
          onClose?.();
        }, 2000);
      } else {
        setError("Invalid discount code");
      }
    } catch (err) {
      setError("Failed to apply discount");
    } finally {
      setIsApplying(false);
    }
  };

  const handleRemoveDiscount = () => {
    setDiscountCode("");
    setSuccess(false);
    setError(undefined);
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

      {discountCode ? (
        <div className="space-y-4">
          <div className="bg-green-50 dark:bg-green-950 p-3 rounded-lg border border-green-200 dark:border-green-800">
            <p className="text-sm text-muted-foreground">Applied Discount</p>
            <p className="font-semibold text-foreground text-lg">
              {discountCode}
            </p>
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              Discount applied
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
