import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Alert } from "@/components/ui/alert";
import { PlusIcon, XIcon } from "@/components/icons";

interface PaymentPart {
  id: string;
  method: string;
  amount: number;
}

interface SplitPaymentProps {
  totalAmount: number;
  onApply: (payments: PaymentPart[]) => void;
  onCancel: () => void;
}

export default function SplitPayment({
  totalAmount,
  onApply,
  onCancel,
}: SplitPaymentProps) {
  const [payments, setPayments] = useState<PaymentPart[]>([
    { id: "1", method: "cash", amount: totalAmount },
  ]);
  const [error, setError] = useState<string>();

  const paymentMethods = [
    { value: "cash", label: "Cash" },
    { value: "card", label: "Card (Paystack)" },
    { value: "mobile_money", label: "Mobile Money" },
    { value: "bank_transfer", label: "Bank Transfer" },
  ];

  const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0);
  const remaining = totalAmount - totalPaid;
  const isValid = Math.abs(remaining) < 0.01 && payments.length > 0;

  const handleAddPayment = () => {
    if (remaining <= 0) {
      setError("Total amount already covered");
      return;
    }
    setError(undefined);
    const newId = Math.max(...payments.map((p) => parseInt(p.id)), 0) + 1;
    setPayments([
      ...payments,
      { id: newId.toString(), method: "cash", amount: 0 },
    ]);
  };

  const handleRemovePayment = (id: string) => {
    if (payments.length === 1) {
      setError("At least one payment method is required");
      return;
    }
    setError(undefined);
    setPayments(payments.filter((p) => p.id !== id));
  };

  const handleUpdatePayment = (
    id: string,
    field: "method" | "amount",
    value: any,
  ) => {
    setError(undefined);
    setPayments(
      payments.map((p) =>
        p.id === id
          ? {
              ...p,
              [field]: field === "amount" ? parseFloat(value) || 0 : value,
            }
          : p,
      ),
    );
  };

  const handleApply = () => {
    if (!isValid) {
      setError(
        `Total must equal ₦${totalAmount.toLocaleString("en-NG", { maximumFractionDigits: 2 })}`,
      );
      return;
    }
    onApply(payments);
  };

  return (
    <Card className="p-4 md:p-6 border-2 border-primary">
      <h3 className="text-base md:text-lg font-semibold mb-4 text-foreground">
        Split Payment
      </h3>

      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}

      <div className="space-y-4">
        {payments.map((payment, idx) => (
          <div key={payment.id} className="p-3 border border-border rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <Label className="text-sm font-medium">Payment {idx + 1}</Label>
              {payments.length > 1 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemovePayment(payment.id)}
                  className="text-destructive hover:text-destructive"
                >
                  <XIcon size={16} />
                </Button>
              )}
            </div>

            <div className="space-y-3">
              <div>
                <Label className="text-xs text-muted-foreground mb-2 block">
                  Payment Method
                </Label>
                <RadioGroup
                  value={payment.method}
                  onValueChange={(value) =>
                    handleUpdatePayment(payment.id, "method", value)
                  }
                >
                  <div className="grid grid-cols-2 gap-2">
                    {paymentMethods.map((method) => (
                      <div
                        key={method.value}
                        className="flex items-center space-x-2"
                      >
                        <RadioGroupItem
                          value={method.value}
                          id={`method-${payment.id}-${method.value}`}
                        />
                        <Label
                          htmlFor={`method-${payment.id}-${method.value}`}
                          className="text-xs cursor-pointer"
                        >
                          {method.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </RadioGroup>
              </div>

              <div>
                <Label htmlFor={`amount-${payment.id}`} className="text-xs">
                  Amount
                </Label>
                <Input
                  id={`amount-${payment.id}`}
                  type="number"
                  placeholder="0.00"
                  value={payment.amount || ""}
                  onChange={(e) =>
                    handleUpdatePayment(payment.id, "amount", e.target.value)
                  }
                  step="0.01"
                  min="0"
                  className="text-sm"
                />
              </div>
            </div>
          </div>
        ))}

        <Button
          variant="outline"
          onClick={handleAddPayment}
          disabled={remaining <= 0}
          className="w-full"
        >
          <PlusIcon size={16} className="mr-2" />
          Add Payment Method
        </Button>

        <div className="bg-muted p-3 rounded-lg space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Total Amount</span>
            <span className="font-medium">
              ₦
              {totalAmount.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Total Paid</span>
            <span
              className={`font-medium ${remaining > 0 ? "text-destructive" : "text-green-600"}`}
            >
              ₦
              {totalPaid.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
          {remaining !== 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">
                {remaining > 0 ? "Remaining" : "Overpaid"}
              </span>
              <span
                className={`font-semibold ${remaining > 0 ? "text-destructive" : "text-green-600"}`}
              >
                ₦
                {Math.abs(remaining).toLocaleString("en-NG", {
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel} className="flex-1">
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={!isValid} className="flex-1">
            Apply Split Payment
          </Button>
        </div>
      </div>
    </Card>
  );
}
