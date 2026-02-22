import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { DollarSignIcon, XIcon } from "@/components/icons";

interface TipHandlerProps {
  subtotal: number;
  onTipChange: (tipAmount: number, tipPercentage: number) => void;
  onClose?: () => void;
}

export default function TipHandler({
  subtotal,
  onTipChange,
  onClose,
}: TipHandlerProps) {
  const [tipType, setTipType] = useState<"percentage" | "fixed">("percentage");
  const [tipValue, setTipValue] = useState<number>(0);

  const tipPercentages = [10, 15, 18, 20];

  const calculateTip = (value: number) => {
    if (tipType === "percentage") {
      return (subtotal * value) / 100;
    }
    return value;
  };

  const handlePercentageSelect = (percentage: number) => {
    setTipType("percentage");
    setTipValue(percentage);
    const tipAmount = calculateTip(percentage);
    onTipChange(tipAmount, percentage);
  };

  const handleCustomTip = (value: number) => {
    setTipValue(value);
    if (tipType === "percentage") {
      const tipAmount = (subtotal * value) / 100;
      onTipChange(tipAmount, value);
    } else {
      onTipChange(value, 0);
    }
  };

  const handleTypeChange = (type: "percentage" | "fixed") => {
    setTipType(type);
    setTipValue(0);
    onTipChange(0, 0);
  };

  const currentTipAmount = calculateTip(tipValue);

  return (
    <Card className="p-4 md:p-6 border-2 border-primary">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base md:text-lg font-semibold text-foreground flex items-center gap-2">
          <DollarSignIcon size={20} />
          Add Tip
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
        {/* Tip Type Selection */}
        <div>
          <Label className="text-sm font-medium mb-2 block">Tip Type</Label>
          <RadioGroup
            value={tipType}
            onValueChange={(value: any) => handleTypeChange(value)}
          >
            <div className="flex gap-4">
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="percentage" id="tip-percentage" />
                <Label htmlFor="tip-percentage" className="cursor-pointer">
                  Percentage
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="fixed" id="tip-fixed" />
                <Label htmlFor="tip-fixed" className="cursor-pointer">
                  Fixed Amount
                </Label>
              </div>
            </div>
          </RadioGroup>
        </div>

        {/* Quick Tip Buttons */}
        {tipType === "percentage" && (
          <div>
            <Label className="text-sm font-medium mb-2 block">
              Quick Select
            </Label>
            <div className="grid grid-cols-4 gap-2">
              {tipPercentages.map((percentage) => (
                <Button
                  key={percentage}
                  variant={tipValue === percentage ? "primary" : "outline"}
                  onClick={() => handlePercentageSelect(percentage)}
                  className="text-sm"
                >
                  {percentage}%
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Custom Tip Input */}
        <div>
          <Label
            htmlFor="custom-tip"
            className="text-sm font-medium mb-2 block"
          >
            {tipType === "percentage" ? "Custom Percentage" : "Custom Amount"}
          </Label>
          <div className="flex gap-2">
            <Input
              id="custom-tip"
              type="number"
              placeholder={tipType === "percentage" ? "0" : "0.00"}
              value={tipValue || ""}
              onChange={(e) => handleCustomTip(parseFloat(e.target.value) || 0)}
              step={tipType === "percentage" ? "1" : "0.01"}
              min="0"
              className="flex-1"
            />
            {tipType === "percentage" && (
              <div className="flex items-center px-3 bg-muted rounded-md">
                <span className="text-sm font-medium">%</span>
              </div>
            )}
          </div>
        </div>

        {/* Tip Summary */}
        <div className="bg-muted p-3 rounded-lg">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Tip Amount</span>
            <span className="text-lg font-bold text-primary">
              ₦
              {currentTipAmount.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
          <div className="flex justify-between items-center mt-2 pt-2 border-t border-border">
            <span className="text-sm text-muted-foreground">
              Subtotal + Tip
            </span>
            <span className="text-lg font-bold text-foreground">
              ₦
              {(subtotal + currentTipAmount).toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
        </div>

        {/* No Tip Option */}
        <Button
          variant="outline"
          onClick={() => {
            setTipValue(0);
            onTipChange(0, 0);
          }}
          className="w-full"
        >
          No Tip
        </Button>
      </div>
    </Card>
  );
}
