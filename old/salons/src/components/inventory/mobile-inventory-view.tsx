'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Minus, Camera, Barcode } from 'lucide-react';
import Image from 'next/image';

interface Product {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  price: number;
  thumbnail_url?: string;
  category: string;
}

interface MobileInventoryViewProps {
  onBarcodeClick?: () => void;
  onCameraClick?: () => void;
}

export function MobileInventoryView({
  onBarcodeClick,
  onCameraClick,
}: MobileInventoryViewProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [adjustingProductId, setAdjustingProductId] = useState<string | null>(null);
  const [adjustmentAmount, setAdjustmentAmount] = useState(1);

  const queryClient = useQueryClient();

  const { data: products, isLoading } = useQuery({
    queryKey: ['mobileInventory', searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      params.append('limit', '100');

      const res = await fetch(`/api/inventory/search/products?${params}`);
      if (!res.ok) throw new Error('Failed to fetch products');
      return res.json();
    },
  });

  const adjustMutation = useMutation({
    mutationFn: async ({
      productId,
      change,
    }: {
      productId: string;
      change: number;
    }) => {
      const res = await fetch(`/api/inventory/products/${productId}/adjust`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quantity_change: change,
          reason: 'Mobile adjustment',
        }),
      });
      if (!res.ok) throw new Error('Failed to adjust quantity');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mobileInventory'] });
      toast.success('Quantity updated');
      setAdjustingProductId(null);
      setAdjustmentAmount(1);
    },
    onError: () => {
      toast.error('Failed to update quantity');
    },
  });

  const productList = products?.data?.products || [];

  const getStockStatus = (quantity: number) => {
    if (quantity === 0) return { label: 'Out', color: 'bg-red-100 text-red-800' };
    if (quantity < 10) return { label: 'Low', color: 'bg-orange-100 text-orange-800' };
    if (quantity < 50) return { label: 'Medium', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'Good', color: 'bg-green-100 text-green-800' };
  };

  return (
    <div className="space-y-4 pb-20">
      {/* Quick Actions */}
      <div className="sticky top-0 bg-white p-4 border-b space-y-3 z-10">
        <Input
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full"
        />

        <div className="grid grid-cols-2 gap-2">
          <Button
            onClick={onBarcodeClick}
            variant="outline"
            className="w-full"
          >
            <Barcode className="w-4 h-4 mr-2" />
            Scan
          </Button>
          <Button
            onClick={onCameraClick}
            variant="outline"
            className="w-full"
          >
            <Camera className="w-4 h-4 mr-2" />
            Photo
          </Button>
        </div>
      </div>

      {/* Products List */}
      {isLoading ? (
        <div className="text-center py-8">Loading...</div>
      ) : productList.length > 0 ? (
        <div className="space-y-3 px-4">
          {productList.map((product: Product) => {
            const stockStatus = getStockStatus(product.quantity);
            const isAdjusting = adjustingProductId === product.id;

            return (
              <Card key={product.id} className="overflow-hidden">
                <CardContent className="p-4">
                  <div className="flex gap-3">
                    {/* Product Image */}
                    {product.thumbnail_url && (
                      <div className="relative w-16 h-16 flex-shrink-0 bg-gray-100 rounded">
                        <Image
                          src={product.thumbnail_url}
                          alt={product.name}
                          fill
                          className="object-cover rounded"
                        />
                      </div>
                    )}

                    {/* Product Info */}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm truncate">
                        {product.name}
                      </h3>
                      <p className="text-xs text-gray-500 truncate">
                        {product.sku}
                      </p>

                      <div className="flex items-center gap-2 mt-2">
                        <Badge
                          className={stockStatus.color}
                          variant="outline"
                        >
                          {product.quantity}
                        </Badge>
                        <span className="text-xs font-medium">
                          ${product.price.toFixed(2)}
                        </span>
                      </div>
                    </div>

                    {/* Quick Adjust */}
                    {!isAdjusting ? (
                      <div className="flex flex-col gap-1 justify-center">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            adjustMutation.mutate({
                              productId: product.id,
                              change: 1,
                            });
                          }}
                          disabled={adjustMutation.isPending}
                        >
                          <Plus className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            adjustMutation.mutate({
                              productId: product.id,
                              change: -1,
                            });
                          }}
                          disabled={adjustMutation.isPending}
                        >
                          <Minus className="w-4 h-4" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex flex-col gap-1 justify-center">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            adjustMutation.mutate({
                              productId: product.id,
                              change: adjustmentAmount,
                            });
                          }}
                          disabled={adjustMutation.isPending}
                        >
                          +{adjustmentAmount}
                        </Button>
                        <Input
                          type="number"
                          value={adjustmentAmount}
                          onChange={(e) =>
                            setAdjustmentAmount(parseInt(e.target.value) || 1)
                          }
                          className="w-12 h-8 text-xs"
                          min="1"
                        />
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500 px-4">
          No products found
        </div>
      )}
    </div>
  );
}
