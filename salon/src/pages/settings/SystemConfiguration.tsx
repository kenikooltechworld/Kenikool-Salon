import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface SystemConfig {
  middlewareSettings: {
    auditLoggingEnabled: boolean;
    rateLimitingEnabled: boolean;
    ddosProtectionEnabled: boolean;
    wafEnabled: boolean;
    intrusionDetectionEnabled: boolean;
    enumerationPreventionEnabled: boolean;
  };
  securitySettings: {
    sastEnabled: boolean;
    dependencyCheckEnabled: boolean;
    pentestFrameworkEnabled: boolean;
  };
  featureFlags: Record<string, boolean>;
}

export function SystemConfiguration() {
  const [config, setConfig] = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch("/api/settings/system-config");
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      setMessage({
        type: "error",
        text: "Failed to load system configuration",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    try {
      await fetch("/api/settings/system-config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      setMessage({ type: "success", text: "Configuration saved successfully" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to save configuration" });
    } finally {
      setSaving(false);
    }
  };

  if (loading)
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="animate-spin" />
      </div>
    );
  if (!config) return <div>Failed to load configuration</div>;

  return (
    <div className="space-y-6">
      {message && (
        <div
          className={`flex items-center gap-2 p-4 rounded-lg ${message.type === "success" ? "bg-green-50 text-green-900" : "bg-red-50 text-red-900"}`}
        >
          {message.type === "success" ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          {message.text}
        </div>
      )}

      <Tabs defaultValue="middleware" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="middleware">Middleware</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="features">Features</TabsTrigger>
        </TabsList>

        <TabsContent value="middleware" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Middleware Configuration</CardTitle>
              <CardDescription>
                Control middleware services and protections
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(config.middlewareSettings).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <Label className="capitalize">
                    {key.replace(/([A-Z])/g, " $1").trim()}
                  </Label>
                  <Switch
                    checked={value}
                    onCheckedChange={(checked) =>
                      setConfig({
                        ...config,
                        middlewareSettings: {
                          ...config.middlewareSettings,
                          [key]: checked,
                        },
                      })
                    }
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Configuration</CardTitle>
              <CardDescription>
                Manage security scanning and testing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(config.securitySettings).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <Label className="capitalize">
                    {key.replace(/([A-Z])/g, " $1").trim()}
                  </Label>
                  <Switch
                    checked={value}
                    onCheckedChange={(checked) =>
                      setConfig({
                        ...config,
                        securitySettings: {
                          ...config.securitySettings,
                          [key]: checked,
                        },
                      })
                    }
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="features" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Feature Flags</CardTitle>
              <CardDescription>Enable or disable features</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(config.featureFlags).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <Label className="capitalize">
                    {key.replace(/([A-Z])/g, " $1").trim()}
                  </Label>
                  <Switch
                    checked={value}
                    onCheckedChange={(checked) =>
                      setConfig({
                        ...config,
                        featureFlags: {
                          ...config.featureFlags,
                          [key]: checked,
                        },
                      })
                    }
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Button onClick={handleSave} disabled={saving} className="w-full">
        {saving ? <Loader2 className="animate-spin mr-2 w-4 h-4" /> : null}
        Save Configuration
      </Button>
    </div>
  );
}
