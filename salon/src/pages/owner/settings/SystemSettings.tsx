import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CheckIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";

interface SystemConfig {
  rate_limit_enabled: boolean;
  rate_limit_requests: number;
  rate_limit_window: number;
  ddos_protection_enabled: boolean;
  ddos_threshold: number;
  waf_enabled: boolean;
  intrusion_detection_enabled: boolean;
  audit_logging_enabled: boolean;
  feature_flags: Record<string, boolean>;
}

const DEFAULT_CONFIG: SystemConfig = {
  rate_limit_enabled: true,
  rate_limit_requests: 100,
  rate_limit_window: 60,
  ddos_protection_enabled: true,
  ddos_threshold: 1000,
  waf_enabled: true,
  intrusion_detection_enabled: true,
  audit_logging_enabled: true,
  feature_flags: {
    pos_system: true,
    public_booking: true,
    waiting_room: true,
    inventory_tracking: true,
    commission_tracking: true,
  },
};

export default function SystemSettings() {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [config, setConfig] = useState<SystemConfig>(DEFAULT_CONFIG);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch("/api/v1/settings/system", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });

      if (!response.ok) throw new Error("Failed to save system settings");

      addToast({
        title: "Success",
        description: "System settings saved successfully!",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to save settings",
        variant: "error",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <button
          onClick={() => navigate("/settings")}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors mb-4"
        >
          ← Back to Settings
        </button>
        <h2 className="text-2xl font-bold text-foreground">System Settings</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Configure security, performance, and feature flags
        </p>
      </div>

      <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
        {/* Rate Limiting */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">
            Rate Limiting
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Rate Limiting
            </label>
            <input
              type="checkbox"
              checked={config.rate_limit_enabled}
              onChange={(e) =>
                setConfig({
                  ...config,
                  rate_limit_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {config.rate_limit_enabled && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-primary">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Requests per Window
                </label>
                <input
                  type="number"
                  min="10"
                  value={config.rate_limit_requests}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      rate_limit_requests: parseInt(e.target.value) || 100,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Window Duration (seconds)
                </label>
                <input
                  type="number"
                  min="1"
                  value={config.rate_limit_window}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      rate_limit_window: parseInt(e.target.value) || 60,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
          )}
        </div>

        {/* DDoS Protection */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            DDoS Protection
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable DDoS Protection
            </label>
            <input
              type="checkbox"
              checked={config.ddos_protection_enabled}
              onChange={(e) =>
                setConfig({
                  ...config,
                  ddos_protection_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {config.ddos_protection_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Request Threshold per IP
              </label>
              <input
                type="number"
                min="100"
                value={config.ddos_threshold}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    ddos_threshold: parseInt(e.target.value) || 1000,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          )}
        </div>

        {/* Security Features */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Security Features
          </h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-foreground">
                Web Application Firewall (WAF)
              </label>
              <input
                type="checkbox"
                checked={config.waf_enabled}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    waf_enabled: e.target.checked,
                  })
                }
                className="w-4 h-4"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-foreground">
                Intrusion Detection
              </label>
              <input
                type="checkbox"
                checked={config.intrusion_detection_enabled}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    intrusion_detection_enabled: e.target.checked,
                  })
                }
                className="w-4 h-4"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-foreground">
                Audit Logging
              </label>
              <input
                type="checkbox"
                checked={config.audit_logging_enabled}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    audit_logging_enabled: e.target.checked,
                  })
                }
                className="w-4 h-4"
              />
            </div>
          </div>
        </div>

        {/* Feature Flags */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Feature Flags
          </h3>

          <div className="space-y-3">
            {Object.entries(config.feature_flags).map(([flag, enabled]) => (
              <div key={flag} className="flex items-center justify-between">
                <label className="text-sm font-medium text-foreground capitalize">
                  {flag.replace(/_/g, " ")}
                </label>
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      feature_flags: {
                        ...config.feature_flags,
                        [flag]: e.target.checked,
                      },
                    })
                  }
                  className="w-4 h-4"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-border pt-6">
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="gap-2 cursor-pointer"
          >
            <CheckIcon size={18} />
            {isSaving ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </div>
    </div>
  );
}
