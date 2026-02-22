import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Spinner } from "@/components/ui/spinner";
import { CreditCardIcon, PlusIcon, XIcon } from "@/components/icons";

interface SavedPaymentMethod {
  id: string;
  type: "card" | "mobile_money" | "bank_transfer";
  label: string;
  lastFour?: string;
  isDefault: boolean;
}

interface QuickCheckoutProps {
  total: number;
  onCheckout: (paymentMethodId: string) => void;
  isProcessing?: boolean;
  onClose?: () => void;
}

export default function QuickCheckout({
  total,
  onCheckout,
  isProcessing = false,
  onClose,
}: QuickCheckoutProps) {
  const [savedMethods, setSavedMethods] = useState<SavedPaymentMethod[]>([
    {
      id: "1",
      type: "card",
      label: "Visa Card",
      lastFour: "4242",
      isDefault: true,
    },
    {
      id: "2",
      type: "mobile_money",
      label: "MTN Mobile Money",
      isDefault: false,
    },
  ]);
  const [selectedMethodId, setSelectedMethodId] = useState(
    savedMethods.find((m) => m.isDefault)?.id || savedMethods[0]?.id || "",
  );
  const [showAddNew, setShowAddNew] = useState(false);

  const handleQuickCheckout = () => {
    if (!selectedMethodId) {
      return;
    }
    onCheckout(selectedMethodId);
  };

  const handleRemoveMethod = (id: string) => {
    setSavedMethods(savedMethods.filter((m) => m.id !== id));
    if (selectedMethodId === id) {
      setSelectedMethodId(savedMethods[0]?.id || "");
    }
  };

  const selectedMethod = savedMethods.find((m) => m.id === selectedMethodId);

  return (
    <Card className="p-4 md:p-6 border-2 border-primary">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base md:text-lg font-semibold text-foreground flex items-center gap-2">
          <CreditCardIcon size={20} />
          Quick Checkout
        </h3>
        {onClose && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <XIcon size={16} />
          </Button>
        )}
      </div>

      <div className="space-y-4">
        {/* Saved Payment Methods */}
        {!showAddNew && (
          <>
            <div>
              <Label className="text-sm font-medium mb-3 block">
                Select Payment Method
              </Label>
              <RadioGroup
                value={selectedMethodId}
                onValueChange={setSelectedMethodId}
              >
                <div className="space-y-2">
                  {savedMethods.map((method) => (
                    <div
                      key={method.id}
                      className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted transition"
                    >
                      <div className="flex items-center space-x-3 flex-1">
                        <RadioGroupItem
                          value={method.id}
                          id={`method-${method.id}`}
                        />
                        <Label
                          htmlFor={`method-${method.id}`}
                          className="flex-1 cursor-pointer"
                        >
                          <div>
                            <p className="font-medium text-sm text-foreground">
                              {method.label}
                            </p>
                            {method.lastFour && (
                              <p className="text-xs text-muted-foreground">
                                •••• {method.lastFour}
                              </p>
                            )}
                            {method.isDefault && (
                              <p className="text-xs text-green-600">Default</p>
                            )}
                          </div>
                        </Label>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveMethod(method.id)}
                        className="text-muted-foreground hover:text-destructive"
                      >
                        <XIcon size={16} />
                      </Button>
                    </div>
                  ))}
                </div>
              </RadioGroup>
            </div>

            <Button
              variant="outline"
              onClick={() => setShowAddNew(true)}
              className="w-full"
            >
              <PlusIcon size={16} className="mr-2" />
              Add New Payment Method
            </Button>
          </>
        )}

        {/* Add New Method Form */}
        {showAddNew && (
          <div className="space-y-3 p-3 bg-muted rounded-lg">
            <p className="text-sm font-medium text-foreground">
              Add New Payment Method
            </p>
            <p className="text-xs text-muted-foreground">
              Feature coming soon. Use standard payment options.
            </p>
            <Button
              variant="outline"
              onClick={() => setShowAddNew(false)}
              className="w-full"
            >
              Back
            </Button>
          </div>
        )}

        {/* Amount Summary */}
        <div className="bg-muted p-3 rounded-lg">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Total Amount</span>
            <span className="text-xl font-bold text-primary">
              ₦
              {total.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
          {selectedMethod && (
            <div className="flex justify-between items-center mt-2 pt-2 border-t border-border">
              <span className="text-xs text-muted-foreground">
                Paying with {selectedMethod.label}
              </span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isProcessing}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            onClick={handleQuickCheckout}
            disabled={isProcessing || !selectedMethodId}
            className="flex-1"
          >
            {isProcessing ? (
              <>
                <Spinner className="w-4 h-4 mr-2" />
                Processing...
              </>
            ) : (
              "Complete Payment"
            )}
          </Button>
        </div>
      </div>
    </Card>
  );
}
