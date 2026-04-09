import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useServiceAddons } from "@/hooks/useServiceAddons";
import {
  CheckIcon as Check,
  Plus,
  MinusIcon as Minus,
} from "@/components/icons";

interface ServiceAddonSelectorProps {
  serviceId: string;
  onAddonsChange: (
    addons: Array<{ addon_id: string; quantity: number }>,
  ) => void;
}

export default function ServiceAddonSelector({
  serviceId,
  onAddonsChange,
}: ServiceAddonSelectorProps) {
  const { data: addons, isLoading } = useServiceAddons(serviceId);
  const [selectedAddons, setSelectedAddons] = useState<Record<string, number>>(
    {},
  );

  const handleToggleAddon = (addonId: string) => {
    const newSelected = { ...selectedAddons };
    if (newSelected[addonId]) {
      delete newSelected[addonId];
    } else {
      newSelected[addonId] = 1;
    }
    setSelectedAddons(newSelected);

    // Notify parent
    const addonsArray = Object.entries(newSelected).map(
      ([addon_id, quantity]) => ({
        addon_id,
        quantity,
      }),
    );
    onAddonsChange(addonsArray);
  };

  const handleQuantityChange = (addonId: string, delta: number) => {
    const newSelected = { ...selectedAddons };
    const currentQty = newSelected[addonId] || 0;
    const newQty = Math.max(1, currentQty + delta);

    newSelected[addonId] = newQty;
    setSelectedAddons(newSelected);

    // Notify parent
    const addonsArray = Object.entries(newSelected).map(
      ([addon_id, quantity]) => ({
        addon_id,
        quantity,
      }),
    );
    onAddonsChange(addonsArray);
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "product":
        return "bg-blue-100 text-blue-800";
      case "upgrade":
        return "bg-purple-100 text-purple-800";
      case "treatment":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return (
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-4">Loading add-ons...</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-4 animate-pulse">
              <div className="h-20 bg-gray-200 rounded"></div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!addons || addons.length === 0) return null;

  const totalAddonsPrice = Object.entries(selectedAddons).reduce(
    (sum, [addonId, qty]) => {
      const addon = addons.find((a) => a.id === addonId);
      return sum + (addon ? addon.price * qty : 0);
    },
    0,
  );

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Enhance Your Experience</h3>
        {Object.keys(selectedAddons).length > 0 && (
          <Badge variant="secondary" className="text-sm">
            +${totalAddonsPrice.toFixed(2)} total
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {addons.map((addon) => {
          const isSelected = !!selectedAddons[addon.id];
          const quantity = selectedAddons[addon.id] || 1;

          return (
            <Card
              key={addon.id}
              className={`p-4 transition-all cursor-pointer ${
                isSelected
                  ? "border-blue-500 bg-blue-50 shadow-md"
                  : "hover:border-gray-400 hover:shadow-sm"
              }`}
              onClick={() => !isSelected && handleToggleAddon(addon.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{addon.name}</h4>
                    <Badge className={getCategoryColor(addon.category)}>
                      {addon.category}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {addon.description}
                  </p>
                  <div className="flex items-center gap-4">
                    <span className="text-lg font-semibold text-blue-600">
                      +${addon.price.toFixed(2)}
                    </span>
                    <span className="text-sm text-gray-500">
                      +{addon.duration_minutes} min
                    </span>
                  </div>

                  {isSelected && (
                    <div
                      className="flex items-center gap-2 mt-3"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleQuantityChange(addon.id, -1)}
                        disabled={quantity <= 1}
                      >
                        <Minus className="h-3 w-3" />
                      </Button>
                      <span className="text-sm font-medium w-8 text-center">
                        {quantity}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleQuantityChange(addon.id, 1)}
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleToggleAddon(addon.id)}
                        className="ml-auto text-red-600 hover:text-red-700"
                      >
                        Remove
                      </Button>
                    </div>
                  )}
                </div>

                {addon.image_url && (
                  <img
                    src={addon.image_url}
                    alt={addon.name}
                    className="w-16 h-16 object-cover rounded ml-4"
                  />
                )}

                {isSelected && !addon.image_url && (
                  <div className="ml-4">
                    <Check className="h-6 w-6 text-blue-600" />
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
