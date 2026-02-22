import React, { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface AddOn {
  id: string;
  name: string;
  description?: string;
  price: number;
  duration?: number;
}

interface AddOnSelectorProps {
  addOns: AddOn[];
  selectedAddOnIds: string[];
  onAddOnsChange: (addOnIds: string[]) => void;
}

export const AddOnSelector: React.FC<AddOnSelectorProps> = ({
  addOns,
  selectedAddOnIds,
  onAddOnsChange,
}) => {
  const [expanded, setExpanded] = useState(false);

  if (!addOns || addOns.length === 0) {
    return null;
  }

  const handleAddOnToggle = (addOnId: string) => {
    const updated = selectedAddOnIds.includes(addOnId)
      ? selectedAddOnIds.filter((id) => id !== addOnId)
      : [...selectedAddOnIds, addOnId];
    onAddOnsChange(updated);
  };

  const totalAddOnPrice = addOns
    .filter((a) => selectedAddOnIds.includes(a.id))
    .reduce((sum, a) => sum + a.price, 0);

  return (
    <div className="space-y-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full p-2 border rounded hover:bg-gray-50"
      >
        <span className="font-medium text-sm">
          Add-Ons
          {selectedAddOnIds.length > 0 && (
            <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              {selectedAddOnIds.length} selected (+${totalAddOnPrice.toFixed(2)}
              )
            </span>
          )}
        </span>
        <span className="text-gray-500">{expanded ? "▼" : "▶"}</span>
      </button>

      {expanded && (
        <div className="space-y-3 p-3 border rounded bg-gray-50">
          {addOns.map((addOn) => (
            <div key={addOn.id} className="flex items-start space-x-3">
              <Checkbox
                id={`addon-${addOn.id}`}
                checked={selectedAddOnIds.includes(addOn.id)}
                onCheckedChange={() => handleAddOnToggle(addOn.id)}
              />
              <Label
                htmlFor={`addon-${addOn.id}`}
                className="flex-1 cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {addOn.name}
                    </p>
                    {addOn.description && (
                      <p className="text-xs text-gray-600">
                        {addOn.description}
                      </p>
                    )}
                  </div>
                  <div className="text-right ml-2">
                    <p className="text-sm font-medium text-gray-900">
                      +${addOn.price.toFixed(2)}
                    </p>
                    {addOn.duration && (
                      <p className="text-xs text-gray-600">
                        +{addOn.duration}min
                      </p>
                    )}
                  </div>
                </div>
              </Label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
