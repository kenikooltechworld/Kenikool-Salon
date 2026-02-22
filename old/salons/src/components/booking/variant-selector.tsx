import React, { useState } from "react";
import { Button } from "@/components/ui/button";

interface Variant {
  id: string;
  name: string;
  description?: string;
  priceModifier: number;
  durationModifier: number;
}

interface VariantSelectorProps {
  variants: Variant[];
  selectedVariantId?: string;
  onVariantSelect: (
    variantId: string,
    priceModifier: number,
    durationModifier: number,
  ) => void;
  basePrice: number;
  baseDuration: number;
}

export const VariantSelector: React.FC<VariantSelectorProps> = ({
  variants,
  selectedVariantId,
  onVariantSelect,
  basePrice,
  baseDuration,
}) => {
  const [expanded, setExpanded] = useState(false);
  const selectedVariant = variants.find((v) => v.id === selectedVariantId);

  if (!variants || variants.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full p-2 border rounded hover:bg-gray-50"
      >
        <span className="font-medium text-sm">
          Service Variant
          {selectedVariant && (
            <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              {selectedVariant.name}
            </span>
          )}
        </span>
        <span className="text-gray-500">{expanded ? "▼" : "▶"}</span>
      </button>

      {expanded && (
        <div className="space-y-2 p-3 border rounded bg-gray-50">
          {variants.map((variant) => {
            const newPrice = basePrice + variant.priceModifier;
            const newDuration = baseDuration + variant.durationModifier;
            const isSelected = selectedVariantId === variant.id;

            return (
              <button
                key={variant.id}
                onClick={() => {
                  onVariantSelect(
                    variant.id,
                    variant.priceModifier,
                    variant.durationModifier,
                  );
                  setExpanded(false);
                }}
                className={`w-full text-left p-3 rounded border-2 transition ${
                  isSelected
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">
                      {variant.name}
                    </p>
                    {variant.description && (
                      <p className="text-xs text-gray-600 mt-1">
                        {variant.description}
                      </p>
                    )}
                  </div>
                  <div className="text-right ml-2">
                    <p className="text-sm font-medium text-gray-900">
                      ${newPrice.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-600">{newDuration} min</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
