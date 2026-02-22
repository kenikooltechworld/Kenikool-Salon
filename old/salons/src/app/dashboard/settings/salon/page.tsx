'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Spinner } from '@/components/ui/spinner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { CheckCircleIcon, AlertCircleIcon } from '@/components/icons';

interface ReferralSettings {
  enabled: boolean;
  reward_type: 'fixed' | 'percentage';
  reward_amount: number;
  min_booking_amount: number;
  expiration_days: number;
  max_referrals_per_client: number;
  max_rewards_per_month: number;
}

/**
 * Salon referral settings page
 * Validates: REQ-7, REQ-12, REQ-13
 */
export default function SalonSettingsPage() {
  const [settings, setSettings] = useState<ReferralSettings>({
    enabled: true,
    reward_type: 'fixed',
    reward_amount: 1000,
    min_booking_amount: 5000,
    expiration_days: 90,
    max_referrals_per_client: 50,
    max_rewards_per_month: 100000,
  });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Fetch current settings
  const { data: currentSettings, isLoading } = useQuery({
    queryKey: ['referral-settings'],
    queryFn: async () => {
      const response = await apiClient.get('/api/tenants/referral-settings');
      return response.data;
    },
  });

  // Update settings mutation
  const updateMutation = useMutation({
    mutationFn: async (newSettings: ReferralSettings) => {
      const response = await apiClient.put(
        '/api/tenants/referral-settings',
        newSettings
      );
      return response.data;
    },
    onSuccess: () => {
      setSuccess(true);
      setError('');
      setTimeout(() => setSuccess(false), 3000);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update settings');
      setSuccess(false);
    },
  });

  // Load current settings
  useEffect(() => {
    if (currentSettings) {
      setSettings(currentSettings);
    }
  }, [currentSettings]);

  const handleChange = (field: keyof ReferralSettings, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate settings
    if (settings.reward_amount <= 0) {
      setError('Reward amount must be greater than 0');
      return;
    }
    
    if (settings.min_booking_amount < 0) {
      setError('Minimum booking amount cannot be negative');
      return;
    }
    
    if (settings.expiration_days <= 0) {
      setError('Expiration days must be greater than 0');
      return;
    }
    
    if (settings.max_referrals_per_client <= 0) {
      setError('Max referrals per client must be greater than 0');
      return;
    }
    
    if (settings.max_rewards_per_month <= 0) {
      setError('Max rewards per month must be greater than 0');
      return;
    }

    updateMutation.mutate(settings);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Referral Program Settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure your salon's referral program
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <Alert className="bg-green-500/10 border-green-500/20">
          <CheckCircleIcon className="h-4 w-4 text-green-500" />
          <AlertDescription className="text-green-700">
            Settings updated successfully!
          </AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {error && (
        <Alert className="bg-red-500/10 border-red-500/20">
          <AlertCircleIcon className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      {/* Settings Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Enable/Disable Program */}
        <Card>
          <CardHeader>
            <CardTitle>Program Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="enabled" className="text-base font-medium">
                  Enable Referral Program
                </Label>
                <p className="text-sm text-muted-foreground mt-1">
                  Turn the referral program on or off for your salon
                </p>
              </div>
              <Switch
                id="enabled"
                checked={settings.enabled}
                onCheckedChange={(checked) =>
                  handleChange('enabled', checked)
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Reward Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Reward Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Reward Type */}
            <div>
              <Label htmlFor="reward_type">Reward Type</Label>
              <Select
                value={settings.reward_type}
                onValueChange={(value) =>
                  handleChange('reward_type', value as 'fixed' | 'percentage')
                }
              >
                <SelectTrigger id="reward_type" className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fixed">Fixed Amount (₦)</SelectItem>
                  <SelectItem value="percentage">Percentage (%)</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                Choose whether rewards are a fixed amount or percentage of booking value
              </p>
            </div>

            {/* Reward Amount */}
            <div>
              <Label htmlFor="reward_amount">
                Reward Amount {settings.reward_type === 'percentage' ? '(%)' : '(₦)'}
              </Label>
              <Input
                id="reward_amount"
                type="number"
                value={settings.reward_amount}
                onChange={(e) =>
                  handleChange('reward_amount', parseFloat(e.target.value))
                }
                min="0"
                step={settings.reward_type === 'percentage' ? '0.1' : '100'}
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Amount earned per successful referral
              </p>
            </div>

            {/* Minimum Booking Amount */}
            <div>
              <Label htmlFor="min_booking_amount">
                Minimum Booking Amount (₦)
              </Label>
              <Input
                id="min_booking_amount"
                type="number"
                value={settings.min_booking_amount}
                onChange={(e) =>
                  handleChange('min_booking_amount', parseFloat(e.target.value))
                }
                min="0"
                step="100"
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Minimum booking value required to earn referral reward
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Expiration & Limits */}
        <Card>
          <CardHeader>
            <CardTitle>Expiration & Limits</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Expiration Days */}
            <div>
              <Label htmlFor="expiration_days">Referral Expiration (Days)</Label>
              <Input
                id="expiration_days"
                type="number"
                value={settings.expiration_days}
                onChange={(e) =>
                  handleChange('expiration_days', parseInt(e.target.value))
                }
                min="1"
                step="1"
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Days before pending referral expires
              </p>
            </div>

            {/* Max Referrals Per Client */}
            <div>
              <Label htmlFor="max_referrals_per_client">
                Max Referrals Per Client
              </Label>
              <Input
                id="max_referrals_per_client"
                type="number"
                value={settings.max_referrals_per_client}
                onChange={(e) =>
                  handleChange('max_referrals_per_client', parseInt(e.target.value))
                }
                min="1"
                step="1"
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum number of referrals per client
              </p>
            </div>

            {/* Max Rewards Per Month */}
            <div>
              <Label htmlFor="max_rewards_per_month">
                Max Rewards Per Month (₦)
              </Label>
              <Input
                id="max_rewards_per_month"
                type="number"
                value={settings.max_rewards_per_month}
                onChange={(e) =>
                  handleChange('max_rewards_per_month', parseFloat(e.target.value))
                }
                min="0"
                step="1000"
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Maximum total rewards paid out per month
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            type="submit"
            disabled={updateMutation.isPending}
            className="flex-1"
          >
            {updateMutation.isPending ? (
              <>
                <Spinner className="mr-2 h-4 w-4" />
                Saving...
              </>
            ) : (
              'Save Settings'
            )}
          </Button>
        </div>
      </form>

      {/* Info Box */}
      <Card className="bg-blue-500/5 border-blue-500/20">
        <CardContent className="pt-6">
          <h3 className="font-semibold mb-2">Referral Program Tips</h3>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• Set competitive rewards to encourage referrals</li>
            <li>• Consider minimum booking amounts to ensure profitability</li>
            <li>• Set reasonable expiration periods (30-90 days recommended)</li>
            <li>• Monitor monthly rewards to control program costs</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
