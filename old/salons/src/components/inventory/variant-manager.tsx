'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Trash2, Plus } from 'lucide-react';

interface Variant {
  id: string;
  type: string;
  value: string;
  sku: string;
  quantity: number;
  price: number;
  cost_price: number;
}

interface VariantManagerProps {
  productId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function VariantManager({
  productId,
  isOpen,
  onClose,
}: VariantManagerProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    variant_type: '',
    variant_value: '',
    sku: '',
    quantity: 0,
    price: 0,
    cost_price: 0,
  });

  const queryClient = useQueryClient();

  const { data: variants } = useQuery({
    queryKey: ['variants', productId],
    queryFn: async () => {
      const res = await fetch(`/api/inventory/variants/product/${productId}`);
      if (!res.ok) throw new Error('Failed to fetch variants');
      return res.json();
    },
    enabled: isOpen,
  });

  const addMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/inventory/variants/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: productId,
          ...formData,
        }),
      });
      if (!res.ok) throw new Error('Failed to add variant');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variants', productId] });
      toast.success('Variant added');
      setFormData({
        variant_type: '',
        variant_value: '',
        sku: '',
        quantity: 0,
        price: 0,
        cost_price: 0,
      });
      setShowAddForm(false);
    },
    onError: () => {
      toast.error('Failed to add variant');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (variantId: string) => {
      const res = await fetch(`/api/inventory/variants/${variantId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete variant');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variants', productId] });
      toast.success('Variant deleted');
    },
    onError: () => {
      toast.error('Failed to delete variant');
    },
  });

  const variantList = variants?.data || [];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px]">
        <DialogHeader>
          <DialogTitle>Manage Variants</DialogTitle>
        </DialogHeader>

        {!showAddForm ? (
          <div className="space-y-4">
            {variantList.length > 0 ? (
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Type</TableHead>
                      <TableHead>Value</TableHead>
                      <TableHead>SKU</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Cost</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {variantList.map((variant: Variant) => (
                      <TableRow key={variant.id}>
                        <TableCell className="font-medium">
                          {variant.type}
                        </TableCell>
                        <TableCell>{variant.value}</TableCell>
                        <TableCell className="text-sm text-gray-600">
                          {variant.sku}
                        </TableCell>
                        <TableCell>{variant.quantity}</TableCell>
                        <TableCell>${variant.price.toFixed(2)}</TableCell>
                        <TableCell>${variant.cost_price.toFixed(2)}</TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteMutation.mutate(variant.id)}
                            disabled={deleteMutation.isPending}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No variants yet
              </div>
            )}

            <Button
              onClick={() => setShowAddForm(true)}
              className="w-full"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Variant
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="type">Variant Type</Label>
                <Input
                  id="type"
                  placeholder="e.g., Size, Color"
                  value={formData.variant_type}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      variant_type: e.target.value,
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="value">Variant Value</Label>
                <Input
                  id="value"
                  placeholder="e.g., Large, Red"
                  value={formData.variant_value}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      variant_value: e.target.value,
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="sku">SKU</Label>
                <Input
                  id="sku"
                  placeholder="SKU"
                  value={formData.sku}
                  onChange={(e) =>
                    setFormData({ ...formData, sku: e.target.value })
                  }
                />
              </div>
              <div>
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      quantity: parseInt(e.target.value),
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="price">Price</Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      price: parseFloat(e.target.value),
                    })
                  }
                />
              </div>
              <div>
                <Label htmlFor="cost">Cost Price</Label>
                <Input
                  id="cost"
                  type="number"
                  step="0.01"
                  value={formData.cost_price}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      cost_price: parseFloat(e.target.value),
                    })
                  }
                />
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowAddForm(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={() => addMutation.mutate()}
                disabled={addMutation.isPending}
              >
                {addMutation.isPending ? 'Adding...' : 'Add Variant'}
              </Button>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
