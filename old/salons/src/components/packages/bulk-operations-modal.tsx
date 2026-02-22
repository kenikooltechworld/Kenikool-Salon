'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertCircle, CheckCircle, X } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface BulkOperationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface OperationResult {
  operation: string;
  total_requested: number;
  successful: number;
  failed: number;
  successful_ids: string[];
  failed_details: Array<{
    package_id?: string;
    purchase_id?: string;
    error: string;
  }>;
  timestamp: string;
}

export function BulkOperationsModal({
  isOpen,
  onClose,
  onSuccess,
}: BulkOperationsModalProps) {
  const [operationType, setOperationType] = useState<'activate' | 'deactivate' | 'prices' | 'extend'>('activate');
  const [packageIds, setPackageIds] = useState('');
  const [purchaseIds, setPurchaseIds] = useState('');
  const [priceUpdates, setPriceUpdates] = useState('');
  const [extensionDays, setExtensionDays] = useState('30');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OperationResult | null>(null);

  const handleClose = () => {
    setPackageIds('');
    setPurchaseIds('');
    setPriceUpdates('');
    setExtensionDays('30');
    setError(null);
    setResult(null);
    onClose();
  };

  const parsePackageIds = (input: string): string[] => {
    return input
      .split(/[\n,;]/)
      .map(id => id.trim())
      .filter(id => id.length > 0);
  };

  const parsePriceUpdates = (input: string): Array<{ package_id: string; new_price: number }> => {
    return input
      .split('\n')
      .map(line => {
        const [id, price] = line.split(':').map(s => s.trim());
        return { package_id: id, new_price: parseFloat(price) };
      })
      .filter(item => item.package_id && !isNaN(item.new_price));
  };

  const handleExecute = async () => {
    setError(null);
    setResult(null);

    try {
      let response;

      switch (operationType) {
        case 'activate': {
          const ids = parsePackageIds(packageIds);
          if (ids.length === 0) {
            setError('Please enter at least one package ID');
            return;
          }
          response = await apiClient.post('/packages/bulk/activate', {
            package_ids: ids,
          });
          break;
        }

        case 'deactivate': {
          const ids = parsePackageIds(packageIds);
          if (ids.length === 0) {
            setError('Please enter at least one package ID');
            return;
          }
          response = await apiClient.post('/packages/bulk/deactivate', {
            package_ids: ids,
          });
          break;
        }

        case 'prices': {
          const updates = parsePriceUpdates(priceUpdates);
          if (updates.length === 0) {
            setError('Please enter at least one price update (format: package_id:price)');
            return;
          }
          response = await apiClient.post('/packages/bulk/update-prices', {
            package_updates: updates,
          });
          break;
        }

        case 'extend': {
          const ids = parsePackageIds(purchaseIds);
          const days = parseInt(extensionDays);
          if (ids.length === 0) {
            setError('Please enter at least one purchase ID');
            return;
          }
          if (isNaN(days) || days <= 0) {
            setError('Please enter a valid number of days');
            return;
          }
          response = await apiClient.post('/packages/purchases/bulk/extend', {
            purchase_updates: ids.map(id => ({
              purchase_id: id,
              additional_days: days,
            })),
          });
          break;
        }
      }

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Operation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const getOperationTitle = () => {
    switch (operationType) {
      case 'activate':
        return 'Bulk Activate Packages';
      case 'deactivate':
        return 'Bulk Deactivate Packages';
      case 'prices':
        return 'Bulk Update Prices';
      case 'extend':
        return 'Bulk Extend Expiration';
      default:
        return 'Bulk Operations';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{getOperationTitle()}</DialogTitle>
          <DialogDescription>
            Perform bulk operations on multiple packages with transaction support
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-4 py-6">
            <div className="flex justify-center">
              <CheckCircle className="w-12 h-12 text-green-600" />
            </div>
            <p className="text-center text-lg font-semibold text-gray-900">
              Operation Completed
            </p>

            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-600">Total Requested</p>
                <p className="text-2xl font-bold text-blue-900">{result.total_requested}</p>
              </div>
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-600">Successful</p>
                <p className="text-2xl font-bold text-green-900">{result.successful}</p>
              </div>
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">Failed</p>
                <p className="text-2xl font-bold text-red-900">{result.failed}</p>
              </div>
            </div>

            {result.failed_details.length > 0 && (
              <div className="space-y-2">
                <p className="font-semibold text-gray-900">Failed Operations:</p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {result.failed_details.map((failure, idx) => (
                    <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm font-medium text-red-900">
                        {failure.package_id || failure.purchase_id}
                      </p>
                      <p className="text-sm text-red-700">{failure.error}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="text-xs text-gray-500">
              Operation completed at {new Date(result.timestamp).toLocaleString()}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <Tabs value={operationType} onValueChange={(v) => setOperationType(v as any)}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="activate">Activate</TabsTrigger>
                <TabsTrigger value="deactivate">Deactivate</TabsTrigger>
                <TabsTrigger value="prices">Prices</TabsTrigger>
                <TabsTrigger value="extend">Extend</TabsTrigger>
              </TabsList>

              <TabsContent value="activate" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="package-ids">Package IDs to Activate</Label>
                  <p className="text-xs text-gray-600">
                    Enter one ID per line or separate with commas/semicolons
                  </p>
                  <textarea
                    id="package-ids"
                    placeholder="pkg_1&#10;pkg_2&#10;pkg_3"
                    value={packageIds}
                    onChange={(e) => setPackageIds(e.target.value)}
                    disabled={isLoading}
                    className="w-full h-32 p-3 border border-gray-300 rounded-md font-mono text-sm"
                  />
                </div>
              </TabsContent>

              <TabsContent value="deactivate" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="package-ids-deactivate">Package IDs to Deactivate</Label>
                  <p className="text-xs text-gray-600">
                    Enter one ID per line or separate with commas/semicolons
                  </p>
                  <textarea
                    id="package-ids-deactivate"
                    placeholder="pkg_1&#10;pkg_2&#10;pkg_3"
                    value={packageIds}
                    onChange={(e) => setPackageIds(e.target.value)}
                    disabled={isLoading}
                    className="w-full h-32 p-3 border border-gray-300 rounded-md font-mono text-sm"
                  />
                </div>
              </TabsContent>

              <TabsContent value="prices" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="price-updates">Price Updates</Label>
                  <p className="text-xs text-gray-600">
                    Format: package_id:new_price (one per line)
                  </p>
                  <textarea
                    id="price-updates"
                    placeholder="pkg_1:99.99&#10;pkg_2:149.99&#10;pkg_3:199.99"
                    value={priceUpdates}
                    onChange={(e) => setPriceUpdates(e.target.value)}
                    disabled={isLoading}
                    className="w-full h-32 p-3 border border-gray-300 rounded-md font-mono text-sm"
                  />
                </div>
              </TabsContent>

              <TabsContent value="extend" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="purchase-ids">Purchase IDs to Extend</Label>
                  <p className="text-xs text-gray-600">
                    Enter one ID per line or separate with commas/semicolons
                  </p>
                  <textarea
                    id="purchase-ids"
                    placeholder="purch_1&#10;purch_2&#10;purch_3"
                    value={purchaseIds}
                    onChange={(e) => setPurchaseIds(e.target.value)}
                    disabled={isLoading}
                    className="w-full h-32 p-3 border border-gray-300 rounded-md font-mono text-sm"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="extension-days">Additional Days</Label>
                  <Input
                    id="extension-days"
                    type="number"
                    min="1"
                    value={extensionDays}
                    onChange={(e) => setExtensionDays(e.target.value)}
                    disabled={isLoading}
                    placeholder="30"
                  />
                </div>
              </TabsContent>
            </Tabs>

            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            <Alert className="border-blue-200 bg-blue-50">
              <AlertCircle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                All operations are performed within a database transaction. Either all operations succeed or all are rolled back.
              </AlertDescription>
            </Alert>
          </div>
        )}

        {!result && (
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleExecute}
              disabled={isLoading}
              className="gap-2"
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Execute Operation
            </Button>
          </DialogFooter>
        )}

        {result && (
          <DialogFooter>
            <Button
              onClick={() => {
                handleClose();
                onSuccess?.();
              }}
            >
              Close
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}
