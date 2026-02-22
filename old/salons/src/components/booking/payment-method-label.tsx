interface PaymentMethodLabelProps {
  method: string;
}

export function PaymentMethodLabel({ method }: PaymentMethodLabelProps) {
  const getLabel = () => {
    switch (method?.toLowerCase()) {
      case "credit_card":
        return "Credit Card";
      case "debit_card":
        return "Debit Card";
      case "bank_transfer":
        return "Bank Transfer";
      case "cash":
        return "Cash";
      case "mobile_money":
        return "Mobile Money";
      default:
        return method || "Unknown";
    }
  };

  return <span>{getLabel()}</span>;
}
