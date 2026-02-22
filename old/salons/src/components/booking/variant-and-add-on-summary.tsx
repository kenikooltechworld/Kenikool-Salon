import React from "react";

interface VariantAndAddOnSummaryProps {
  selectedVariant?: {
    name: string;
    priceModifier: number;
  };
  selectedAddOns?: Array<{
    name: string;
    price: number;
  }>;
  basePrice: number;
  baseDuration: number;
  variantDurationModifier?: number;
  addOnDurationModifier?: number;
}

export const VariantAndAddOnSummary: React.FC<VariantAndAddOnSummaryProps> = ({
  selectedVariant,
  selectedAddOns = [],
  basePrice,
  baseDuration,
  variantDurationModifier = 0,
  addOnDurationModifier = 0,
}) => {
  const variantPrice = selectedVariant?.priceModifier || 0;
  const addOnsPrice = selectedAddOns.reduce((sum, a) => sum + a.price, 0);
  const totalPrice = basePrice + variantPrice + addOnsPrice;
  const totalDuration =
    baseDuration + variantDurationModifier + addOnDurationModifier;

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-gray-50 p-4">
      <h3 className="font-medium text-gray-900">Service Summary</h3>

      {/* Base Service */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">Base Service</span>
        <span className="font-medium text-gray-900">
          ${basePrice.toFixed(2)}
        </span>
      </div>

      {/* Variant */}
      {selectedVariant && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            Variant: <span className="font-medium">{selectedVariant.name}</span>
          </span>
          <span className="font-medium text-gray-900">
            {variantPrice > 0 ? "+" : ""}${variantPrice.toFixed(2)}
          </span>
        </div>
      )}

      {/* Add-Ons */}
      {selectedAddOns.length > 0 && (
        <div className="space-y-1">
          {selectedAddOns.map((addOn, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between text-sm"
            >
              <span className="text-gray-600">
                Add-on: <span className="font-medium">{addOn.name}</span>
              </span>
              <span className="font-medium text-gray-900">
                +${addOn.price.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Divider */}
      <div className="border-t border-gray-200" />

      {/* Total */}
      <div className="flex items-center justify-between">
        <span className="font-medium text-gray-900">Total</span>
        <div className="text-right">
          <p className="text-lg font-bold text-gray-900">
            ${totalPrice.toFixed(2)}
          </p>
          <p className="text-xs text-gray-600">{totalDuration} minutes</p>
        </div>
      </div>
    </div>
  );
};
