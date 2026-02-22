'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
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
import { Switch } from '@/components/ui/switch';

interface AlertPreferencesModalProps {
  productId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function AlertPreferencesModal({
  productId,
  isOpen,
  onClose,
}: AlertPreferencesModalProps) {
  const [formData, setFormData] = useState({
    email_notifications: true,
    sms_notifications: false,
    email: '',
    phone: '',
    low_stock_threshold: 10,
    critical_stock_level: 5,
  });

  const { data: preferences } = useQuery({
    queryKey: ['alertPreferences', productId],
    queryFn: async () => {
      const res = await fetch(`/api/inventory/alerts/preferences/${productId}`);
      if (!res.ok) throw new Error('Failed to fetch preferences');
      return res.json();
    },
    enabled: isOpen,
  });

  useEffect(() => {
    if (preferences?.data) {
      setFormData(preferences.data);
    }
  }, [preferences]);

  const updateMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`/api/inventory/alerts/preferences/${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!res.ok) throw new Error('Failed to update preferences');
      return res.json();
    },
    onSuccess: () => {
      toast.success('Alert preferences updated');
      onClose();
    },
    onError: () => {
      toast.error('Failed to update preferences');
    },
  });

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Alert Preferences</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Email Notifications</Label>
            <Switch
              checked={formData.email_notifications}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, email_notifications: checked })
              }
            />
          </div>

          {formData.email_notifications && (
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                placeholder="your@email.com"
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <Label>SMS Notifications</Label>
            <Switch
              checked={formData.sms_notifications}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, sms_notifications: checked })
              }
            />
          </div>

          {formData.sms_notifications && (
            <div>
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) =>
                  setFormData({ ...formData, phone: e.target.value })
                }
                placeholder="+1234567890"
              />
            </div>
          )}

          <div>
            <Label htmlFor="low-stock">Low Stock Threshold</Label>
            <Input
              id="low-stock"
              type="number"
              value={formData.low_stock_threshold}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  low_stock_threshold: parseFloat(e.target.value),
                })
              }
              min="1"
            />
          </div>

          <div>
            <Label htmlFor="critical-stock">Critical Stock Level</Label>
            <Input
              id="critical-stock"
              type="number"
              value={formData.critical_stock_level}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  critical_stock_level: parseFloat(e.target.value),
                })
              }
              min="1"
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => updateMutation.mutate()}
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? 'Saving...' : 'Save Preferences'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
