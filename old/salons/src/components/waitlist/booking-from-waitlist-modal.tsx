'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCreateBookingFromWaitlist, WaitlistEntry } from '@/lib/api/hooks/useWaitlist';
import { format } from 'date-fns';

interface BookingFromWaitlistModalProps {
  entry: WaitlistEntry | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export const BookingFromWaitlistModal: React.FC<BookingFromWaitlistModalProps> = ({
  entry,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [bookingDate, setBookingDate] = useState('');
  const [bookingTime, setBookingTime] = useState('');
  const [error, setError] = useState('');
  const createBookingMutation = useCreateBookingFromWaitlist();

  const handleCreateBooking = async () => {
    if (!bookingDate || !bookingTime) {
      setError('Please select both date and time');
      return;
    }

    if (!entry) {
      setError('No entry selected');
      return;
    }

    try {
      await createBookingMutation.mutateAsync({
        waitlist_id: entry.id,
        booking_date: bookingDate,
        booking_time: bookingTime,
      });

      setBookingDate('');
      setBookingTime('');
      setError('');
      onClose();
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Failed to create booking');
    }
  };

  if (!entry) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Create Booking from Waitlist</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Entry Details */}
          <Card className="p-4 bg-gray-50">
            <h3 className="font-semibold mb-4">Waitlist Entry Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Client Name</p>
                <p className="font-medium">{entry.client_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{entry.client_phone}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{entry.client_email || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Service</p>
                <p className="font-medium">{entry.service_name}</p>
              </div>
              {entry.stylist_name && (
                <div>
                  <p className="text-sm text-gray-600">Stylist</p>
                  <p className="font-medium">{entry.stylist_name}</p>
                </div>
              )}
              {entry.location_name && (
                <div>
                  <p className="text-sm text-gray-600">Location</p>
                  <p className="font-medium">{entry.location_name}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-600">Priority Score</p>
                <p className="font-medium">{entry.priority_score.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Joined</p>
                <p className="font-medium">{format(new Date(entry.created_at), 'MMM dd, yyyy')}</p>
              </div>
            </div>
          </Card>

          {/* Booking Details */}
          <div className="space-y-4">
            <h3 className="font-semibold">Booking Details</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Booking Date</label>
                <Input
                  type="date"
                  value={bookingDate}
                  onChange={(e) => setBookingDate(e.target.value)}
                  min={format(new Date(), 'yyyy-MM-dd')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Booking Time</label>
                <Input
                  type="time"
                  value={bookingTime}
                  onChange={(e) => setBookingTime(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {/* Success Message */}
          {createBookingMutation.isSuccess && (
            <Alert className="bg-green-50 border-green-200">
              <AlertDescription className="text-green-800">
                Booking created successfully!
              </AlertDescription>
            </Alert>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateBooking}
              disabled={createBookingMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {createBookingMutation.isPending ? 'Creating...' : 'Create Booking'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
