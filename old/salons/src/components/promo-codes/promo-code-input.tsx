import { useState } from "react";
import { useValidatePromoCode, type PromoCodeValidation } from "@/lib/api/hooks/usePromoCodes";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CheckIcon, XIcon, Loader2Icon, TrashIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface PromoCodeInputProps {
  clientId: string;
  serviceIds: string[];
  totalAmount: number;
  onApply?: (validation: PromoCodeValidation) => void;
  onClear?: () => void;
  appliedCode?: PromoCodeValidation | null;
}

export function PromoCodeInput({
  clientId,
  serviceIds,
  totalAmount,
  onApply,
  onClear,
  appliedCode,
}: PromoCodeInputProps) {
  const [code, setCode] = useState("");
  const [validation, setValidation] = useState<PromoCodeValidation | null>(
    appliedCode || null
  );
  const [error, setError] = useState<string | null>(null);
  const validateMutation = useValidatePromoCode();

  const handleValidate = async () => {
    if (!code.trim()) {
      setError("Please enter a promo code");
      return;
    }

    setError(null);

    try {
      const result = await validateMutation.mutateAsync({
        code: code.trim().toUpperCase(),
        client_id: clientId,
        service_ids: serviceIds,
        total_amount: totalAmount,
      });

      if (result.valid) {
        setValidation(result);
        onApply?.(result);
        showToast("Promo code applied successfully", "success");
      } else {
        setError(result.error || "Invalid promo code");
        setValidation(null);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || "Failed to validate promo code";
      setError(errorMessage);
      setValidation(null);
    }
  };

  const handleClear = () => {
    setCode("");
    setValidation(null);
    setError(null);
    onClear?.();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleValidate();
    }
  };

  // If a code is already applied, show success state
  if (validation?.valid) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-md">
          <CheckIcon size={20} className="text-green-600" />
          <div className="flex-1">
            <p className="text-sm font-medium text-green-900">
              {validation.code || "Promo code"} applied
            </p>
            {validation.discount_amount && (
              <p className="text-xs text-green-700">
                Discount: ${validation.discount_amount.toFixed(2)}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="text-green-600 hover:text-green-700"
          >
            <TrashIcon size={16} />
          </Button>
        </div>
        {validation.final_amount && (
          <div className="text-sm font-medium text-right">
            Final Amount: ${validation.final_amount.toFixed(2)}
          </div>
        )}
      </div>
    );
  }

  // Show input state
  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <Input
          type="text"
          placeholder="Enter promo code"
          value={code}
          onChange={(e) => {
            setCode(e.target.value);
            setError(null);
          }}
          onKeyDown={handleKeyPress}
          disabled={validateMutation.isPending}
          className={error ? "border-red-500" : ""}
        />
        <Button
          onClick={handleValidate}
          disabled={validateMutation.isPending || !code.trim()}
          className="whitespace-nowrap"
        >
          {validateMutation.isPending ? (
            <>
              <Loader2Icon size={16} className="mr-2 animate-spin" />
              Validating...
            </>
          ) : (
            "Apply"
          )}
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-2 bg-red-50 border border-red-200 rounded-md">
          <XIcon size={16} className="text-red-600" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  );
}
