import React from "react";
import { AlertCircle } from "lucide-react";

interface NoShowFeeCalculatorProps {
  bookingPrice: number;
  noShowFeePercentage?: number;
  noShowFeeFixed?: number;
  isNoShow: boolean;
}

export const NoShowFeeCalculator: React.FC<NoShowFeeCalculatorProps> = ({
  bookingPrice,
  noShowFeePercentage = 0,
  noShowFeeFixed = 0,
  isNoShow,
}) => {
  if (!isNoShow) {
    return null;
  }

  const percentageFee = (bookingPrice * noShowFeePercentage) / 100;
  const totalFee = percentageFee + noShowFeeFixed;

  return (
    <div className="space-y-3 rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-2">
        <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-medium text-red-900">No-Show Fee</h3>
          <p className="text-sm text-red-800 mt-1">
            A no-show fee will be charged for this booking
          </p>
        </div>
      </div>

      <div className="space-y-2 rounded bg-white p-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Original Booking Price</span>
          <span className="font-medium text-gray-900">
            ${bookingPrice.toFixed(2)}
          </span>
        </div>

        {percentageFee > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              No-Show Fee ({noShowFeePercentage}%)
            </span>
            <span className="font-medium text-red-600">
              +${percentageFee.toFixed(2)}
            </span>
          </div>
        )}

        {noShowFeeFixed > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Fixed No-Show Fee</span>
            <span className="font-medium text-red-600">
              +${noShowFeeFixed.toFixed(2)}
            </span>
          </div>
        )}

        {totalFee > 0 && (
          <>
            <div className="border-t border-gray-200" />
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-900">Total Charge</span>
              <span className="text-lg font-bold text-red-600">
                ${(bookingPrice + totalFee).toFixed(2)}
              </span>
            </div>
          </>
        )}
      </div>

      <p className="text-xs text-red-800">
        The no-show fee will be charged to the customer's account or payment
        method.
      </p>
    </div>
  );
};
