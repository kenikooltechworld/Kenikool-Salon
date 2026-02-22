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
  PlusIcon,
  Trash2Icon,
} from "@/components/icons";

interface CommissionRule {
  id: string;
  name: string;
  percentage: number;
  minAmount: number;
  maxAmount: number;
  applicableTo: "staff" | "service";
}

interface FinancialSettings {
  commissionRules: CommissionRule[];
  balanceEnforcement: {
    enabled: boolean;
    minimumBalance: number;
  };
  paymentSettings: {
    autoSettlement: boolean;
    settlementDay: number;
  };
}

export function CommissionSettings() {
  const [settings, setSettings] = useState<FinancialSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/settings/commission");
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      setMessage({ type: "error", text: "Failed to load commission settings" });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await fetch("/api/settings/commission", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      setMessage({ type: "success", text: "Commission settings saved" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to save settings" });
    } finally {
      setSaving(false);
    }
  };

  const addRule = () => {
    if (!settings) return;
    const newRule: CommissionRule = {
      id: Date.now().toString(),
      name: "New Rule",
      percentage: 0,
      minAmount: 0,
      maxAmount: 0,
      applicableTo: "staff",
    };
    setSettings({
      ...settings,
      commissionRules: [...settings.commissionRules, newRule],
    });
  };

  const removeRule = (id: string) => {
    if (!settings) return;
    setSettings({
      ...settings,
      commissionRules: settings.commissionRules.filter((r) => r.id !== id),
    });
  };

  const updateRule = (id: string, updates: Partial<CommissionRule>) => {
    if (!settings) return;
    setSettings({
      ...settings,
      commissionRules: settings.commissionRules.map((r) =>
        r.id === id ? { ...r, ...updates } : r,
      ),
    });
  };

  if (loading)
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2Icon className="animate-spin" />
      </div>
    );
  if (!settings) return <div>Failed to load settings</div>;

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

      <Tabs defaultValue="rules" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="rules">Commission Rules</TabsTrigger>
          <TabsTrigger value="financial">Financial Controls</TabsTrigger>
        </TabsList>

        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Commission Rules</CardTitle>
                <CardDescription>Define commission structures</CardDescription>
              </div>
              <Button onClick={addRule} size="sm">
                <PlusIcon className="w-4 h-4 mr-2" />
                Add Rule
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {settings.commissionRules.map((rule) => (
                <div key={rule.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex-1 space-y-3">
                      <div>
                        <Label>Rule Name</Label>
                        <Input
                          value={rule.name}
                          onChange={(e) =>
                            updateRule(rule.id, { name: e.target.value })
                          }
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <Label>Percentage (%)</Label>
                          <Input
                            type="number"
                            step="0.1"
                            value={rule.percentage}
                            onChange={(e) =>
                              updateRule(rule.id, {
                                percentage: parseFloat(e.target.value),
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label>Min Amount</Label>
                          <Input
                            type="number"
                            value={rule.minAmount}
                            onChange={(e) =>
                              updateRule(rule.id, {
                                minAmount: parseFloat(e.target.value),
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label>Max Amount</Label>
                          <Input
                            type="number"
                            value={rule.maxAmount}
                            onChange={(e) =>
                              updateRule(rule.id, {
                                maxAmount: parseFloat(e.target.value),
                              })
                            }
                          />
                        </div>
                      </div>
                      <div>
                        <Label>Applicable To</Label>
                        <select
                          value={rule.applicableTo}
                          onChange={(e) =>
                            updateRule(rule.id, {
                              applicableTo: e.target.value as
                                | "staff"
                                | "service",
                            })
                          }
                          className="w-full border rounded px-3 py-2"
                        >
                          <option value="staff">Staff</option>
                          <option value="service">Service</option>
                        </select>
                      </div>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => removeRule(rule.id)}
                      className="ml-4"
                    >
                      <Trash2Icon className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="financial" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Financial Controls</CardTitle>
              <CardDescription>
                Manage balance enforcement and payment settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="balance-enforcement"
                    checked={settings.balanceEnforcement.enabled}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        balanceEnforcement: {
                          ...settings.balanceEnforcement,
                          enabled: e.target.checked,
                        },
                      })
                    }
                  />
                  <Label htmlFor="balance-enforcement">
                    Enable Balance Enforcement
                  </Label>
                </div>
              </div>
              <div>
                <Label>Minimum Balance Required</Label>
                <Input
                  type="number"
                  value={settings.balanceEnforcement.minimumBalance}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      balanceEnforcement: {
                        ...settings.balanceEnforcement,
                        minimumBalance: parseFloat(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="auto-settlement"
                    checked={settings.paymentSettings.autoSettlement}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        paymentSettings: {
                          ...settings.paymentSettings,
                          autoSettlement: e.target.checked,
                        },
                      })
                    }
                  />
                  <Label htmlFor="auto-settlement">
                    Enable Auto Settlement
                  </Label>
                </div>
              </div>
              <div>
                <Label>Settlement Day (1-31)</Label>
                <Input
                  type="number"
                  min="1"
                  max="31"
                  value={settings.paymentSettings.settlementDay}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      paymentSettings: {
                        ...settings.paymentSettings,
                        settlementDay: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Button onClick={handleSave} disabled={saving} className="w-full">
        {saving ? <Loader2Icon className="animate-spin mr-2 w-4 h-4" /> : null}
        Save Commission Settings
      </Button>
    </div>
  );
}
