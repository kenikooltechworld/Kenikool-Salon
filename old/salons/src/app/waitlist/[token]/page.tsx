'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { useWaitlistByToken, useUpdateClientInfo, useCancelWaitlist } from '@/lib/api/hooks/useWaitlistClient';
import { format } from 'date-fns';

interface PageProps {
  params: {
    token: string;
  };
}

export default function WaitlistClientPortalPage({ params }: PageProps) {
  const token = params.token;

  const { data: entry, isLoading, error } = useWaitlistByToken(token);
  const updateMutation = useUpdateClientInfo();
  const cancelMutation = useCancelWaitlist();

  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    client_name: '',
    client_phone: '',
    client_email: '',
  });
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  React.useEffect(() => {
    if (entry) {
      setFormData({
        client_name: entry.client_name,
        client_phone: entry.client_phone,
        client_email: entry.client_email || '',
      });
    }
  }, [entry]);

  const handleUpdateInfo = async () => {
    if (!formData.client_name || !formData.client_phone) {
      setErrorMessage('Name and phone are required');
      return;
    }

    try {
      await updateMutation.mutateAsync({
        token,
        client_name: formData.client_name,
        client_phone: formData.client_phone,
        client_email: formData.client_email,
      });
      setSuccessMessage('Information updated successfully');
      setEditMode(false);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to update information');
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your waitlist request?')) {
      return;
    }

    try {
      await cancelMutation.mutateAsync(token);
      setSuccessMessage('Your waitlist request has been cancelled');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to cancel request');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="text-center py-8">Loading your waitlist information...</div>
        </div>
      </div>
    );
  }

  if (error || !entry) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">
              {error?.message || 'Invalid or expired waitlist token. Please check your link and try again.'}
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    waiting: 'bg-yellow-100 text-yellow-800',
    notified: 'bg-blue-100 text-blue-800',
    booked: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    expired: 'bg-gray-100 text-gray-800',
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Your Waitlist Status</h1>
          <p className="text-gray-600">Manage your waitlist request and stay updated</p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <Alert className="mb-6 bg-green-50 border-green-200">
            <AlertDescription className="text-green-800">{successMessage}</AlertDescription>
          </Alert>
        )}

        {/* Error Message */}
        {errorMessage && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">{errorMessage}</AlertDescription>
          </Alert>
        )}

        {/* Status Card */}
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Request Status</h2>
            <Badge className={statusColors[entry.status]}>
              {entry.status.charAt(0).toUpperCase() + entry.status.slice(1)}
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Service</p>
              <p className="font-semibold">{entry.service_name}</p>
            </div>
            {entry.stylist_name && (
              <div>
                <p className="text-sm text-gray-600 mb-1">Preferred Stylist</p>
                <p className="font-semibold">{entry.stylist_name}</p>
              </div>
            )}
            {entry.location_name && (
              <div>
                <p className="text-sm text-gray-600 mb-1">Location</p>
                <p className="font-semibold">{entry.location_name}</p>
              </div>
            )}
            {entry.preferred_date && (
              <div>
                <p className="text-sm text-gray-600 mb-1">Preferred Date</p>
                <p className="font-semibold">{format(new Date(entry.preferred_date), 'MMM dd, yyyy')}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-gray-600 mb-1">Priority Score</p>
              <p className="font-semibold">{entry.priority_score.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Joined</p>
              <p className="font-semibold">{format(new Date(entry.created_at), 'MMM dd, yyyy')}</p>
            </div>
            {entry.notes && (
              <div className="md:col-span-2">
                <p className="text-sm text-gray-600 mb-1">Notes</p>
                <p className="font-semibold">{entry.notes}</p>
              </div>
            )}
          </div>
        </Card>

        {/* Contact Information */}
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Contact Information</h2>
            {!editMode && entry.status !== 'booked' && entry.status !== 'cancelled' && (
              <Button onClick={() => setEditMode(true)} variant="outline" size="sm">
                Edit
              </Button>
            )}
          </div>

          {editMode ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name</label>
                <Input
                  value={formData.client_name}
                  onChange={(e) => setFormData({ ...formData, client_name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Phone</label>
                <Input
                  value={formData.client_phone}
                  onChange={(e) => setFormData({ ...formData, client_phone: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <Input
                  type="email"
                  value={formData.client_email}
                  onChange={(e) => setFormData({ ...formData, client_email: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleUpdateInfo}
                  disabled={updateMutation.isPending}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button onClick={() => setEditMode(false)} variant="outline">
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Name</p>
                <p className="font-semibold">{entry.client_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Phone</p>
                <p className="font-semibold">{entry.client_phone}</p>
              </div>
              {entry.client_email && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Email</p>
                  <p className="font-semibold">{entry.client_email}</p>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Actions */}
        {entry.status !== 'booked' && entry.status !== 'cancelled' && entry.status !== 'expired' && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <Button
              onClick={handleCancel}
              disabled={cancelMutation.isPending}
              variant="destructive"
            >
              {cancelMutation.isPending ? 'Cancelling...' : 'Cancel Waitlist Request'}
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
}
