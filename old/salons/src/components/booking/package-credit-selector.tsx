'use client';

import React, { useState } from 'react';
import { useBookingPackageCredits } from '@/lib/api/hooks/useBookingPackageCredits';
import { PackageCredit } from '@/lib/api/hooks/useBookingPackageCredits';

interface PackageCreditSelectorProps {
  clientId: string;
  serviceId: string;
  servicePrice: number;
  onCreditSelected?: (credit: PackageCredit | null) => void;
  onPaymentMethodChange?: (method: 'cash' | 'card' | 'package') => void;
}

/**
 * Component for selecting package credits during booking
 * Requirements: 14.1, 14.2
 */
export function PackageCreditSelector({
  clientId,
  serviceId,
  servicePrice,
  onCreditSelected,
  onPaymentMethodChange,
}: PackageCreditSelectorProps) {
  const [selectedCreditId, setSelectedCreditId] = useState<string | null>(null);
  const [usePackageCredit, setUsePackageCredit] = useState(false);

  const { data: availableCredits = [], isLoading, error } = useBookingPackageCredits(
    clientId,
    serviceId
  );

  const handleTogglePackageCredit = (checked: boolean) => {
    setUsePackageCredit(checked);
    if (!checked) {
      setSelectedCreditId(null);
      onCreditSelected?.(null);
      onPaymentMethodChange?.('cash');
    } else {
      onPaymentMethodChange?.('package');
    }
  };

  const handleSelectCredit = (creditId: string) => {
    setSelectedCreditId(creditId);
    const selected = availableCredits.find((c) => c._id === creditId);
    onCreditSelected?.(selected || null);
  };

  if (!clientId || !serviceId) {
    return null;
  }

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Package Credits</h3>
        {availableCredits.length > 0 && (
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={usePackageCredit}
              onChange={(e) => handleTogglePackageCredit(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Use package credit</span>
          </label>
        )}
      </div>

      {isLoading && (
        <div className="text-sm text-gray-500">Loading available credits...</div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          Error loading package credits
        </div>
      )}

      {availableCredits.length === 0 && !isLoading && (
        <div className="text-sm text-gray-500">
          No package credits available for this service
        </div>
      )}

      {usePackageCredit && availableCredits.length > 0 && (
        <div className="space-y-3">
          {availableCredits.map((credit) => (
            <label
              key={credit._id}
              className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-3 hover:bg-gray-50"
            >
              <input
                type="radio"
                name="package-credit"
                value={credit._id}
                checked={selectedCreditId === credit._id}
                onChange={() => handleSelectCredit(credit._id)}
                className="mt-1 h-4 w-4"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900">
                  {credit.service_name}
                </div>
                <div className="text-sm text-gray-600">
                  {credit.remaining_quantity} credit
                  {credit.remaining_quantity !== 1 ? 's' : ''} remaining
                </div>
                <div className="text-sm font-semibold text-green-600">
                  Free (normally ${credit.service_price.toFixed(2)})
                </div>
              </div>
            </label>
          ))}

          {selectedCreditId && (
            <div className="rounded-lg bg-green-50 p-3 text-sm text-green-800">
              ✓ You'll save ${servicePrice.toFixed(2)} by using this package credit
            </div>
          )}
        </div>
      )}
    </div>
  );
}
