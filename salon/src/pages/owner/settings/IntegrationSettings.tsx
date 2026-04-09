import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  Loader2Icon,
  EyeIcon,
  EyeOffIcon,
} from "@/components/icons";

interface IntegrationConfig {
  termii: {
    apiKey: string;
    senderId: string;
    enabled: boolean;
  };
  paystack: {
    publicKey: string;
    secretKey: string;
    webhookUrl: string;
    enabled: boolean;
  };
}

export function IntegrationSettings() {
  const [config, setConfig] = useState<IntegrationConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch("/api/v1/settings/integrations");
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      setMessage({
        type: "error",
        text: "Failed to load integration settings",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    try {
      await fetch("/api/v1/settings/integrations", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      setMessage({ type: "success", text: "Integration settings saved" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to save settings" });
    } finally {
      setSaving(false);
    }
  };

  if (loading)
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2Icon className="animate-spin" />
      </div>
    );
  if (!config) return <div>Failed to load settings</div>;

  const toggleSecret = (key: string) => {
    setShowSecrets({ ...showSecrets, [key]: !showSecrets[key] });
  };

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate("/settings")}
        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        ← Back to Settings
      </button>

      {message && (
        <div
          className={`flex items-center gap-2 p-4 rounded-lg ${message.type === "success" ? "bg-green-50 text-green-900" : "bg-red-50 text-red-900"}`}
        >
          {message.type === "success" ? (
            <CheckCircle2Icon className="w-5 h-5" />
          ) : (
            <AlertCircleIcon className="w-5 h-5" />
          )}
          {message.text}
        </div>
      )}

      <Tabs defaultValue="termii" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="termii">Termii SMS</TabsTrigger>
          <TabsTrigger value="paystack">Paystack Payments</TabsTrigger>
        </TabsList>

        <TabsContent value="termii" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Termii SMS Configuration</CardTitle>
              <CardDescription>
                Configure SMS notifications via Termii
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>API Key</Label>
                <div className="flex gap-2">
                  <Input
                    type={showSecrets["termii-key"] ? "text" : "password"}
                    value={config.termii.apiKey}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        termii: { ...config.termii, apiKey: e.target.value },
                      })
                    }
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => toggleSecret("termii-key")}
                  >
                    {showSecrets["termii-key"] ? (
                      <EyeOffIcon className="w-4 h-4" />
                    ) : (
                      <EyeIcon className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div>
                <Label>Sender ID</Label>
                <Input
                  value={config.termii.senderId}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      termii: { ...config.termii, senderId: e.target.value },
                    })
                  }
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="termii-enabled"
                  checked={config.termii.enabled}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      termii: { ...config.termii, enabled: e.target.checked },
                    })
                  }
                />
                <Label htmlFor="termii-enabled">Enable Termii SMS</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="paystack" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Paystack Payment Configuration</CardTitle>
              <CardDescription>
                Configure payment processing via Paystack
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Public Key</Label>
                <Input
                  value={config.paystack.publicKey}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      paystack: {
                        ...config.paystack,
                        publicKey: e.target.value,
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Secret Key</Label>
                <div className="flex gap-2">
                  <Input
                    type={showSecrets["paystack-secret"] ? "text" : "password"}
                    value={config.paystack.secretKey}
                    onChange={(e) =>
                      setConfig({
                        ...config,
                        paystack: {
                          ...config.paystack,
                          secretKey: e.target.value,
                        },
                      })
                    }
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => toggleSecret("paystack-secret")}
                  >
                    {showSecrets["paystack-secret"] ? (
                      <EyeOffIcon className="w-4 h-4" />
                    ) : (
                      <EyeIcon className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
              <div>
                <Label>Webhook URL</Label>
                <Input
                  value={config.paystack.webhookUrl}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      paystack: {
                        ...config.paystack,
                        webhookUrl: e.target.value,
                      },
                    })
                  }
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="paystack-enabled"
                  checked={config.paystack.enabled}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      paystack: {
                        ...config.paystack,
                        enabled: e.target.checked,
                      },
                    })
                  }
                />
                <Label htmlFor="paystack-enabled">Enable Paystack</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Button onClick={handleSave} disabled={saving} className="w-full">
        {saving ? <Loader2Icon className="animate-spin mr-2 w-4 h-4" /> : null}
        Save Integration Settings
      </Button>
    </div>
  );
}
