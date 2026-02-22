import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface Currency {
  code: string;
  symbol: string;
  name: string;
  rate: number; // Exchange rate relative to USD
}

const CURRENCIES: Currency[] = [
  { code: "USD", symbol: "$", name: "US Dollar", rate: 1.0 },
  { code: "EUR", symbol: "€", name: "Euro", rate: 0.92 },
  { code: "GBP", symbol: "£", name: "British Pound", rate: 0.79 },
  { code: "NGN", symbol: "₦", name: "Nigerian Naira", rate: 1550.0 },
  { code: "CAD", symbol: "C$", name: "Canadian Dollar", rate: 1.36 },
  { code: "AUD", symbol: "A$", name: "Australian Dollar", rate: 1.53 },
  { code: "JPY", symbol: "¥", name: "Japanese Yen", rate: 149.5 },
  { code: "CNY", symbol: "¥", name: "Chinese Yuan", rate: 7.24 },
];

interface CurrencySelectorProps {
  open: boolean;
  onClose: () => void;
  amount: number;
  onCurrencySelected: (convertedAmount: number, currency: string) => void;
}

export function CurrencySelector({
  open,
  onClose,
  amount,
  onCurrencySelected,
}: CurrencySelectorProps) {
  const [selectedCurrency, setSelectedCurrency] = useState("USD");

  // Compute converted amount based on selected currency
  const selectedCurrencyData = CURRENCIES.find(
    (c) => c.code === selectedCurrency
  );
  const convertedAmount = selectedCurrencyData
    ? amount * selectedCurrencyData.rate
    : amount;

  const handleClose = () => {
    setSelectedCurrency("USD");
    onClose();
  };

  const handleConfirm = () => {
    onCurrencySelected(convertedAmount, selectedCurrency);
    handleClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Select Payment Currency</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Original Amount */}
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">Original Amount</p>
            <p className="text-2xl font-bold">{formatCurrency(amount)} USD</p>
          </div>

          {/* Currency Selection */}
          <div className="space-y-2">
            <Label htmlFor="currency">Select Currency</Label>
            <Select
              value={selectedCurrency}
              onValueChange={setSelectedCurrency}
            >
              <SelectTrigger id="currency">
                <SelectValue>
                  {selectedCurrencyData
                    ? `${selectedCurrencyData.symbol} ${selectedCurrencyData.code} - ${selectedCurrencyData.name}`
                    : "Select currency"}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {CURRENCIES.map((currency) => (
                  <SelectItem key={currency.code} value={currency.code}>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{currency.symbol}</span>
                      <span>{currency.code}</span>
                      <span className="text-muted-foreground text-sm">
                        - {currency.name}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Converted Amount */}
          <div className="space-y-2">
            <Label htmlFor="converted-amount">Converted Amount</Label>
            <Input
              id="converted-amount"
              type="text"
              value={`${
                selectedCurrencyData?.symbol || "$"
              }${convertedAmount.toFixed(2)}`}
              readOnly
              className="text-lg font-semibold"
            />
            <p className="text-xs text-muted-foreground">
              Exchange rate: 1 USD = {selectedCurrencyData?.rate.toFixed(2)}{" "}
              {selectedCurrency}
            </p>
          </div>

          {/* Info */}
          <div className="p-3 bg-[var(--muted)] border border-[var(--border)] rounded-lg">
            <p className="text-sm text-[var(--foreground)]">
              The customer will pay in {selectedCurrencyData?.name}. The amount
              will be converted at the current exchange rate.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button onClick={handleConfirm}>
            Confirm Payment in {selectedCurrency}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
