'use client';

import { useState, useMemo } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useRecordManualPayment } from '@/lib/api/hooks/useRecordManualPayment';
import { useBookings } from '@/lib/api/hooks/useBookings';
import { ManualPaymentRequest, Booking } from '@/lib/api/types';
import { Loader2, AlertCircle, CheckCircle, Search } from 'lucide-react';
import { format } from 'date-fns';

interface ManualPaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

/**
 * Manual Payment Modal Component
 * Allows recording manual payments (cash, check, bank transfer, etc.)
 * Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
 */
export function ManualPaymentModal({
  isOpen,
  onClose,
  onSuccess,
}: ManualPaymentModalProps) {
  const [selectedBookingId, setSelectedBookingId] = useState('');
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<
    'cash' | 'bank_transfer' | 'check' | 'other'
  >('cash');
  const [reference, setReference] = useState('');
  const [notes, setNotes] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [step, setStep] = useState<'form' | 'confirm' | 'processing' | 'success' | 'error'>(
    'form'
  );
  const [errorMessage, setErrorMessage] = useState('');

  const { data: bookingsData } = useBookings({
    status: 'confirmed',
    limit: 100,
  });
  const { mutate: recordPayment, isPending } = useRecordManualPayment();

  if (!isOpen) return null;

  // Filter bookings based on search query and payment status
  const filteredBookings = useMemo(() => {
    if (!bookingsData?.items) return [];

    return bookingsData.items.filter((booking: Booking) => {
      // Only show bookings that don't have full payment
      const hasFullPayment = booking.payment_status === 'paid';
      if (hasFullPayment) return false;

      // Filter by search query (client name, phone, etc.)
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        return (
          booking.id?.toLowerCase().includes(query) ||
          booking.client_name?.toLowerCase().includes(query) ||
          booking.client_phone?.toLowerCase().includes(query)
        );
      }

      return true;
    });
  }, [bookingsData?.items, searchQuery]);

  const selectedBooking = bookingsData?.items?.find(
    (b: Booking) => b.id === selectedBookingId
  );
  const maxAmount = selectedBooking?.service_price || 0;
  const currentAmount = parseFloat(amount) || 0;
  const isValidAmount = currentAmount > 0 && currentAmount <= maxAmount;

  const handleSubmit = () => {
    if (!selectedBookingId) {
      setErrorMessage('Please select a booking');
      return;
    }
    if (!isValidAmount) {
      setErrorMessage(
        `Amount must be between 0 and ₦${maxAmount.toLocaleString()}`
      );
      return;
    }
    setStep('confirm');
  };

  const handleConfirm = () => {
    setStep('processing');
    setErrorMessage('');

    const paymentData: ManualPaymentRequest = {
      booking_id: selectedBookingId,
      amount: currentAmount,
      payment_method: paymentMethod,
      reference: reference.trim() || undefined,
      notes: notes.trim() || undefined,
    };

    recordPayment(paymentData, {
      onSuccess: () => {
        setStep('success');
        setTimeout(() => {
          onSuccess?.();
          handleClose();
        }, 2000);
      },
      onError: (error: any) => {
        setStep('error');
        setErrorMessage(
          error.response?.data?.message || 'Failed to record payment'
        );
      },
    });
  };

  const handleClose = () => {
    setStep('form');
    setSelectedBookingId('');
    setAmount('');
    setPaymentMethod('cash');
    setReference('');
    setNotes('');
    setSearchQuery('');
    setErrorMessage('');
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Record Manual Payment</DialogTitle>
        </DialogHeader>

        {/* Form Step */}
        {step === 'form' && (
          <div className="space-y-4">
            {/* Booking Selection */}
            <div className="space-y-2">
              <Label htmlFor="booking-search" className="text-sm font-medium">
                Select Booking
              </Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="booking-search"
                  type="text"
                  placeholder="Search by reference, client name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={selectedBookingId} onValueChange={setSelectedBookingId}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Choose a booking" />
                </SelectTrigger>
                <SelectContent>
                  {filteredBookings.length > 0 ? (
                    filteredBookings.map((booking: Booking) => (
                      <SelectItem key={booking.id} value={booking.id || ''}>
                        #{booking.id} - {booking.client_name} (₦{booking.service_price?.toLocaleString()})
                      </SelectItem>
                    ))
                  ) : (
                    <div className="p-2 text-sm text-gray-500">No bookings available</div>
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Booking Details */}
            {selectedBooking && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Client:</span>
                  <span className="font-semibold">{selectedBooking.client_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Booking Date:</span>
                  <span className="font-semibold">
                    {format(new Date(selectedBooking.booking_date), 'PPp')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Service Price:</span>
                  <span className="font-semibold">
                    ₦{selectedBooking.service_price?.toLocaleString()}
                  </span>
                </div>
              </div>
            )}

            {/* Payment Method */}
            <div className="space-y-2">
              <Label htmlFor="payment-method" className="text-sm font-medium">
                Payment Method
              </Label>
              <Select value={paymentMethod} onValueChange={(value: any) => setPaymentMethod(value)}>
                <SelectTrigger id="payment-method">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cash">Cash</SelectItem>
                  <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
                  <SelectItem value="check">Check</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Amount */}
            <div className="space-y-2">
              <Label htmlFor="amount" className="text-sm font-medium">
                Amount
              </Label>
              <Input
                id="amount"
                type="number"
                min="0"
                max={maxAmount}
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                disabled={!selectedBooking}
              />
              {amount && !isValidAmount && (
                <p className="text-xs text-red-600">
                  Amount must be between 0 and ₦{maxAmount.toLocaleString()}
                </p>
              )}
            </div>

            {/* Reference (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="reference" className="text-sm font-medium">
                Reference (Optional)
              </Label>
              <Input
                id="reference"
                type="text"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="e.g., Check #123, Transfer ID"
              />
            </div>

            {/* Notes (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="notes" className="text-sm font-medium">
                Notes (Optional)
              </Label>
              <Textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any additional notes"
                className="min-h-20"
              />
            </div>

            {errorMessage && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex gap-2 text-sm text-red-700">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleSubmit}
                disabled={!selectedBookingId || !isValidAmount}
                className="flex-1"
              >
                Continue
              </Button>
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Confirmation Step */}
        {step === 'confirm' && selectedBooking && (
          <div className="space-y-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-semibold text-yellow-900 mb-3">
                Confirm Payment
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Booking:</span>
                  <span className="font-semibold">#{selectedBooking.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Client:</span>
                  <span className="font-semibold">{selectedBooking.client_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Amount:</span>
                  <span className="font-semibold">
                    ₦{currentAmount.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Method:</span>
                  <span className="font-semibold capitalize">
                    {paymentMethod.replace('_', ' ')}
                  </span>
                </div>
                {reference && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Reference:</span>
                    <span className="font-semibold">{reference}</span>
                  </div>
                )}
              </div>
            </div>

            <p className="text-sm text-gray-600">
              This will record a manual payment for the booking. The booking status
              will be updated accordingly.
            </p>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleConfirm}
                disabled={isPending}
                className="flex-1"
              >
                {isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Confirm Payment
              </Button>
              <Button
                variant="outline"
                onClick={() => setStep('form')}
                disabled={isPending}
                className="flex-1"
              >
                Back
              </Button>
            </div>
          </div>
        )}

        {/* Processing Step */}
        {step === 'processing' && (
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <p className="text-center text-gray-600">Recording payment...</p>
          </div>
        )}

        {/* Success Step */}
        {step === 'success' && (
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <p className="text-center font-semibold text-green-600">
              Payment recorded successfully!
            </p>
            <p className="text-center text-sm text-gray-600">
              ₦{currentAmount.toLocaleString()} has been recorded for the booking.
            </p>
          </div>
        )}

        {/* Error Step */}
        {step === 'error' && (
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-red-900">Payment Failed</h4>
                <p className="text-sm text-red-700 mt-1">{errorMessage}</p>
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                onClick={() => setStep('form')}
                className="flex-1"
              >
                Try Again
              </Button>
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Close
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
