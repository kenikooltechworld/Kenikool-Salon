import { useState } from "react";
import { Card } from "@/components/ui/card";
import { PaystackPayment } from "./paystack-payment";
import { FlutterwavePayment } from "./flutterwave-payment";
import { CheckCircleIcon } from "@/components/icons";

interface PaymentGatewaySelectorProps {
  bookingId: string;
  amount: number;
  email: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

type Gateway = "paystack" | "flutterwave";

export function PaymentGatewaySelector({
  bookingId,
  amount,
  email,
  onSuccess,
  onError,
}: PaymentGatewaySelectorProps) {
  const [selectedGateway, setSelectedGateway] = useState<Gateway>("paystack");

  const gateways = [
    {
      id: "paystack" as Gateway,
      name: "Paystack",
      description: "Pay with card via Paystack",
      logo: "💳",
    },
    {
      id: "flutterwave" as Gateway,
      name: "Flutterwave",
      description: "Pay with card via Flutterwave",
      logo: "💰",
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-foreground mb-2">
          Select Payment Gateway
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {gateways.map((gateway) => (
            <button
              key={gateway.id}
              onClick={() => setSelectedGateway(gateway.id)}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                selectedGateway === gateway.id
                  ? "border-[var(--primary)] bg-[var(--primary)]/5"
                  : "border-[var(--border)] hover:border-[var(--primary)]/50"
              }`}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl">{gateway.logo}</span>
                <div className="flex-1">
                  <h3 className="font-medium text-foreground">
                    {gateway.name}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {gateway.description}
                  </p>
                </div>
                {selectedGateway === gateway.id && (
                  <CheckCircleIcon
                    size={20}
                    className="text-[var(--primary)]"
                  />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      <Card className="p-4">
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Amount to Pay</span>
            <span className="font-bold text-foreground text-lg">
              ₦{amount.toLocaleString()}
            </span>
          </div>

          {selectedGateway === "paystack" && (
            <PaystackPayment
              bookingId={bookingId}
              amount={amount}
              email={email}
              onSuccess={onSuccess}
              onError={onError}
            />
          )}

          {selectedGateway === "flutterwave" && (
            <FlutterwavePayment
              bookingId={bookingId}
              amount={amount}
              email={email}
              onSuccess={onSuccess}
              onError={onError}
            />
          )}
        </div>
      </Card>
    </div>
  );
}
