/**
 * PaymentMethodCard Component
 * Displays a single payment method option as a selectable card
 */
import React from "react";
import { Card } from "@/components/ui/card";
import {
  CreditCardIcon,
  WalletIcon,
  CheckCircleIcon,
} from "@/components/icons";

interface PaymentMethodCardProps {
  id: string;
  type: "credit_card" | "debit_card" | "digital_wallet" | "package_credits";
  name: string;
  isSelected: boolean;
  isDefault?: boolean;
  availableCredits?: number;
  disabled?: boolean;
  onSelect: (methodId: string) => void;
}

const getPaymentMethodIcon = (
  type: "credit_card" | "debit_card" | "digital_wallet" | "package_credits",
) => {
  switch (type) {
    case "credit_card":
    case "debit_card":
      return <CreditCardIcon size={20} />;
    case "digital_wallet":
      return <WalletIcon size={20} />;
    case "package_credits":
      return <CheckCircleIcon size={20} />;
    default:
      return null;
  }
};

const getPaymentMethodLabel = (
  type: "credit_card" | "debit_card" | "digital_wallet" | "package_credits",
) => {
  switch (type) {
    case "credit_card":
      return "Credit Card";
    case "debit_card":
      return "Debit Card";
    case "digital_wallet":
      return "Digital Wallet";
    case "package_credits":
      return "Package Credits";
    default:
      return "Payment Method";
  }
};

export const PaymentMethodCard: React.FC<PaymentMethodCardProps> = ({
  id,
  type,
  name,
  isSelected,
  isDefault,
  availableCredits,
  disabled = false,
  onSelect,
}) => {
  return (
    <Card
      onClick={() => !disabled && onSelect(id)}
      className={`p-4 cursor-pointer transition-all ${
        isSelected
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50"
      } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="text-primary">{getPaymentMethodIcon(type)}</div>
          <div>
            <div className="font-semibold text-foreground">
              {getPaymentMethodLabel(type)}
            </div>
            <div className="text-sm text-muted-foreground">{name}</div>
          </div>
        </div>
        {isDefault && (
          <span className="rounded bg-primary/10 px-2 py-1 text-xs font-semibold text-primary">
            Default
          </span>
        )}
      </div>

      {/* Package Credits Balance */}
      {type === "package_credits" && availableCredits !== undefined && (
        <div className="mt-2 text-sm text-muted-foreground">
          Available: ${availableCredits.toFixed(2)}
        </div>
      )}
    </Card>
  );
};

export default PaymentMethodCard;
