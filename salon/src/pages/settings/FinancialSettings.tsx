import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CheckIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";

interface FinancialConfig {
  balance_enforcement_enabled: boolean;
  minimum_balance_threshold: number;
  refund_policy_enabled: boolean;
  refund_window_days: number;
  commission_tracking_enabled: boolean;
  staff_commission_percentage: number;
  service_commission_percentage: number;
  invoice_numbering_prefix: string;
  invoice_numbering_start: number;
}

const DEFAULT_CONFIG: FinancialConfig = {
  balance_enforcement_enabled: true,
  minimum_balance_threshold: 0,
  refund_policy_enabled: true,
  refund_window_days: 30,
  commission_tracking_enabled: true,
  staff_commission_percentage: 10,
  service_commission_percentage: 5,
  invoice_numbering_prefix: "INV",
  invoice_numbering_start: 1000,
};

export default function FinancialSettings() {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [config, setConfig] = useState<FinancialConfig>(DEFAULT_CONFIG);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch("/api/settings/financial", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });

      if (!response.ok) throw new Error("Failed to save financial settings");

      addToast({
        title: "Success",
        description: "Financial settings saved successfully!",
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
        <h2 className="text-2xl font-bold text-foreground">
          Financial Settings
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Configure financial policies and commission rules
        </p>
      </div>

      <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
        {/* Balance Enforcement */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">
            Balance Enforcement
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Balance Enforcement
            </label>
            <input
              type="checkbox"
              checked={config.balance_enforcement_enabled}
              onChange={(e) =>
                setConfig({
                  ...config,
                  balance_enforcement_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {config.balance_enforcement_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Minimum Balance Threshold
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={config.minimum_balance_threshold}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    minimum_balance_threshold: parseFloat(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Customers cannot make transactions below this balance
              </p>
            </div>
          )}
        </div>

        {/* Refund Policy */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Refund Policy
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Refund Policy
            </label>
            <input
              type="checkbox"
              checked={config.refund_policy_enabled}
              onChange={(e) =>
                setConfig({
                  ...config,
                  refund_policy_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {config.refund_policy_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Refund Window (days)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={config.refund_window_days}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    refund_window_days: parseInt(e.target.value) || 30,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Number of days after transaction when refunds are allowed
              </p>
            </div>
          )}
        </div>

        {/* Commission Configuration */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Commission Configuration
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Commission Tracking
            </label>
            <input
              type="checkbox"
              checked={config.commission_tracking_enabled}
              onChange={(e) =>
                setConfig({
                  ...config,
                  commission_tracking_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {config.commission_tracking_enabled && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-4 border-l-2 border-primary">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Staff Commission (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={config.staff_commission_percentage}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      staff_commission_percentage:
                        parseFloat(e.target.value) || 0,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Service Commission (%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={config.service_commission_percentage}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      service_commission_percentage:
                        parseFloat(e.target.value) || 0,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
          )}
        </div>

        {/* Invoice Configuration */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Invoice Configuration
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Invoice Number Prefix
              </label>
              <input
                type="text"
                value={config.invoice_numbering_prefix}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    invoice_numbering_prefix: e.target.value,
                  })
                }
                placeholder="e.g., INV"
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Starting Invoice Number
              </label>
              <input
                type="number"
                min="1"
                value={config.invoice_numbering_start}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    invoice_numbering_start: parseInt(e.target.value) || 1000,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <p className="text-xs text-blue-900 dark:text-blue-100">
              Example invoice number:{" "}
              <span className="font-semibold">
                {config.invoice_numbering_prefix}-
                {config.invoice_numbering_start}
              </span>
            </p>
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
