import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calculator, Users, Percent, DollarSign } from "@/components/icons";
import { toast } from "sonner";
import { formatCurrency } from "@/lib/utils/currency";

interface SplitPaymentCalculatorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  totalAmount: number;
  onSplitCalculated: (
    splits: Array<{ amount: number; method: string }>
  ) => void;
}

export function SplitPaymentCalculator({
  open,
  onOpenChange,
  totalAmount,
  onSplitCalculated,
}: SplitPaymentCalculatorProps) {
  const [splitMode, setSplitMode] = useState<
    "equal" | "percentage" | "amount" | "person"
  >("equal");
  const [numberOfPeople, setNumberOfPeople] = useState(2);
  const [customSplits, setCustomSplits] = useState<
    Array<{ amount: number; percentage: number }>
  >([
    { amount: 0, percentage: 0 },
    { amount: 0, percentage: 0 },
  ]);

  const calculateEqualSplit = () => {
    const amountPerPerson = totalAmount / numberOfPeople;
    const splits = Array(numberOfPeople).fill({
      amount: amountPerPerson,
      method: "cash",
    });
    return splits;
  };

  const calculatePercentageSplit = () => {
    const totalPercentage = customSplits.reduce(
      (sum, split) => sum + split.percentage,
      0
    );

    if (Math.abs(totalPercentage - 100) > 0.01) {
      toast.error("Percentages must add up to 100%");
      return null;
    }

    return customSplits.map((split) => ({
      amount: (totalAmount * split.percentage) / 100,
      method: "cash",
    }));
  };

  const calculateAmountSplit = () => {
    const totalSplit = customSplits.reduce(
      (sum, split) => sum + split.amount,
      0
    );

    if (Math.abs(totalSplit - totalAmount) > 0.01) {
      toast.error(`Amounts must add up to ${formatCurrency(totalAmount)}`);
      return null;
    }

    return customSplits.map((split) => ({
      amount: split.amount,
      method: "cash",
    }));
  };

  const handleApplySplit = () => {
    let splits;

    switch (splitMode) {
      case "equal":
        splits = calculateEqualSplit();
        break;
      case "percentage":
        splits = calculatePercentageSplit();
        break;
      case "amount":
        splits = calculateAmountSplit();
        break;
      case "person":
        splits = calculateEqualSplit();
        break;
      default:
        return;
    }

    if (splits) {
      onSplitCalculated(splits);
      onOpenChange(false);
      toast.success("Split payment calculated");
    }
  };

  const updateCustomSplit = (
    index: number,
    field: "amount" | "percentage",
    value: number
  ) => {
    const newSplits = [...customSplits];
    newSplits[index] = { ...newSplits[index], [field]: value };
    setCustomSplits(newSplits);
  };

  const addSplit = () => {
    setCustomSplits([...customSplits, { amount: 0, percentage: 0 }]);
  };

  const removeSplit = (index: number) => {
    if (customSplits.length > 2) {
      setCustomSplits(customSplits.filter((_, i) => i !== index));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Split Payment Calculator</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Total Amount Display */}
          <div className="p-4 bg-primary/10 rounded-lg">
            <div className="text-sm text-muted-foreground">Total Amount</div>
            <div className="text-3xl font-bold">
              {formatCurrency(totalAmount)}
            </div>
          </div>

          {/* Split Mode Selection */}
          <div className="grid grid-cols-4 gap-2">
            <Button
              variant={splitMode === "equal" ? "primary" : "outline"}
              onClick={() => setSplitMode("equal")}
              className="flex flex-col h-auto py-4"
            >
              <Users className="h-5 w-5 mb-2" />
              <span className="text-xs">Equal Split</span>
            </Button>
            <Button
              variant={splitMode === "percentage" ? "primary" : "outline"}
              onClick={() => setSplitMode("percentage")}
              className="flex flex-col h-auto py-4"
            >
              <Percent className="h-5 w-5 mb-2" />
              <span className="text-xs">By Percentage</span>
            </Button>
            <Button
              variant={splitMode === "amount" ? "primary" : "outline"}
              onClick={() => setSplitMode("amount")}
              className="flex flex-col h-auto py-4"
            >
              <DollarSign className="h-5 w-5 mb-2" />
              <span className="text-xs">By Amount</span>
            </Button>
            <Button
              variant={splitMode === "person" ? "primary" : "outline"}
              onClick={() => setSplitMode("person")}
              className="flex flex-col h-auto py-4"
            >
              <Calculator className="h-5 w-5 mb-2" />
              <span className="text-xs">Per Person</span>
            </Button>
          </div>

          {/* Split Configuration */}
          <div className="space-y-4">
            {splitMode === "equal" || splitMode === "person" ? (
              <div>
                <Label>Number of People</Label>
                <Input
                  type="number"
                  min="2"
                  max="10"
                  value={numberOfPeople}
                  onChange={(e) =>
                    setNumberOfPeople(parseInt(e.target.value) || 2)
                  }
                />
                <div className="mt-2 text-sm text-muted-foreground">
                  Each person pays:{" "}
                  {formatCurrency(totalAmount / numberOfPeople)}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {customSplits.map((split, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="flex-1">
                      <Label>Person {index + 1}</Label>
                      {splitMode === "percentage" ? (
                        <div className="flex items-center gap-2">
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            step="0.01"
                            value={split.percentage}
                            onChange={(e) =>
                              updateCustomSplit(
                                index,
                                "percentage",
                                parseFloat(e.target.value) || 0
                              )
                            }
                            placeholder="Percentage"
                          />
                          <span className="text-sm">%</span>
                          <span className="text-sm text-muted-foreground">
                            ={" "}
                            {formatCurrency(
                              (totalAmount * split.percentage) / 100
                            )}
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Input
                            type="number"
                            min="0"
                            step="0.01"
                            value={split.amount}
                            onChange={(e) =>
                              updateCustomSplit(
                                index,
                                "amount",
                                parseFloat(e.target.value) || 0
                              )
                            }
                            placeholder="Amount"
                          />
                        </div>
                      )}
                    </div>
                    {customSplits.length > 2 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeSplit(index)}
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
                <Button variant="outline" size="sm" onClick={addSplit}>
                  Add Person
                </Button>
                <div className="text-sm text-muted-foreground">
                  {splitMode === "percentage" ? (
                    <>
                      Total:{" "}
                      {customSplits
                        .reduce((sum, s) => sum + s.percentage, 0)
                        .toFixed(2)}
                      %
                    </>
                  ) : (
                    <>
                      Total:{" "}
                      {formatCurrency(
                        customSplits.reduce((sum, s) => sum + s.amount, 0)
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button onClick={handleApplySplit}>Apply Split</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
