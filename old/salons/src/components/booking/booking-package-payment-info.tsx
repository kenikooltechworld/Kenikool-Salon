'use client';

import React from 'react';
import { useBookingPackageInfo } from '@/lib/api/hooks/useBookingPackageCredits';
import { format } from 'date-fns';

interface BookingPackagePaymentInfoProps {
  bookingId: string;
}

/**
 * Component for displaying package payment information in booking details
 * Requirements: 14.6
 */
export function BookingPackagePaymentInfo({
  bookingId,
}: BookingPackagePaymentInfoProps) {
  const { data: packageInfo, isLoading, error } = useBookingPackageInfo(bookingId);

  if (!packageInfo) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <div className="text-sm text-gray-500">Loading payment info...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="text-sm text-red-600">Error loading payment info</div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-green-200 bg-green-50 p-4">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-gray-900">Payment Method</span>
          <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
            Package Credit
          </span>
        </div>

        <div className="space-y-1 border-t border-green-200 pt-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Package</span>
            <span className="font-medium text-gray-900">{packageInfo.package_name}</span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Service Value</span>
            <span className="font-medium text-gray-900">
              ${packageInfo.service_value.toFixed(2)}
            </span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Remaining Credits</span>
            <span className="font-medium text-gray-900">
              {packageInfo.remaining_credits} credit
              {packageInfo.remaining_credits !== 1 ? 's' : ''}
            </span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Redeemed On</span>
            <span className="font-medium text-gray-900">
              {format(new Date(packageInfo.redemption_date), 'MMM d, yyyy')}
            </span>
          </div>
        </div>

        <div className="rounded-lg bg-green-100 p-2 text-center text-sm font-semibold text-green-800">
          Amount Saved: ${packageInfo.service_value.toFixed(2)}
        </div>
      </div>
    </div>
  );
}
