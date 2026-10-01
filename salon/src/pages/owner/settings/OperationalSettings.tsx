import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CheckIcon, ArrowLeftIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { Skeleton } from "@/components/ui/skeleton";
import { useOperationalSettings, useUpdateOperationalSettings } from "@/hooks/useOperationalSettings";
import type { OperationalConfig } from "@/hooks/useOperationalSettings";

export function OperationalSettings() {
  const navigate = useNavigate();
  const { data: config, isLoading, refetch } = useOperationalSettings();
  const { mutate: updateSettings, isPending } = useUpdateOperationalSettings();
  const { addToast } = useToast();
  const [localConfig, setLocalConfig] = useState<OperationalConfig>({
    inventory_tracking_enabled: true,
    low_stock_threshold: 10,
    waiting_room_enabled: true,
    waiting_room_max_capacity: 50,
    resource_management_enabled: true,
    notification_preferences_enabled: true,
    sms_provider: "termii",
    email_provider: "smtp",
    backup_enabled: true,
    backup_frequency: "daily",
    cache_optimization_enabled: true,
    cache_ttl_minutes: 60,
  });

  useState(() => {
    if (config) setLocalConfig(config);
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="space-y-2">
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-5 w-72" />
        </div>
        <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-10 w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/settings")}
            className="gap-2 cursor-pointer"
          >
            <ArrowLeftIcon size={18} />
            Back
          </Button>
        </div>
        <div className="bg-red-50 text-red-900 border border-red-200 rounded-lg p-4">
          Failed to load operational settings.
        </div>
      </div>
    );
  }

  const handleSave = () => {
    updateSettings(localConfig, {
      onSuccess: () => {
        addToast({
          title: "Success",
          description: "Operational settings saved successfully!",
          variant: "success",
        });
      },
      onError: (error) => {
        addToast({
          title: "Error",
          description:
            error instanceof Error ? error.message : "Failed to save settings",
          variant: "error",
        });
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/settings")}
          className="gap-2 cursor-pointer"
        >
          <ArrowLeftIcon size={18} />
          Back
        </Button>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-foreground">
            Operational Settings
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Configure inventory, waiting room, and system preferences
          </p>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
        {/* Inventory & Resources */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-foreground">
            Inventory & Resources
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Inventory Tracking
            </label>
            <input
              type="checkbox"
              checked={localConfig.inventory_tracking_enabled}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  inventory_tracking_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {localConfig.inventory_tracking_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Low Stock Threshold
              </label>
              <input
                type="number"
                min="0"
                value={localConfig.low_stock_threshold}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    low_stock_threshold: parseInt(e.target.value) || 0,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Alert when stock falls below this quantity
              </p>
            </div>
          )}

          <div className="flex items-center justify-between border-t border-border pt-4">
            <label className="text-sm font-medium text-foreground">
              Enable Resource Management
            </label>
            <input
              type="checkbox"
              checked={localConfig.resource_management_enabled}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  resource_management_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>
        </div>

        {/* Waiting Room */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Waiting Room
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Waiting Room
            </label>
            <input
              type="checkbox"
              checked={localConfig.waiting_room_enabled}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  waiting_room_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {localConfig.waiting_room_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Maximum Queue Capacity
              </label>
              <input
                type="number"
                min="1"
                value={localConfig.waiting_room_max_capacity}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    waiting_room_max_capacity: parseInt(e.target.value) || 50,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-2">
                Maximum number of customers allowed in the waiting queue
              </p>
            </div>
          )}
        </div>

        {/* Notifications */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Notifications
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Notification Preferences
            </label>
            <input
              type="checkbox"
              checked={localConfig.notification_preferences_enabled}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  notification_preferences_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                SMS Provider
              </label>
              <select
                value={localConfig.sms_provider}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    sms_provider: e.target.value as OperationalConfig["sms_provider"],
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="termii">Termii</option>
                <option value="twilio">Twilio</option>
                <option value="none">None</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Email Provider
              </label>
              <select
                value={localConfig.email_provider}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    email_provider: e.target.value as OperationalConfig["email_provider"],
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="smtp">SMTP</option>
                <option value="sendgrid">SendGrid</option>
                <option value="none">None</option>
              </select>
            </div>
          </div>
        </div>

        {/* Backup & Cache */}
        <div className="space-y-4 border-t border-border pt-6">
          <h3 className="text-lg font-semibold text-foreground">
            Backup & Performance
          </h3>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">
              Enable Automatic Backups
            </label>
            <input
              type="checkbox"
              checked={localConfig.backup_enabled}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  backup_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {localConfig.backup_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Backup Frequency
              </label>
              <select
                value={localConfig.backup_frequency}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    backup_frequency: e.target.value as OperationalConfig["backup_frequency"],
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          )}

          <div className="flex items-center justify-between border-t border-border pt-4">
            <label className="text-sm font-medium text-foreground">
              Enable Cache Optimization
            </label>
            <input
              type="checkbox"
              checked={localConfig.cache_optimization_enabled}
              onChange={(e) =>
                setLocalConfig({
                  ...localConfig,
                  cache_optimization_enabled: e.target.checked,
                })
              }
              className="w-4 h-4"
            />
          </div>

          {localConfig.cache_optimization_enabled && (
            <div className="pl-4 border-l-2 border-primary">
              <label className="block text-sm font-medium text-foreground mb-2">
                Cache TTL (minutes)
              </label>
              <input
                type="number"
                min="1"
                value={localConfig.cache_ttl_minutes}
                onChange={(e) =>
                  setLocalConfig({
                    ...localConfig,
                    cache_ttl_minutes: parseInt(e.target.value) || 60,
                  })
                }
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <p className="text-xs text-muted-foreground mt-2">
                How long cached data remains valid
              </p>
            </div>
          )}
        </div>

        <div className="flex flex-col sm:flex-row justify-end gap-3 border-t border-border pt-6">
          <Button
            onClick={handleSave}
            disabled={isPending}
            className="gap-2 w-full sm:w-auto cursor-pointer"
          >
            <CheckIcon size={18} />
            {isPending ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </div>
    </div>
  );
}
