import { CreditCardIcon } from "@/components/icons";

interface PaymentMethodIconProps {
  method: string;
  size?: number;
}

export function PaymentMethodIcon({
  method,
  size = 24,
}: PaymentMethodIconProps) {
  const getIcon = () => {
    switch (method?.toLowerCase()) {
      case "credit_card":
      case "debit_card":
        return <CreditCardIcon size={size} />;
      case "bank_transfer":
        return <CreditCardIcon size={size} />;
      case "cash":
        return <CreditCardIcon size={size} />;
      case "mobile_money":
        return <CreditCardIcon size={size} />;
      default:
        return <CreditCardIcon size={size} />;
    }
  };

  return (
    <div className="inline-flex items-center justify-center">{getIcon()}</div>
  );
}
