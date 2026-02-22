/**
 * PaymentMethodSelector Component
 * Displays available payment methods for selection
 * Validates: Requirements 3.1
 * Property 3: Payment Method Display
 */
import React, { useEffect } from "react";
import { PaymentMethodCard } from "./payment-method-card";
import { Card } from "@/components/ui/card";

interface PaymentMethodOption {
  id: string;
  type: "credit_card" | "debit_card" | "digital_wallet" | "package_credits";
  name: string;
  is_default?: boolean;
}

interface PaymentMethodSelectorProps {
  methods: PaymentMethodOption[];
  selectedMethod?: string;
  onMethodSelect: (methodId: string) => void;
  loading?: boolean;
  availableCredits?: number;
  onMethodsLoaded?: (methods: PaymentMethodOption[]) => void;
}

/**
 * Component for selecting a payment method
 * Displays all available payment options including package credits
 * Validates: Requirements 3.1
 * Property 3: Payment Method Display - All payment methods should be displayed
 */
export const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  methods,
  selectedMethod,
  onMethodSelect,
  loading = false,
  availableCredits,
  onMethodsLoaded,
}) => {
  // Auto-select first method if none selected
  useEffect(() => {
    if (methods.length > 0 && !selectedMethod) {
      const defaultMethod = methods.find((m) => m.is_default) || methods[0];
      onMethodSelect(defaultMethod.id);
    }
    onMethodsLoaded?.(methods);
  }, [methods, selectedMethod, onMethodSelect, onMethodsLoaded]);

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-foreground">Payment Method</h3>

      <div className="grid gap-3 sm:grid-cols-2">
        {methods.map((method) => (
          <PaymentMethodCard
            key={method.id}
            id={method.id}
            type={method.type}
            name={method.name}
            isSelected={selectedMethod === method.id}
            isDefault={method.is_default}
            availableCredits={
              method.type === "package_credits" ? availableCredits : undefined
            }
            disabled={loading}
            onSelect={onMethodSelect}
          />
        ))}
      </div>

      {methods.length === 0 && (
        <Card className="p-4 bg-accent/10 border-accent">
          <div className="text-sm text-accent-foreground">
            No payment methods available. Please add a payment method to
            continue.
          </div>
        </Card>
      )}
    </div>
  );
};

export default PaymentMethodSelector;
