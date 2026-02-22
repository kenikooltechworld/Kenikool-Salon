import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { CalendarIcon, UsersIcon, GiftIcon } from "@/components/icons";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api/client";

interface AutomationSettings {
  birthday_campaigns: {
    enabled: boolean;
    discount_percentage: number;
    message_template: string;
    channels: string[];
    send_time: string;
  };
  winback_campaigns: {
    enabled: boolean;
    inactive_days: number;
    discount_percentage: number;
    message_template: string;
    channels: string[];
    frequency_limit_days: number;
  };
  post_visit_campaigns: {
    enabled: boolean;
    delay_days: number;
    message_template: string;
    channels: string[];
  };
  enabled: boolean;
}

export function CampaignAutomation() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<AutomationSettings>({
    birthday_campaigns: {
      enabled: true,
      discount_percentage: 20,
      message_template:
        "Happy Birthday! 🎉 Enjoy {discount}% off your next visit. Book now!",
      channels: ["sms"],
      send_time: "09:00",
    },
    winback_campaigns: {
      enabled: true,
      inactive_days: 90,
      discount_percentage: 15,
      message_template:
        "We miss you! Come back and enjoy {discount}% off your next service.",
      channels: ["sms"],
      frequency_limit_days: 30,
    },
    post_visit_campaigns: {
      enabled: false,
      delay_days: 3,
      message_template: "Thank you for your visit! We hope you loved it.",
      channels: ["sms"],
    },
    enabled: true,
  });

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get("/api/campaign-automation/settings");
      if (response.data) {
        setSettings(response.data);
      }
    } catch (error) {
      console.error("Failed to load automation settings:", error);
      toast({
        title: "Error",
        description: "Failed to load automation settings",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiClient.put("/api/campaign-automation/settings", settings);
      toast({
        title: "Success",
        description: "Automation settings saved successfully",
      });
    } catch (error) {
      console.error("Failed to save automation settings:", error);
      toast({
        title: "Error",
        description: "Failed to save automation settings",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-12 text-center">
        <Spinner size="lg" />
        <p className="text-muted-foreground mt-4">Loading automation settings...</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Birthday Campaigns */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <GiftIcon size={24} className="text-primary" />
              </div>
              <div>
                <CardTitle>Birthday Campaigns</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Automatically send birthday wishes with special offers
                </p>
              </div>
            </div>
            <Switch
              checked={settings.birthday_campaigns.enabled}
              onCheckedChange={(checked) =>
                setSettings({
                  ...settings,
                  birthday_campaigns: {
                    ...settings.birthday_campaigns,
                    enabled: checked,
                  },
                })
              }
            />
          </div>
        </CardHeader>
        {settings.birthday_campaigns.enabled && (
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="birthday-discount">Discount Percentage</Label>
              <Input
                id="birthday-discount"
                type="number"
                min="0"
                max="100"
                value={settings.birthday_campaigns.discount_percentage}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    birthday_campaigns: {
                      ...settings.birthday_campaigns,
                      discount_percentage: parseInt(e.target.value) || 0,
                    },
                  })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="birthday-send-time">Send Time</Label>
              <Input
                id="birthday-send-time"
                type="time"
                value={settings.birthday_campaigns.send_time}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    birthday_campaigns: {
                      ...settings.birthday_campaigns,
                      send_time: e.target.value,
                    },
                  })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="birthday-message">Message Template</Label>
              <Textarea
                id="birthday-message"
                rows={3}
                value={settings.birthday_campaigns.message_template}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    birthday_campaigns: {
                      ...settings.birthday_campaigns,
                      message_template: e.target.value,
                    },
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                Use {"{discount}"} for discount percentage
              </p>
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm font-medium mb-1">How it works:</p>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Checks for client birthdays daily</li>
                <li>• Sends message on their birthday at specified time</li>
                <li>• Includes personalized discount code</li>
              </ul>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Win-Back Campaigns */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <UsersIcon size={24} className="text-primary" />
              </div>
              <div>
                <CardTitle>Win-Back Campaigns</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Re-engage inactive clients with special offers
                </p>
              </div>
            </div>
            <Switch
              checked={settings.winback_campaigns.enabled}
              onCheckedChange={(checked) =>
                setSettings({
                  ...settings,
                  winback_campaigns: {
                    ...settings.winback_campaigns,
                    enabled: checked,
                  },
                })
              }
            />
          </div>
        </CardHeader>
        {settings.winback_campaigns.enabled && (
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="winback-days">Inactive Days Threshold</Label>
              <Input
                id="winback-days"
                type="number"
                min="30"
                max="365"
                value={settings.winback_campaigns.inactive_days}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    winback_campaigns: {
                      ...settings.winback_campaigns,
                      inactive_days: parseInt(e.target.value) || 90,
                    },
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                Target clients who haven't visited in this many days
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="winback-discount">Discount Percentage</Label>
              <Input
                id="winback-discount"
                type="number"
                min="0"
                max="100"
                value={settings.winback_campaigns.discount_percentage}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    winback_campaigns: {
                      ...settings.winback_campaigns,
                      discount_percentage: parseInt(e.target.value) || 0,
                    },
                  })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="winback-frequency">Frequency Limit (Days)</Label>
              <Input
                id="winback-frequency"
                type="number"
                min="1"
                max="365"
                value={settings.winback_campaigns.frequency_limit_days}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    winback_campaigns: {
                      ...settings.winback_campaigns,
                      frequency_limit_days: parseInt(e.target.value) || 30,
                    },
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                Don't send more than once per X days to same client
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="winback-message">Message Template</Label>
              <Textarea
                id="winback-message"
                rows={3}
                value={settings.winback_campaigns.message_template}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    winback_campaigns: {
                      ...settings.winback_campaigns,
                      message_template: e.target.value,
                    },
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                Use {"{discount}"} for discount percentage
              </p>
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm font-medium mb-1">How it works:</p>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Checks for inactive clients daily</li>
                <li>• Sends message to clients past threshold</li>
                <li>• Respects frequency limit to avoid spam</li>
                <li>• Includes personalized discount code</li>
              </ul>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Post-Visit Campaigns */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <CalendarIcon size={24} className="text-primary" />
              </div>
              <div>
                <CardTitle>Post-Visit Campaigns</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Send follow-up messages after client visits
                </p>
              </div>
            </div>
            <Switch
              checked={settings.post_visit_campaigns.enabled}
              onCheckedChange={(checked) =>
                setSettings({
                  ...settings,
                  post_visit_campaigns: {
                    ...settings.post_visit_campaigns,
                    enabled: checked,
                  },
                })
              }
            />
          </div>
        </CardHeader>
        {settings.post_visit_campaigns.enabled && (
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="postvisit-delay">Delay (Days)</Label>
              <Input
                id="postvisit-delay"
                type="number"
                min="0"
                max="30"
                value={settings.post_visit_campaigns.delay_days}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    post_visit_campaigns: {
                      ...settings.post_visit_campaigns,
                      delay_days: parseInt(e.target.value) || 3,
                    },
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                Send message this many days after visit
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="postvisit-message">Message Template</Label>
              <Textarea
                id="postvisit-message"
                rows={3}
                value={settings.post_visit_campaigns.message_template}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    post_visit_campaigns: {
                      ...settings.post_visit_campaigns,
                      message_template: e.target.value,
                    },
                  })
                }
              />
            </div>
            <div className="p-3 bg-muted/50 rounded-lg">
              <p className="text-sm font-medium mb-1">How it works:</p>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Triggered after client completes a visit</li>
                <li>• Sends message after specified delay</li>
                <li>• Great for feedback and follow-up</li>
              </ul>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save Automation Settings"}
        </Button>
      </div>

      {/* Info Card */}
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <CalendarIcon size={20} className="text-primary mt-1" />
            <div>
              <p className="font-medium text-foreground mb-1">
                Automated Campaign Schedule
              </p>
              <p className="text-sm text-muted-foreground">
                Automated campaigns run daily. Birthday campaigns send on the
                client's birthday, win-back campaigns target inactive clients,
                and post-visit campaigns send after visits. All campaigns
                respect client communication preferences.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
