'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PackagePurchaseDetails } from '@/lib/api/hooks/useClientPackages';
import { PackageTransferModal } from './package-transfer-modal';
import { PackageRefundModal } from './package-refund-modal';
import { Send, RotateCcw } from 'lucide-react';

interface PackageDetailsModalProps {
  package: PackagePurchaseDetails | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh?: () => void;
}

export function PackageDetailsModal({
  package: pkg,
  isOpen,
  onClose,
  onRefresh,
}: PackageDetailsModalProps) {
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);

  if (!pkg) return null;

  const totalValue = pkg.credits.reduce((sum, c) => sum + (c.service_price * c.initial_quantity), 0);
  const remainingValue = pkg.credits.reduce((sum, c) => sum + (c.service_price * c.remaining_quantity), 0);
  const savings = totalValue - pkg.amount_paid;
  const totalCredits = pkg.credits.reduce((sum, c) => sum + c.remaining_quantity, 0);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{pkg.package_name}</DialogTitle>
        </DialogHeader>

        {/* Action Buttons */}
        {pkg.status === 'active' && totalCredits > 0 && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowTransferModal(true)}
              className="gap-2"
            >
              <Send className="w-4 h-4" />
              Transfer
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRefundModal(true)}
              className="gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Refund
            </Button>
          </div>
        )}

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="credits">Credits</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">Status</p>
                <Badge className={
                  pkg.status === 'active' ? 'bg-green-600' :
                  pkg.status === 'expired' ? 'bg-red-600' :
                  pkg.status === 'fully_redeemed' ? 'bg-blue-600' :
                  'bg-gray-600'
                }>
                  {pkg.status.replace('_', ' ').toUpperCase()}
                </Badge>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Days Remaining</p>
                <p className="text-lg font-semibold">
                  {pkg.days_remaining > 0 ? pkg.days_remaining : 'Expired'}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Purchase Date</p>
                <p className="text-sm">
                  {new Date(pkg.purchase_date).toLocaleDateString()}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Expiration Date</p>
                <p className="text-sm">
                  {new Date(pkg.expiration_date).toLocaleDateString()}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Price Paid</p>
                <p className="text-lg font-semibold">
                  ${pkg.amount_paid.toFixed(2)}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-lg font-semibold">
                  ${totalValue.toFixed(2)}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Your Savings</p>
                <p className="text-lg font-semibold text-green-600">
                  ${savings.toFixed(2)}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm text-gray-600">Remaining Value</p>
                <p className="text-lg font-semibold">
                  ${remainingValue.toFixed(2)}
                </p>
              </div>
            </div>

            {pkg.is_gift && (
              <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-md">
                <p className="text-sm text-purple-900">
                  <span className="font-semibold">Gift Package</span>
                  {pkg.gift_message && (
                    <>
                      <br />
                      <span className="italic">"{pkg.gift_message}"</span>
                    </>
                  )}
                </p>
              </div>
            )}

            <p className="text-sm text-gray-600 mt-4">
              {pkg.package_description}
            </p>
          </TabsContent>

          {/* Credits Tab */}
          <TabsContent value="credits" className="space-y-4">
            <div className="space-y-3">
              {pkg.credits.map((credit) => (
                <div key={credit._id} className="p-3 border border-gray-200 rounded-md">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium">{credit.service_name}</p>
                      <p className="text-sm text-gray-600">
                        ${credit.service_price.toFixed(2)} per service
                      </p>
                    </div>
                    <Badge variant="outline">
                      {credit.remaining_quantity} / {credit.initial_quantity}
                    </Badge>
                  </div>

                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Available</span>
                      <span className="font-medium">{credit.remaining_quantity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Reserved</span>
                      <span className="font-medium">{credit.reserved_quantity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Used</span>
                      <span className="font-medium">
                        {credit.initial_quantity - credit.remaining_quantity - credit.reserved_quantity}
                      </span>
                    </div>
                  </div>

                  <div className="mt-2 text-sm">
                    <span className="text-gray-600">Status: </span>
                    <Badge variant="outline" className="ml-1">
                      {credit.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-4">
            {pkg.redemption_history && pkg.redemption_history.length > 0 ? (
              <div className="space-y-2">
                {pkg.redemption_history.map((redemption) => (
                  <div key={redemption._id} className="p-3 border border-gray-200 rounded-md">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{redemption.service_name}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(redemption.redemption_date).toLocaleDateString()} at{' '}
                          {new Date(redemption.redemption_date).toLocaleTimeString()}
                        </p>
                      </div>
                      <p className="font-semibold">
                        ${redemption.service_value.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-600 py-8">
                No redemptions yet
              </p>
            )}
          </TabsContent>
        </Tabs>

        <PackageTransferModal
          package={pkg}
          isOpen={showTransferModal}
          onClose={() => setShowTransferModal(false)}
          onSuccess={() => {
            onRefresh?.();
            onClose();
          }}
        />

        <PackageRefundModal
          package={pkg}
          isOpen={showRefundModal}
          onClose={() => setShowRefundModal(false)}
          onSuccess={() => {
            onRefresh?.();
            onClose();
          }}
        />
      </DialogContent>
    </Dialog>
  );
}
