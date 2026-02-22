import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PlusIcon, TrashIcon } from "@/components/icons";

interface PriceTier {
  level: string;
  multiplier: number;
}

interface TieredPricingEditorProps {
  basePrice: number;
  tiers: PriceTier[];
  onChange: (tiers: PriceTier[]) => void;
}

export function TieredPricingEditor({
  basePrice,
  tiers,
  onChange,
}: TieredPricingEditorProps) {
  const [localTiers, setLocalTiers] = useState<PriceTier[]>(
    tiers.length > 0
      ? tiers
      : [
          { level: "Junior", multiplier: 1.0 },
          { level: "Senior", multiplier: 1.2 },
          { level: "Master", multiplier: 1.5 },
        ]
  );

  const handleAddTier = () => {
    const newTiers = [
      ...localTiers,
      { level: `Level ${localTiers.length + 1}`, multiplier: 1.0 },
    ];
    setLocalTiers(newTiers);
    onChange(newTiers);
  };

  const handleRemoveTier = (index: number) => {
    const newTiers = localTiers.filter((_, i) => i !== index);
    setLocalTiers(newTiers);
    onChange(newTiers);
  };

  const handleTierChange = (
    index: number,
    field: "level" | "multiplier",
    value: string | number
  ) => {
    const newTiers = [...localTiers];
    if (field === "level") {
      newTiers[index].level = value as string;
    } else {
      newTiers[index].multiplier = parseFloat(value as string) || 1.0;
    }
    setLocalTiers(newTiers);
    onChange(newTiers);
  };

  const calculatePrice = (multiplier: number) => {
    return basePrice * multiplier;
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-foreground">Tiered Pricing</h3>
          <p className="text-sm text-muted-foreground">
            Set different prices based on stylist experience level
          </p>
        </div>
        <Button size="sm" onClick={handleAddTier}>
          <PlusIcon size={16} className="mr-2" />
          Add Tier
        </Button>
      </div>

      <div className="space-y-3">
        {localTiers.map((tier, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-3 border border-border rounded-lg"
          >
            <div className="flex-1 grid grid-cols-3 gap-3">
              {/* Level Name */}
              <div>
                <Label htmlFor={`level-${index}`} className="text-xs">
                  Level Name
                </Label>
                <Input
                  id={`level-${index}`}
                  value={tier.level}
                  onChange={(e) =>
                    handleTierChange(index, "level", e.target.value)
                  }
                  placeholder="e.g., Junior, Senior"
                />
              </div>

              {/* Multiplier */}
              <div>
                <Label htmlFor={`multiplier-${index}`} className="text-xs">
                  Multiplier
                </Label>
                <Input
                  id={`multiplier-${index}`}
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={tier.multiplier}
                  onChange={(e) =>
                    handleTierChange(index, "multiplier", e.target.value)
                  }
                  placeholder="1.0"
                />
              </div>

              {/* Calculated Price */}
              <div>
                <Label className="text-xs">Final Price</Label>
                <div className="h-10 flex items-center px-3 bg-muted rounded-lg">
                  <span className="font-medium text-foreground">
                    ₦{calculatePrice(tier.multiplier).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Remove Button */}
            {localTiers.length > 1 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleRemoveTier(index)}
                className="mt-5"
              >
                <TrashIcon size={16} />
              </Button>
            )}
          </div>
        ))}
      </div>

      {/* Info */}
      <div className="mt-4 p-3 bg-muted/50 rounded-lg">
        <p className="text-sm text-muted-foreground">
          <strong>Base Price:</strong> ₦{basePrice.toLocaleString()}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          The multiplier is applied to the base price to calculate the final
          price for each tier. For example, a multiplier of 1.5 means the price
          will be 50% higher than the base price.
        </p>
      </div>
    </Card>
  );
}
