import { useState } from "react";
// TODO: These hooks need to be implemented in useGiftCards
// import {
//   useValidateGiftCard,
//   useRedeemGiftCard,
// } from "@/lib/api/hooks/useGiftCards";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckCircleIcon,
  XCircleIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { AxiosError } from "axios";
import { ErrorResponse } from "@/lib/api/types";

interface GiftCardRedeemModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRedeemed?: (code: string, amount: number) => void;
}

export function GiftCardRedeemModal({
  isOpen,
  onClose,
  onRedeemed,
}: GiftCardRedeemModalProps) {
  const [code, setCode] = useState("");
  const [amount, setAmount] = useState("");
  const [validationResult, setValidationResult] = useState<any>(null);
  const [validatedCode, setValidatedCode] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateGiftCard = useValidateGiftCard({
    onSuccess: (data) => {
      setValidationResult(data);
      setValidatedCode(code);
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      setErrors({ validate: error.message });
    },
  });

  const redeemGiftCard = useRedeemGiftCard({
    onSuccess: (data) => {
      if (onRedeemed) {
        onRedeemed(validatedCode, parseFloat(amount));
      }
      handleReset();
      onClose();
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      setErrors({ redeem: error.message });
    },
  });

  const handleValidate = (e: React.FormEvent) => {
    e.preventDefault();

    if (!code.trim()) {
      setErrors({ code: "Gift card code is required" });
      return;
    }

    setErrors({});
    validateGiftCard.mutate(code.toUpperCase());
  };

  const handleRedeem = (e: React.FormEvent) => {
    e.preventDefault();

    const amountNum = parseFloat(amount);
    if (!amount || isNaN(amountNum) || amountNum <= 0) {
      setErrors({ amount: "Amount must be greater than 0" });
      return;
    }

    if (validationResult?.balance && amountNum > validationResult.balance) {
      setErrors({ amount: "Amount exceeds gift card balance" });
      return;
    }

    setErrors({});
    redeemGiftCard.mutate({ code: validatedCode, amount: amountNum });
  };

  const handleReset = () => {
    setCode("");
    setAmount("");
    setValidationResult(null);
    setValidatedCode("");
    setErrors({});
  };

  const handleClose = () => {
    handleReset();
    onClose();
  };

  return (
    <Modal open={isOpen} onClose={handleClose} size="lg">
      <div className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          Redeem Gift Card
        </h2>

        <div className="space-y-6">
          {/* Validation Step */}
          {!validationResult?.valid && (
            <form onSubmit={handleValidate} className="space-y-4">
              {errors.validate && (
                <Alert variant="error">
                  <AlertTriangleIcon size={20} />
                  <div>
                    <p className="text-sm">{errors.validate}</p>
                  </div>
                </Alert>
              )}

              <div>
                <Label htmlFor="code">Gift Card Code *</Label>
                <Input
                  id="code"
                  value={code}
                  onChange={(e) => {
                    setCode(e.target.value.toUpperCase());
                    if (errors.code) {
                      setErrors((prev) => {
                        const newErrors = { ...prev };
                        delete newErrors.code;
                        return newErrors;
                      });
                    }
                  }}
                  placeholder="Enter gift card code"
                  className="uppercase"
                  error={!!errors.code}
                />
                {errors.code && (
                  <p className="text-sm text-error mt-1">{errors.code}</p>
                )}
              </div>

              <Button
                type="submit"
                disabled={validateGiftCard.isPending}
                fullWidth
              >
                {validateGiftCard.isPending ? (
                  <>
                    <Spinner size="sm" />
                    Validating...
                  </>
                ) : (
                  "Validate Gift Card"
                )}
              </Button>
            </form>
          )}

          {/* Validation Result */}
          {validationResult && (
            <div className="space-y-4">
              {validationResult.valid ? (
                <>
                  <div className="bg-[var(--success)]/10 border-2 border-[var(--success)] rounded-[var(--radius-lg)] p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircleIcon className="w-5 h-5 text-[var(--success)]" />
                      <span className="font-semibold text-[var(--foreground)]">
                        Valid Gift Card
                      </span>
                    </div>
                    <div className="text-sm text-[var(--foreground)]">
                      <p>Code: {validatedCode}</p>
                      <p className="text-lg font-bold mt-2">
                        Balance: ₦{validationResult.balance?.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Redemption Form */}
                  <form onSubmit={handleRedeem} className="space-y-4">
                    {errors.redeem && (
                      <Alert variant="error">
                        <AlertTriangleIcon size={20} />
                        <div>
                          <p className="text-sm">{errors.redeem}</p>
                        </div>
                      </Alert>
                    )}

                    <div>
                      <Label htmlFor="amount">Amount to Redeem *</Label>
                      <Input
                        id="amount"
                        value={amount}
                        onChange={(e) => {
                          setAmount(e.target.value);
                          if (errors.amount) {
                            setErrors((prev) => {
                              const newErrors = { ...prev };
                              delete newErrors.amount;
                              return newErrors;
                            });
                          }
                        }}
                        type="number"
                        placeholder="Enter amount to redeem"
                        min="1"
                        max={validationResult.balance}
                        step="0.01"
                        error={!!errors.amount}
                      />
                      {errors.amount && (
                        <p className="text-sm text-error mt-1">
                          {errors.amount}
                        </p>
                      )}
                    </div>

                    <div className="flex gap-3">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleClose}
                        disabled={redeemGiftCard.isPending}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        disabled={redeemGiftCard.isPending}
                        className="flex-1"
                      >
                        {redeemGiftCard.isPending ? (
                          <>
                            <Spinner size="sm" />
                            Redeeming...
                          </>
                        ) : (
                          "Redeem"
                        )}
                      </Button>
                    </div>
                  </form>
                </>
              ) : (
                <div className="bg-[var(--error)]/10 border-2 border-[var(--error)] rounded-[var(--radius-lg)] p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <XCircleIcon className="w-5 h-5 text-[var(--error)]" />
                    <span className="font-semibold text-[var(--foreground)]">
                      Invalid Gift Card
                    </span>
                  </div>
                  <p className="text-sm text-[var(--foreground)]">
                    {validationResult.error}
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setValidationResult(null);
                      setCode("");
                    }}
                    className="mt-3"
                  >
                    Try Another Code
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
