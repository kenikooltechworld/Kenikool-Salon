'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
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
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useCreatePackagePurchase, PackageDefinition } from '@/lib/api/hooks/usePackageSales';
import { useToast } from '@/hooks/use-toast';
import { Gift, AlertCircle } from 'lucide-react';
import { formatCurrency } from '@/lib/utils/currency';

interface PackageSaleModalProps {
  package: PackageDefinition | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (purchase: any) => void;
  clients: Array<{ _id: string; name: string; email: string }>;
}

export function PackageSaleModal({
  package: pkg,
  isOpen,
  onClose,
  onSuccess,
  clients,
}: PackageSaleModalProps) {
  const { toast } = useToast();
  const [selectedClientId, setSelectedClientId] = useState<string>('');
  const [paymentMethod, setPaymentMethod] = useState<string>('cash');
  const [isGift, setIsGift] = useState(false);
  const [recipientClientId, setRecipientClientId] = useState<string>('');
  const [giftMessage, setGiftMessage] = useState('');
  const [clientSearch, setClientSearch] = useState('');

  const createPurchaseMutation = useCreatePackagePurchase();

  if (!pkg) return null;

  const totalValue = pkg.services.reduce(
    (sum, s) => sum + s.price * s.quantity,
    0
  );
  const savings = totalValue - pkg.package_price;

  const filteredClients = clients.filter(
    (c) =>
      c.name.toLowerCase().includes(clientSearch.toLowerCase()) ||
      c.email.toLowerCase().includes(clientSearch.toLowerCase())
  );

  const selectedClient = clients.find((c) => c._id === selectedClientId);
  const selectedRecipient = clients.find((c) => c._id === recipientClientId);

  const handlePurchase = async () => {
    if (!selectedClientId) {
      toast('Please select a client', 'error');
      return;
    }

    if (isGift && !recipientClientId) {
      toast('Please select a recipient for the gift', 'error');
      return;
    }

    try {
      const result = await createPurchaseMutation.mutateAsync({
        package_definition_id: pkg._id,
        client_id: isGift ? recipientClientId : selectedClientId,
        payment_method: paymentMethod,
        is_gift: isGift,
        recipient_id: isGift ? recipientClientId : undefined,
        gift_message: isGift ? giftMessage : undefined,
      });

      toast('Package purchased successfully', 'success');
      onSuccess?.(result);
      onClose();
    } catch (error: any) {
      toast(
        error.response?.data?.detail || 'Failed to process purchase',
        'error'
      );
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Sell Package: {pkg.name}</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="client">Client</TabsTrigger>
            <TabsTrigger value="payment">Payment</TabsTrigger>
          </TabsList>

          {/* Details Tab */}
          <TabsContent value="details" className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Description</p>
              <p className="text-sm">{pkg.description}</p>
            </div>

            <div className="space-y-3">
              <p className="font-semibold">Services Included:</p>
              {pkg.services.map((service) => (
                <div
                  key={service.service_id}
                  className="p-3 border border-gray-200 rounded-md"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{service.service_name}</p>
                      <p className="text-sm text-gray-600">
                        {formatCurrency(service.price)} per service
                      </p>
                    </div>
                    <Badge variant="outline">Qty: {service.quantity}</Badge>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    Total: {formatCurrency(service.price * service.quantity)}
                  </div>
                </div>
              ))}
            </div>

            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-700">Original Value:</span>
                  <span className="font-semibold">
                    {formatCurrency(pkg.original_price)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Package Price:</span>
                  <span className="font-semibold text-lg">
                    {formatCurrency(pkg.package_price)}
                  </span>
                </div>
                <div className="flex justify-between border-t pt-2">
                  <span className="text-green-700 font-semibold">
                    Client Savings:
                  </span>
                  <span className="font-bold text-green-700">
                    {formatCurrency(savings)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Discount:</span>
                  <span className="font-semibold">
                    {pkg.discount_percentage}%
                  </span>
                </div>
              </CardContent>
            </Card>

            {pkg.validity_days && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-md">
                <p className="text-sm text-amber-900">
                  <span className="font-semibold">Valid for:</span>{' '}
                  {pkg.validity_days} days from purchase
                </p>
              </div>
            )}
          </TabsContent>

          {/* Client Tab */}
          <TabsContent value="client" className="space-y-4">
            <div className="space-y-3">
              <div>
                <Label htmlFor="client-search">Search Client</Label>
                <Input
                  id="client-search"
                  type="text"
                  placeholder="Search by name or email..."
                  value={clientSearch}
                  onChange={(e) => setClientSearch(e.target.value)}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="client-select">Select Client</Label>
                <Select value={selectedClientId} onValueChange={setSelectedClientId}>
                  <SelectTrigger id="client-select" className="mt-2">
                    <SelectValue placeholder="Choose a client..." />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredClients.map((client) => (
                      <SelectItem key={client._id} value={client._id}>
                        <div className="flex flex-col">
                          <span>{client.name}</span>
                          <span className="text-xs text-gray-500">
                            {client.email}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedClient && (
                <Card>
                  <CardContent className="pt-4">
                    <p className="font-semibold">{selectedClient.name}</p>
                    <p className="text-sm text-gray-600">{selectedClient.email}</p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Gift Option */}
            <div className="space-y-3 p-4 border border-purple-200 rounded-lg bg-purple-50">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="is-gift"
                  checked={isGift}
                  onCheckedChange={(checked) => {
                    setIsGift(checked as boolean);
                    if (!checked) {
                      setRecipientClientId('');
                      setGiftMessage('');
                    }
                  }}
                />
                <Label htmlFor="is-gift" className="flex items-center gap-2 cursor-pointer">
                  <Gift className="w-4 h-4" />
                  This is a gift package
                </Label>
              </div>

              {isGift && (
                <div className="space-y-3 mt-3">
                  <div>
                    <Label htmlFor="recipient-select">Gift Recipient</Label>
                    <Select
                      value={recipientClientId}
                      onValueChange={setRecipientClientId}
                    >
                      <SelectTrigger id="recipient-select" className="mt-2">
                        <SelectValue placeholder="Choose recipient..." />
                      </SelectTrigger>
                      <SelectContent>
                        {filteredClients.map((client) => (
                          <SelectItem key={client._id} value={client._id}>
                            {client.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="gift-message">Gift Message (Optional)</Label>
                    <Input
                      id="gift-message"
                      type="text"
                      placeholder="Add a personal message..."
                      value={giftMessage}
                      onChange={(e) => setGiftMessage(e.target.value)}
                      className="mt-2"
                      maxLength={200}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {giftMessage.length}/200 characters
                    </p>
                  </div>

                  {selectedRecipient && (
                    <div className="p-2 bg-white border border-purple-200 rounded">
                      <p className="text-sm">
                        <span className="font-semibold">Gift to:</span>{' '}
                        {selectedRecipient.name}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          {/* Payment Tab */}
          <TabsContent value="payment" className="space-y-4">
            <div>
              <Label htmlFor="payment-method">Payment Method</Label>
              <Select value={paymentMethod} onValueChange={setPaymentMethod}>
                <SelectTrigger id="payment-method" className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cash">Cash</SelectItem>
                  <SelectItem value="card">Card</SelectItem>
                  <SelectItem value="transfer">Bank Transfer</SelectItem>
                  <SelectItem value="check">Check</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Card className="bg-gray-50">
              <CardHeader>
                <CardTitle className="text-lg">Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span>Package:</span>
                  <span className="font-semibold">{pkg.name}</span>
                </div>
                <div className="flex justify-between">
                  <span>Client:</span>
                  <span className="font-semibold">
                    {selectedClient?.name || 'Not selected'}
                  </span>
                </div>
                {isGift && (
                  <div className="flex justify-between">
                    <span>Gift to:</span>
                    <span className="font-semibold">
                      {selectedRecipient?.name || 'Not selected'}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Payment Method:</span>
                  <span className="font-semibold capitalize">{paymentMethod}</span>
                </div>
                <div className="border-t pt-3 flex justify-between">
                  <span className="font-semibold">Total Amount:</span>
                  <span className="text-xl font-bold text-green-600">
                    {formatCurrency(pkg.package_price)}
                  </span>
                </div>
              </CardContent>
            </Card>

            {!selectedClientId && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md flex gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">
                  Please select a client before proceeding with payment
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>

        <div className="flex gap-2 justify-end mt-6">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handlePurchase}
            disabled={
              !selectedClientId ||
              (isGift && !recipientClientId) ||
              createPurchaseMutation.isPending
            }
          >
            {createPurchaseMutation.isPending
              ? 'Processing...'
              : `Complete Sale (${formatCurrency(pkg.package_price)})`}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
