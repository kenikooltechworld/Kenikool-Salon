"use client";

import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Loader2Icon,
  PlusIcon,
  Edit2Icon,
  TrashIcon,
  BellIcon,
  CheckCircle2Icon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useToast } from "@/hooks/use-toast";

interface NotificationRule {
  id: string;
  name: string;
  trigger: string;
  channels: string[];
  message_template: string;
  enabled: boolean;
  conditions: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface NotificationHistory {
  id: string;
  client_id: string;
  channels: string[];
  message: string;
  notification_type: string;
  status: string;
  delivery_status: Record<string, any>;
  sent_at?: string;
  created_at: string;
}

interface NotificationSettingsPageProps {
  tenantId: string;
}

const TRIGGERS = [
  { value: "booking_created", label: "Booking Created" },
  { value: "booking_completed", label: "Booking Completed" },
  { value: "booking_cancelled", label: "Booking Cancelled" },
  { value: "payment_received", label: "Payment Received" },
  { value: "review_submitted", label: "Review Submitted" },
  { value: "birthday", label: "Birthday" },
  { value: "anniversary", label: "Anniversary" },
  { value: "inactive_client", label: "Inactive Client" },
];

const CHANNELS = [
  { value: "sms", label: "SMS" },
  { value: "email", label: "Email" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "push", label: "Push Notification" },
];

export function NotificationSettingsPage({
  tenantId,
}: NotificationSettingsPageProps) {
  const { toast } = useToast();
  const [showRuleDialog, setShowRuleDialog] = useState(false);
  const [editingRule, setEditingRule] = useState<NotificationRule | null>(null);
  const [activeTab, setActiveTab] = useState<"rules" | "history">("rules");

  // Fetch rules
  const {
    data: rulesData,
    refetch: refetchRules,
    isLoading: rulesLoading,
    error: rulesError,
  } = useQuery({
    queryKey: ["notification-rules", tenantId],
    queryFn: async () => {
      try {
        const response = await fetch("/api/notifications/rules", {
          headers: { "X-Tenant-ID": tenantId },
        });
        if (!response.ok) throw new Error("Failed to fetch rules");
        return response.json();
      } catch (error) {
        console.error("Error fetching rules:", error);
        return { rules: [] };
      }
    },
  });

  // Fetch history
  const { data: historyData, error: historyError } = useQuery({
    queryKey: ["notification-history", tenantId],
    queryFn: async () => {
      try {
        const response = await fetch("/api/notifications/history", {
          headers: { "X-Tenant-ID": tenantId },
        });
        if (!response.ok) throw new Error("Failed to fetch history");
        return response.json();
      } catch (error) {
        console.error("Error fetching history:", error);
        return { notifications: [] };
      }
    },
  });

  // Delete rule mutation
  const deleteRuleMutation = useMutation({
    mutationFn: async (ruleId: string) => {
      const response = await fetch(`/api/notifications/rules/${ruleId}`, {
        method: "DELETE",
        headers: { "X-Tenant-ID": tenantId },
      });
      if (!response.ok) throw new Error("Failed to delete rule");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Notification rule deleted",
      });
      refetchRules();
    },
    onError: (error) => {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete rule",
        variant: "destructive",
      });
    },
  });

  const rules = rulesData?.rules || [];
  const history = historyData?.notifications || [];

  // Show error state if queries failed
  if (rulesError || historyError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Notification Settings</h1>
          <p className="text-gray-600 mt-2">
            Configure automated notifications and view delivery history
          </p>
        </div>
        <Alert variant="destructive">
          <AlertTriangleIcon className="h-4 w-4" />
          <AlertDescription>
            Failed to load notification settings. Please try again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Notification Settings</h1>
        <p className="text-gray-600 mt-2">
          Configure automated notifications and view delivery history
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setActiveTab("rules")}
          className={`px-4 py-2 font-medium border-b-2 ${
            activeTab === "rules"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-600"
          }`}
        >
          Notification Rules
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-4 py-2 font-medium border-b-2 ${
            activeTab === "history"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-600"
          }`}
        >
          Delivery History
        </button>
      </div>

      {/* Rules Tab */}
      {activeTab === "rules" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Button onClick={() => setShowRuleDialog(true)}>
              <PlusIcon className="mr-2 h-4 w-4" />
              Create Rule
            </Button>
          </div>

          {rules.length === 0 ? (
            <Alert>
              <BellIcon className="h-4 w-4" />
              <AlertDescription>
                No notification rules configured. Create one to get started.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              {rules.map((rule) => (
                <Card key={rule.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{rule.name}</CardTitle>
                        <CardDescription>
                          Trigger:{" "}
                          {
                            TRIGGERS.find((t) => t.value === rule.trigger)
                              ?.label
                          }
                        </CardDescription>
                      </div>
                      <Badge variant={rule.enabled ? "default" : "secondary"}>
                        {rule.enabled ? "Enabled" : "Disabled"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">Channels</p>
                      <div className="flex gap-2">
                        {rule.channels.map((channel) => (
                          <Badge key={channel} variant="outline">
                            {CHANNELS.find((c) => c.value === channel)?.label}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">
                        Message Template
                      </p>
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                        {rule.message_template}
                      </p>
                    </div>
                    <div className="flex gap-2 justify-end">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingRule(rule);
                          setShowRuleDialog(true);
                        }}
                      >
                        <Edit2Icon className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteRuleMutation.mutate(rule.id)}
                        disabled={deleteRuleMutation.isPending}
                      >
                        <TrashIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === "history" && (
        <div className="space-y-4">
          {history.length === 0 ? (
            <Alert>
              <CheckCircle2Icon className="h-4 w-4" />
              <AlertDescription>No notifications sent yet.</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              {history.map((notification) => (
                <Card key={notification.id}>
                  <CardContent className="pt-6">
                    <div className="grid grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Type</p>
                        <p className="font-semibold capitalize">
                          {notification.notification_type.replace("_", " ")}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Channels</p>
                        <div className="flex gap-1 flex-wrap">
                          {notification.channels.map((channel) => (
                            <Badge
                              key={channel}
                              variant="outline"
                              className="text-xs"
                            >
                              {channel}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Status</p>
                        <Badge
                          variant={
                            notification.status === "sent"
                              ? "default"
                              : "secondary"
                          }
                        >
                          {notification.status}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Sent</p>
                        <p className="font-semibold">
                          {notification.sent_at
                            ? new Date(
                                notification.sent_at,
                              ).toLocaleDateString()
                            : "N/A"}
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-600">Message</p>
                      <p className="text-sm mt-1">{notification.message}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Rule Dialog */}
      <RuleDialog
        open={showRuleDialog}
        onOpenChange={setShowRuleDialog}
        rule={editingRule}
        tenantId={tenantId}
        onSuccess={() => {
          setEditingRule(null);
          setShowRuleDialog(false);
          refetchRules();
        }}
      />
    </div>
  );
}

interface RuleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  rule: NotificationRule | null;
  tenantId: string;
  onSuccess: () => void;
}

function RuleDialog({
  open,
  onOpenChange,
  rule,
  tenantId,
  onSuccess,
}: RuleDialogProps) {
  const { toast } = useToast();
  const [name, setName] = useState(rule?.name || "");
  const [trigger, setTrigger] = useState(rule?.trigger || "");
  const [channels, setChannels] = useState<string[]>(rule?.channels || []);
  const [messageTemplate, setMessageTemplate] = useState(
    rule?.message_template || "",
  );
  const [enabled, setEnabled] = useState(rule?.enabled ?? true);
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = async () => {
    if (!name || !trigger || channels.length === 0 || !messageTemplate) {
      toast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const url = rule
        ? `/api/notifications/rules/${rule.id}`
        : "/api/notifications/rules";
      const method = rule ? "PATCH" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": tenantId,
        },
        body: JSON.stringify({
          name,
          trigger,
          channels,
          message_template: messageTemplate,
          enabled,
        }),
      });

      if (!response.ok) throw new Error("Failed to save rule");

      toast({
        title: "Success",
        description: rule ? "Rule updated" : "Rule created",
      });
      onSuccess();
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to save rule",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {rule ? "Edit Rule" : "Create Notification Rule"}
          </DialogTitle>
          <DialogDescription>
            Configure when and how notifications are sent
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Rule Name *
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Birthday Greeting"
              disabled={isLoading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Trigger Event *
            </label>
            <Select value={trigger} onValueChange={setTrigger}>
              <SelectTrigger>
                <SelectValue placeholder="Select trigger" />
              </SelectTrigger>
              <SelectContent>
                {TRIGGERS.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Channels *</label>
            <div className="space-y-2">
              {CHANNELS.map((channel) => (
                <div key={channel.value} className="flex items-center">
                  <Checkbox
                    checked={channels.includes(channel.value)}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        setChannels([...channels, channel.value]);
                      } else {
                        setChannels(
                          channels.filter((c) => c !== channel.value),
                        );
                      }
                    }}
                    disabled={isLoading}
                  />
                  <label className="ml-2 text-sm">{channel.label}</label>
                </div>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Message Template *
            </label>
            <Textarea
              value={messageTemplate}
              onChange={(e) => setMessageTemplate(e.target.value)}
              placeholder="Enter message template"
              disabled={isLoading}
            />
          </div>
          <div className="flex items-center">
            <Checkbox
              checked={enabled}
              onCheckedChange={setEnabled}
              disabled={isLoading}
            />
            <label className="ml-2 text-sm">Enable this rule</label>
          </div>
          <div className="flex gap-4 justify-end">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              {isLoading && (
                <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
              )}
              {rule ? "Update" : "Create"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
