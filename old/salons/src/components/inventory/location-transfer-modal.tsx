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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { ArrowRight, CheckCircle2, XCircle } from 'lucide-react';

interface Location {
  id: string;
  name: string;
  quantity: number;
  reorder_point: number;
}

interface Transfer {
  id: string;
  source_location_id: string;
  destination_location_id: string;
  quantity: number;
  status: string;
  created_at: string;
}

interface LocationTransferModalProps {
  productId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function LocationTransferModal({
  productId,
  isOpen,
  onClose,
}: LocationTransferModalProps) {
  const [sourceLocationId, setSourceLocationId] = useState('');
  const [destinationLocationId, setDestinationLocationId] = useState('');
  const [quantity, setQuantity] = useState(0);
  const [reason, setReason] = useState('stock_transfer');

  const queryClient = useQueryClient();

  const { data: locationsData } = useQuery({
    queryKey: ['locations', productId],
    queryFn: async () => {
      const res = await fetch(`/api/inventory/locations/product/${productId}`);
      if (!res.ok) throw new Error('Failed to fetch locations');
      return res.json();
    },
    enabled: isOpen,
  });

  const { data: transfersData } = useQuery({
    queryKey: ['transfers', productId],
    queryFn: async () => {
      const res = await fetch(
        `/api/inventory/locations/transfers?product_id=${productId}`
      );
      if (!res.ok) throw new Error('Failed to fetch transfers');
      return res.json();
    },
    enabled: isOpen,
  });

  const createTransferMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/inventory/locations/transfer/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: productId,
          source_location_id: sourceLocationId,
          destination_location_id: destinationLocationId,
          quantity,
          reason,
        }),
      });
      if (!res.ok) throw new Error('Failed to create transfer');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transfers', productId] });
      toast.success('Transfer created');
      setSourceLocationId('');
      setDestinationLocationId('');
      setQuantity(0);
    },
    onError: () => {
      toast.error('Failed to create transfer');
    },
  });

  const completeTransferMutation = useMutation({
    mutationFn: async (transferId: string) => {
      const res = await fetch(
        `/api/inventory/locations/transfer/${transferId}/complete`,
        { method: 'POST' }
      );
      if (!res.ok) throw new Error('Failed to complete transfer');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transfers', productId] });
      queryClient.invalidateQueries({ queryKey: ['locations', productId] });
      toast.success('Transfer completed');
    },
    onError: () => {
      toast.error('Failed to complete transfer');
    },
  });

  const cancelTransferMutation = useMutation({
    mutationFn: async (transferId: string) => {
      const res = await fetch(
        `/api/inventory/locations/transfer/${transferId}/cancel`,
        { method: 'POST' }
      );
      if (!res.ok) throw new Error('Failed to cancel transfer');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transfers', productId] });
      toast.success('Transfer cancelled');
    },
    onError: () => {
      toast.error('Failed to cancel transfer');
    },
  });

  const locations = locationsData?.data || [];
  const transfers = transfersData?.data || [];
  const sourceLocation = locations.find((l: Location) => l.id === sourceLocationId);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px]">
        <DialogHeader>
          <DialogTitle>Stock Transfer Between Locations</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Create Transfer Form */}
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold">Create New Transfer</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="source">Source Location</Label>
                <Select value={sourceLocationId} onValueChange={setSourceLocationId}>
                  <SelectTrigger id="source">
                    <SelectValue placeholder="Select source" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((loc: Location) => (
                      <SelectItem key={loc.id} value={loc.id}>
                        {loc.name} ({loc.quantity} available)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="destination">Destination Location</Label>
                <Select
                  value={destinationLocationId}
                  onValueChange={setDestinationLocationId}
                >
                  <SelectTrigger id="destination">
                    <SelectValue placeholder="Select destination" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations
                      .filter((l: Location) => l.id !== sourceLocationId)
                      .map((loc: Location) => (
                        <SelectItem key={loc.id} value={loc.id}>
                          {loc.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value))}
                  max={sourceLocation?.quantity || 0}
                  min="1"
                />
              </div>

              <div>
                <Label htmlFor="reason">Reason</Label>
                <Select value={reason} onValueChange={setReason}>
                  <SelectTrigger id="reason">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stock_transfer">Stock Transfer</SelectItem>
                    <SelectItem value="rebalance">Rebalance</SelectItem>
                    <SelectItem value="consolidation">Consolidation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={() => createTransferMutation.mutate()}
              disabled={
                !sourceLocationId ||
                !destinationLocationId ||
                quantity <= 0 ||
                createTransferMutation.isPending
              }
              className="w-full"
            >
              {createTransferMutation.isPending ? 'Creating...' : 'Create Transfer'}
            </Button>
          </div>

          {/* Transfers List */}
          {transfers.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Pending Transfers</h3>
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>From</TableHead>
                      <TableHead>To</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {transfers.map((transfer: Transfer) => {
                      const source = locations.find(
                        (l: Location) => l.id === transfer.source_location_id
                      );
                      const dest = locations.find(
                        (l: Location) => l.id === transfer.destination_location_id
                      );

                      return (
                        <TableRow key={transfer.id}>
                          <TableCell>{source?.name}</TableCell>
                          <TableCell>{dest?.name}</TableCell>
                          <TableCell>{transfer.quantity}</TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                transfer.status === 'pending'
                                  ? 'outline'
                                  : 'secondary'
                              }
                            >
                              {transfer.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {transfer.status === 'pending' && (
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() =>
                                    completeTransferMutation.mutate(transfer.id)
                                  }
                                  disabled={completeTransferMutation.isPending}
                                >
                                  <CheckCircle2 className="w-4 h-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() =>
                                    cancelTransferMutation.mutate(transfer.id)
                                  }
                                  disabled={cancelTransferMutation.isPending}
                                >
                                  <XCircle className="w-4 h-4" />
                                </Button>
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
