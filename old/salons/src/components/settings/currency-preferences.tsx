import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, AlertTriangleIcon } from "@/components/icons";
import {
  useUserPreferences,
  useUpdateUserPreferences,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

const CURRENCIES = [
  { code: "NGN", name: "Nigerian Naira (₦)", symbol: "₦" },
  { code: "USD", name: "US Dollar ($)", symbol: "$" },
  { code: "EUR", name: "Euro (€)", symbol: "€" },
  { code: "GBP", name: "British Pound (£)", symbol: "£" },
  { code: "ZAR", name: "South African Rand (R)", symbol: "R" },
  { code: "KES", name: "Kenyan Shilling (KSh)", symbol: "KSh" },
  { code: "GHS", name: "Ghanaian Cedi (₵)", symbol: "₵" },
];

export function CurrencyPreferences() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const queryClient = useQueryClient();

  const { data: preferences, isLoading } = useUserPreferences();

  const updatePreferencesMutation = useUpdateUserPreferences({
    onSuccess: () => {
      setSuccessMessage("Currency preference updated successfully");
      queryClient.invalidateQueries({ queryKey: ["user-preferences"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to update currency preference"
      );
    },
  });

  const handleCurrencyChange = (currencyCode: string) => {
    updatePreferencesMutation.mutate({
      currency: currencyCode,
    });
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  const currentCurrency = preferences?.currency || "NGN";
  const selectedCurrencyData = CURRENCIES.find(
    (c) => c.code === currentCurrency
  );

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Currency Preferences
      </h2>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {errorMessage && (
        <Alert variant="error" className="mb-4">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      <div className="space-y-4">
        {/* Current Selection */}
        <div className="bg-muted p-4 rounded-lg">
          <p className="text-sm font-medium text-foreground mb-1">
            Current Currency
          </p>
          <p className="text-lg font-semibold text-foreground">
            {selectedCurrencyData?.name}
          </p>
        </div>

        {/* Currency Options */}
        <div className="space-y-2">
          {CURRENCIES.map((currency) => (
            <Button
              key={currency.code}
              variant={
                currentCurrency === currency.code ? "default" : "outline"
              }
              onClick={() => handleCurrencyChange(currency.code)}
              disabled={updatePreferencesMutation.isPending}
              className="w-full justify-start"
            >
              {updatePreferencesMutation.isPending &&
                currentCurrency === currency.code && (
                  <Spinner size="sm" className="mr-2" />
                )}
              <span className="text-lg mr-3">{currency.symbol}</span>
              {currency.name}
            </Button>
          ))}
        </div>

        {/* Format Preview */}
        <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            Format Preview
          </p>
          <p className="text-lg font-semibold text-blue-900 dark:text-blue-100">
            {selectedCurrencyData?.symbol}1,234.56
          </p>
          <p className="text-xs text-blue-800 dark:text-blue-200 mt-1">
            All amounts will be displayed in this format
          </p>
        </div>
      </div>
    </Card>
  );
}
