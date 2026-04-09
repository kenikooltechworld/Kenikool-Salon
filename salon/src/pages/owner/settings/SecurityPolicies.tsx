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
} from "@/components/icons";

interface SecurityPolicy {
  rateLimiting: {
    requestsPerMinute: number;
    requestsPerHour: number;
    burstLimit: number;
  };
  ddosProtection: {
    threshold: number;
    blockDuration: number;
    enabled: boolean;
  };
  wafRules: {
    sqlInjectionProtection: boolean;
    xssProtection: boolean;
    csrfProtection: boolean;
    customRules: string[];
  };
  paymentRetry: {
    maxRetries: number;
    retryDelaySeconds: number;
    backoffMultiplier: number;
  };
}

export function SecurityPolicies() {
  const [policy, setPolicy] = useState<SecurityPolicy | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPolicy();
  }, []);

  const fetchPolicy = async () => {
    try {
      const response = await fetch("/api/v1/settings/security-policies");
      const data = await response.json();
      setPolicy(data);
    } catch (error) {
      setMessage({ type: "error", text: "Failed to load security policies" });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!policy) return;
    setSaving(true);
    try {
      await fetch("/api/v1/settings/security-policies", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(policy),
      });
      setMessage({ type: "success", text: "Security policies saved" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to save policies" });
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
  if (!policy) return <div>Failed to load policies</div>;

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

      <Tabs defaultValue="rate-limiting" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="rate-limiting">Rate Limiting</TabsTrigger>
          <TabsTrigger value="ddos">DDoS</TabsTrigger>
          <TabsTrigger value="waf">WAF</TabsTrigger>
          <TabsTrigger value="payment">Payment</TabsTrigger>
        </TabsList>

        <TabsContent value="rate-limiting" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Rate Limiting</CardTitle>
              <CardDescription>Control request rate limits</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Requests per Minute</Label>
                <Input
                  type="number"
                  value={policy.rateLimiting.requestsPerMinute}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      rateLimiting: {
                        ...policy.rateLimiting,
                        requestsPerMinute: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Requests per Hour</Label>
                <Input
                  type="number"
                  value={policy.rateLimiting.requestsPerHour}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      rateLimiting: {
                        ...policy.rateLimiting,
                        requestsPerHour: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Burst Limit</Label>
                <Input
                  type="number"
                  value={policy.rateLimiting.burstLimit}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      rateLimiting: {
                        ...policy.rateLimiting,
                        burstLimit: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ddos" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>DDoS Protection</CardTitle>
              <CardDescription>
                Configure DDoS detection and mitigation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Detection Threshold</Label>
                <Input
                  type="number"
                  value={policy.ddosProtection.threshold}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      ddosProtection: {
                        ...policy.ddosProtection,
                        threshold: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Block Duration (seconds)</Label>
                <Input
                  type="number"
                  value={policy.ddosProtection.blockDuration}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      ddosProtection: {
                        ...policy.ddosProtection,
                        blockDuration: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="waf" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Web Application Firewall</CardTitle>
              <CardDescription>Configure WAF rules</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>SQL Injection Protection</Label>
                <input
                  type="checkbox"
                  checked={policy.wafRules.sqlInjectionProtection}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      wafRules: {
                        ...policy.wafRules,
                        sqlInjectionProtection: e.target.checked,
                      },
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label>XSS Protection</Label>
                <input
                  type="checkbox"
                  checked={policy.wafRules.xssProtection}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      wafRules: {
                        ...policy.wafRules,
                        xssProtection: e.target.checked,
                      },
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label>CSRF Protection</Label>
                <input
                  type="checkbox"
                  checked={policy.wafRules.csrfProtection}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      wafRules: {
                        ...policy.wafRules,
                        csrfProtection: e.target.checked,
                      },
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="payment" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Payment Retry Policy</CardTitle>
              <CardDescription>
                Configure payment retry behavior
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Max Retries</Label>
                <Input
                  type="number"
                  value={policy.paymentRetry.maxRetries}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      paymentRetry: {
                        ...policy.paymentRetry,
                        maxRetries: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Retry Delay (seconds)</Label>
                <Input
                  type="number"
                  value={policy.paymentRetry.retryDelaySeconds}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      paymentRetry: {
                        ...policy.paymentRetry,
                        retryDelaySeconds: parseInt(e.target.value),
                      },
                    })
                  }
                />
              </div>
              <div>
                <Label>Backoff Multiplier</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={policy.paymentRetry.backoffMultiplier}
                  onChange={(e) =>
                    setPolicy({
                      ...policy,
                      paymentRetry: {
                        ...policy.paymentRetry,
                        backoffMultiplier: parseFloat(e.target.value),
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
        Save Policies
      </Button>
    </div>
  );
}
