'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { X } from 'lucide-react';

export interface AdvancedFilters {
  paymentTypes: string[];
  minAmount?: number;
  maxAmount?: number;
  customerEmail?: string;
  statuses: string[];
  gateways: string[];
}

interface AdvancedFiltersPanelProps {
  filters: AdvancedFilters;
  onFiltersChange: (filters: AdvancedFilters) => void;
  onClose: () => void;
}

/**
 * Advanced Filters Panel Component
 * Allows filtering payments by type, amount range, customer email, status, and gateway
 * Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.8
 */
export function AdvancedFiltersPanel({
  filters,
  onFiltersChange,
  onClose,
}: AdvancedFiltersPanelProps) {
  const [localFilters, setLocalFilters] = useState<AdvancedFilters>(filters);

  const paymentTypeOptions = ['full', 'deposit', 'checkout'];
  const statusOptions = ['completed', 'pending', 'failed', 'refunded', 'partially_refunded'];
  const gatewayOptions = ['paystack', 'flutterwave'];

  const handlePaymentTypeToggle = (type: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      paymentTypes: prev.paymentTypes.includes(type)
        ? prev.paymentTypes.filter((t) => t !== type)
        : [...prev.paymentTypes, type],
    }));
  };

  const handleStatusToggle = (status: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      statuses: prev.statuses.includes(status)
        ? prev.statuses.filter((s) => s !== status)
        : [...prev.statuses, status],
    }));
  };

  const handleGatewayToggle = (gateway: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      gateways: prev.gateways.includes(gateway)
        ? prev.gateways.filter((g) => g !== gateway)
        : [...prev.gateways, gateway],
    }));
  };

  const handleApply = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  const handleClear = () => {
    const clearedFilters: AdvancedFilters = {
      paymentTypes: [],
      minAmount: undefined,
      maxAmount: undefined,
      customerEmail: undefined,
      statuses: [],
      gateways: [],
    };
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
    onClose();
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Advanced Filters</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Payment Type Filter */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-gray-700">Payment Type</Label>
        <div className="space-y-2">
          {paymentTypeOptions.map((type) => (
            <label key={type} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={localFilters.paymentTypes.includes(type)}
                onChange={() => handlePaymentTypeToggle(type)}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-sm text-gray-700 capitalize">{type}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Amount Range Filter */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-gray-700">Amount Range</Label>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-600">Min Amount</label>
            <Input
              type="number"
              min="0"
              step="0.01"
              value={localFilters.minAmount || ''}
              onChange={(e) =>
                setLocalFilters((prev) => ({
                  ...prev,
                  minAmount: e.target.value ? parseFloat(e.target.value) : undefined,
                }))
              }
              placeholder="0"
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Max Amount</label>
            <Input
              type="number"
              min="0"
              step="0.01"
              value={localFilters.maxAmount || ''}
              onChange={(e) =>
                setLocalFilters((prev) => ({
                  ...prev,
                  maxAmount: e.target.value ? parseFloat(e.target.value) : undefined,
                }))
              }
              placeholder="No limit"
              className="mt-1"
            />
          </div>
        </div>
      </div>

      {/* Customer Email Filter */}
      <div className="space-y-3">
        <Label htmlFor="customer-email" className="text-sm font-medium text-gray-700">
          Customer Email
        </Label>
        <Input
          id="customer-email"
          type="email"
          value={localFilters.customerEmail || ''}
          onChange={(e) =>
            setLocalFilters((prev) => ({
              ...prev,
              customerEmail: e.target.value || undefined,
            }))
          }
          placeholder="Search by email"
          className="mt-1"
        />
      </div>

      {/* Status Filter */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-gray-700">Status</Label>
        <div className="space-y-2">
          {statusOptions.map((status) => (
            <label key={status} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={localFilters.statuses.includes(status)}
                onChange={() => handleStatusToggle(status)}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-sm text-gray-700 capitalize">
                {status.replace('_', ' ')}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Gateway Filter */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-gray-700">Payment Gateway</Label>
        <div className="space-y-2">
          {gatewayOptions.map((gateway) => (
            <label key={gateway} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={localFilters.gateways.includes(gateway)}
                onChange={() => handleGatewayToggle(gateway)}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-sm text-gray-700 capitalize">{gateway}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 pt-4 border-t">
        <Button onClick={handleApply} className="flex-1">
          Apply Filters
        </Button>
        <Button variant="outline" onClick={handleClear} className="flex-1">
          Clear All
        </Button>
        <Button variant="outline" onClick={onClose} className="flex-1">
          Cancel
        </Button>
      </div>
    </div>
  );
}
