/**
 * CreditSlider Component
 * Slider for selecting credit amount to apply
 */
import React from "react";

interface CreditSliderProps {
  creditsToApply: number;
  maxApplicable: number;
  onSliderChange: (value: number) => void;
  loading?: boolean;
}

export const CreditSlider: React.FC<CreditSliderProps> = ({
  creditsToApply,
  maxApplicable,
  onSliderChange,
  loading = false,
}) => {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <label className="font-medium text-foreground">Credits to Apply</label>
        <span className="font-semibold text-primary">
          ${creditsToApply.toFixed(2)}
        </span>
      </div>
      <input
        type="range"
        min="0"
        max={maxApplicable}
        step="0.01"
        value={creditsToApply}
        onChange={(e) => onSliderChange(parseFloat(e.target.value))}
        disabled={loading}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>$0</span>
        <span>${maxApplicable.toFixed(2)}</span>
      </div>
    </div>
  );
};

export default CreditSlider;
