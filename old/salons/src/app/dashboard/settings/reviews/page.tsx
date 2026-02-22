'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, CheckCircle, Mail, MessageSquare } from 'lucide-react';

interface ReviewSettings {
  reminder_enabled: boolean;
  reminder_delay_hours: number;
  incentive_enabled: boolean;
  incentive_points: number;
  notification_enabled: boolean;
  notification_digest: boolean;
  reminder_email_template: string;
  reminder_sms_template: string;
}

export default function ReviewSettingsPage() {
  const [settings, setSettings] = useState<ReviewSettings>({
    reminder_enabled: true,
    reminder_delay_hours: 24,
    incentive_enabled: false,
    incentive_points: 50,
    notification_enabled: true,
    notification_digest: false,
    reminder_email_template: '',
    reminder_sms_template: ''
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [testingEmail, setTestingEmail] = useState(false);
  const [testingSMS, setTestingSMS] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/review-settings');
      
      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }

      const data = await response.json();
      setSettings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(false);

      const response = await fetch('/api/review-settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestEmail = async () => {
    try {
      setTestingEmail(true);
      const response = await fetch('/api/review-settings/test-email', {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to send test email');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send test email');
    } finally {
      setTestingEmail(false);
    }
  };

  const handleTestSMS = async () => {
    try {
      setTestingSMS(true);
      const response = await fetch('/api/review-settings/test-sms', {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to send test SMS');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send test SMS');
    } finally {
      setTestingSMS(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Review Settings</h1>
          <p className="text-gray-600 mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Review Settings</h1>
        <p className="text-gray-600 mt-2">
          Configure review reminders, incentives, and notifications
        </p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {success && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-green-700">Settings saved successfully</p>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="reminders" className="space-y-4">
        <TabsList>
          <TabsTrigger value="reminders">Reminders</TabsTrigger>
          <TabsTrigger value="incentives">Incentives</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        {/* Reminders Tab */}
        <TabsContent value="reminders" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Review Reminders</CardTitle>
              <CardDescription>
                Automatically send reminders to clients after their booking
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Enable/Disable */}
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base font-semibold">Enable Review Reminders</Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Send automatic reminders to clients to leave reviews
                  </p>
                </div>
                <Switch
                  checked={settings.reminder_enabled}
                  onCheckedChange={(checked) =>
                    setSettings(prev => ({ ...prev, reminder_enabled: checked }))
                  }
                />
              </div>

              {settings.reminder_enabled && (
                <>
                  {/* Delay */}
                  <div className="space-y-2">
                    <Label htmlFor="delay">
                      Reminder Delay (hours): {settings.reminder_delay_hours}
                    </Label>
                    <input
                      id="delay"
                      type="range"
                      min="1"
                      max="168"
                      value={settings.reminder_delay_hours}
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          reminder_delay_hours: parseInt(e.target.value)
                        }))
                      }
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500">
                      Reminders will be sent {settings.reminder_delay_hours} hours after booking completion
                    </p>
                  </div>

                  {/* Email Template */}
                  <div className="space-y-2">
                    <Label htmlFor="email-template" className="flex items-center gap-2">
                      <Mail size={16} />
                      Email Template
                    </Label>
                    <Textarea
                      id="email-template"
                      placeholder="Enter email template..."
                      value={settings.reminder_email_template}
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          reminder_email_template: e.target.value
                        }))
                      }
                      className="min-h-[120px]"
                    />
                    <p className="text-xs text-gray-500">
                      Use {'{client_name}'}, {'{review_link}'}, {'{salon_name}'} as placeholders
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleTestEmail}
                      disabled={testingEmail}
                    >
                      {testingEmail ? 'Sending...' : 'Send Test Email'}
                    </Button>
                  </div>

                  {/* SMS Template */}
                  <div className="space-y-2">
                    <Label htmlFor="sms-template" className="flex items-center gap-2">
                      <MessageSquare size={16} />
                      SMS Template
                    </Label>
                    <Textarea
                      id="sms-template"
                      placeholder="Enter SMS template..."
                      value={settings.reminder_sms_template}
                      onChange={(e) =>
                        setSettings(prev => ({
                          ...prev,
                          reminder_sms_template: e.target.value
                        }))
                      }
                      className="min-h-[80px]"
                      maxLength={160}
                    />
                    <p className="text-xs text-gray-500">
                      {settings.reminder_sms_template.length}/160 characters
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleTestSMS}
                      disabled={testingSMS}
                    >
                      {testingSMS ? 'Sending...' : 'Send Test SMS'}
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Incentives Tab */}
        <TabsContent value="incentives" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Review Incentives</CardTitle>
              <CardDescription>
                Reward clients for leaving reviews with loyalty points
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Enable/Disable */}
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base font-semibold">Enable Review Incentives</Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Award loyalty points when clients leave reviews
                  </p>
                </div>
                <Switch
                  checked={settings.incentive_enabled}
                  onCheckedChange={(checked) =>
                    setSettings(prev => ({ ...prev, incentive_enabled: checked }))
                  }
                />
              </div>

              {settings.incentive_enabled && (
                <div className="space-y-2">
                  <Label htmlFor="points">Points per Review</Label>
                  <Input
                    id="points"
                    type="number"
                    min="1"
                    max="1000"
                    value={settings.incentive_points}
                    onChange={(e) =>
                      setSettings(prev => ({
                        ...prev,
                        incentive_points: parseInt(e.target.value) || 0
                      }))
                    }
                  />
                  <p className="text-xs text-gray-500">
                    Clients will earn {settings.incentive_points} points for each review
                  </p>
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Incentives only apply to first review per booking. Clients can only earn points once per booking.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>
                Configure how you receive notifications about new reviews
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Enable/Disable */}
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-base font-semibold">Enable Notifications</Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Receive notifications when new reviews are submitted
                  </p>
                </div>
                <Switch
                  checked={settings.notification_enabled}
                  onCheckedChange={(checked) =>
                    setSettings(prev => ({ ...prev, notification_enabled: checked }))
                  }
                />
              </div>

              {settings.notification_enabled && (
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-base font-semibold">Digest Mode</Label>
                    <p className="text-sm text-gray-600 mt-1">
                      Receive batched notifications instead of individual alerts
                    </p>
                  </div>
                  <Switch
                    checked={settings.notification_digest}
                    onCheckedChange={(checked) =>
                      setSettings(prev => ({ ...prev, notification_digest: checked }))
                    }
                  />
                </div>
              )}

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>Digest Mode:</strong> When enabled, you'll receive one email every 6 hours with all new reviews instead of individual notifications.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      <div className="flex justify-end gap-2">
        <Button
          variant="outline"
          onClick={fetchSettings}
          disabled={saving}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
}
