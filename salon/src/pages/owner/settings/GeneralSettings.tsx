import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { CheckIcon, ArrowLeftIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { useNavigate } from "react-router-dom";
import {
  useTenantSettings,
  useUpdateTenantSettings,
  type TenantSettingsData,
} from "@/hooks/owner/useTenantSettings";
import { useSubscription } from "@/hooks/owner/useSubscription";

const DEFAULT_SETTINGS: TenantSettingsData = {
  salon_name: "My Salon",
  email: "salon@example.com",
  phone: "+234 801 234 5678",
  address: "123 Main Street, Lagos",
  tax_rate: 0,
  currency: "NGN",
  timezone: "Africa/Lagos",
  language: "en",
  business_hours: {
    monday: { open_time: "09:00", close_time: "18:00", is_closed: false },
    tuesday: { open_time: "09:00", close_time: "18:00", is_closed: false },
    wednesday: { open_time: "09:00", close_time: "18:00", is_closed: false },
    thursday: { open_time: "09:00", close_time: "18:00", is_closed: false },
    friday: { open_time: "09:00", close_time: "18:00", is_closed: false },
    saturday: { open_time: "10:00", close_time: "16:00", is_closed: false },
    sunday: { open_time: "00:00", close_time: "00:00", is_closed: true },
  },
  notification_email: true,
  notification_sms: false,
  notification_push: false,
  logo_url: undefined,
  primary_color: "#000000",
  secondary_color: "#FFFFFF",
  appointment_reminder_hours: 24,
  allow_online_booking: true,
  require_customer_approval: false,
  auto_confirm_bookings: true,
};

export default function GeneralSettings() {
  const navigate = useNavigate();
  const { data: tenantData, isLoading } = useTenantSettings();
  const { mutate: updateSettings, isPending } = useUpdateTenantSettings();
  const { data: subscription } = useSubscription();
  const { addToast } = useToast();
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);

  // Get plan name from subscription
  const planName = subscription?.plan_name || "Loading...";

  // Get full subdomain URL from backend (no hardcoding)
  const subdomainUrl = tenantData?.subdomain_url || "";

  useEffect(() => {
    if (tenantData) {
      setSettings(tenantData);
      if (tenantData.logo_url) {
        setLogoPreview(tenantData.logo_url);
      }
    }
  }, [tenantData]);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        setLogoPreview(result);
        setSettings({ ...settings, logo_url: result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async () => {
    try {
      updateSettings(settings, {
        onSuccess: () => {
          addToast({
            title: "Success",
            description: "Settings saved successfully!",
            variant: "success",
          });
        },
        onError: (error) => {
          addToast({
            title: "Error",
            description:
              error instanceof Error
                ? error.message
                : "Failed to save settings",
            variant: "error",
          });
        },
      });
    } catch (error) {
      addToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to save settings",
        variant: "error",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
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
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            General Settings
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage basic business information and preferences
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="bg-card border border-border rounded-lg p-4 md:p-6">
          <div className="space-y-4">
            <div className="h-6 bg-muted rounded animate-pulse w-1/4" />
            <div className="space-y-3">
              {[...Array(7)].map((_, i) => (
                <div key={i} className="h-10 bg-muted rounded animate-pulse" />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <>
          {/* Account Information */}
          <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-4">
            <h3 className="text-lg font-semibold text-foreground">
              Account Information
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Subscription Status
                </label>
                <input
                  type="text"
                  value={
                    subscription?.status
                      ? subscription.status.charAt(0).toUpperCase() +
                        subscription.status.slice(1)
                      : "Loading..."
                  }
                  disabled
                  className="w-full px-3 py-2 border border-border rounded-lg bg-muted text-foreground opacity-60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Plan
                </label>
                <input
                  type="text"
                  value={planName}
                  disabled
                  className="w-full px-3 py-2 border border-border rounded-lg bg-muted text-foreground opacity-60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Billing Cycle
                </label>
                <input
                  type="text"
                  value={
                    subscription?.billing_cycle
                      ? subscription.billing_cycle.charAt(0).toUpperCase() +
                        subscription.billing_cycle.slice(1)
                      : "Loading..."
                  }
                  disabled
                  className="w-full px-3 py-2 border border-border rounded-lg bg-muted text-foreground opacity-60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Subdomain URL
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={subdomainUrl}
                    disabled
                    className="flex-1 px-3 py-2 border border-border rounded-lg bg-muted text-foreground opacity-60"
                  />
                  <Button
                    onClick={async () => {
                      if (subdomainUrl) {
                        try {
                          await navigator.clipboard.writeText(subdomainUrl);
                          addToast({
                            title: "Copied",
                            description: "Subdomain URL copied to clipboard",
                            variant: "success",
                          });
                        } catch (error) {
                          addToast({
                            title: "Error",
                            description: "Failed to copy subdomain URL",
                            variant: "error",
                          });
                        }
                      }
                    }}
                    variant="outline"
                    size="sm"
                    className="whitespace-nowrap cursor-pointer"
                  >
                    Copy
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Basic Information */}
          <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground">
                Basic Information
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Salon Name
                  </label>
                  <input
                    type="text"
                    value={settings.salon_name}
                    onChange={(e) =>
                      setSettings({ ...settings, salon_name: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={settings.email}
                    onChange={(e) =>
                      setSettings({ ...settings, email: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={settings.phone}
                    onChange={(e) =>
                      setSettings({ ...settings, phone: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Address
                  </label>
                  <input
                    type="text"
                    value={settings.address}
                    onChange={(e) =>
                      setSettings({ ...settings, address: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            {/* Business Hours */}
            <div className="space-y-4 border-t border-border pt-6">
              <h3 className="text-lg font-semibold text-foreground">
                Business Hours
              </h3>

              <div className="space-y-3">
                {Object.entries(settings.business_hours).map(([day, hours]) => (
                  <div
                    key={day}
                    className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4"
                  >
                    <label className="w-full sm:w-24 text-sm font-medium text-foreground capitalize">
                      {day}
                    </label>

                    <div className="flex items-center gap-3 flex-1">
                      <input
                        type="checkbox"
                        checked={!hours.is_closed}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            business_hours: {
                              ...settings.business_hours,
                              [day]: { ...hours, is_closed: !e.target.checked },
                            },
                          })
                        }
                        className="w-4 h-4"
                      />

                      {!hours.is_closed && (
                        <>
                          <input
                            type="time"
                            value={hours.open_time}
                            onChange={(e) =>
                              setSettings({
                                ...settings,
                                business_hours: {
                                  ...settings.business_hours,
                                  [day]: {
                                    ...hours,
                                    open_time: e.target.value,
                                  },
                                },
                              })
                            }
                            className="px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                          />

                          <span className="text-muted-foreground text-sm">
                            to
                          </span>

                          <input
                            type="time"
                            value={hours.close_time}
                            onChange={(e) =>
                              setSettings({
                                ...settings,
                                business_hours: {
                                  ...settings.business_hours,
                                  [day]: {
                                    ...hours,
                                    close_time: e.target.value,
                                  },
                                },
                              })
                            }
                            className="px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                          />
                        </>
                      )}

                      {hours.is_closed && (
                        <span className="text-sm text-muted-foreground">
                          Closed
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Business Configuration */}
            <div className="space-y-4 border-t border-border pt-6">
              <h3 className="text-lg font-semibold text-foreground">
                Business Configuration
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Tax Rate (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={settings.tax_rate}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        tax_rate: parseFloat(e.target.value) || 0,
                      })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Currency
                  </label>
                  <select
                    value={settings.currency}
                    onChange={(e) =>
                      setSettings({ ...settings, currency: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="NGN">NGN (Nigerian Naira)</option>
                    <option value="USD">USD (US Dollar)</option>
                    <option value="EUR">EUR (Euro)</option>
                    <option value="GBP">GBP (British Pound)</option>
                    <option value="ZAR">ZAR (South African Rand)</option>
                    <option value="KES">KES (Kenyan Shilling)</option>
                    <option value="GHS">GHS (Ghanaian Cedi)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Timezone
                  </label>
                  <select
                    value={settings.timezone}
                    onChange={(e) =>
                      setSettings({ ...settings, timezone: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="Africa/Lagos">Africa/Lagos (WAT)</option>
                    <option value="Africa/Johannesburg">
                      Africa/Johannesburg (SAST)
                    </option>
                    <option value="Africa/Cairo">Africa/Cairo (EET)</option>
                    <option value="Africa/Nairobi">Africa/Nairobi (EAT)</option>
                    <option value="Africa/Accra">Africa/Accra (GMT)</option>
                    <option value="UTC">UTC</option>
                    <option value="Europe/London">
                      Europe/London (GMT/BST)
                    </option>
                    <option value="America/New_York">
                      America/New_York (EST/EDT)
                    </option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Language
                  </label>
                  <select
                    value={settings.language}
                    onChange={(e) =>
                      setSettings({ ...settings, language: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="en">English</option>
                    <option value="fr">Français (French)</option>
                    <option value="es">Español (Spanish)</option>
                    <option value="pt">Português (Portuguese)</option>
                    <option value="yo">Yorùbá (Yoruba)</option>
                    <option value="ha">Hausa</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Branding */}
            <div className="space-y-4 border-t border-border pt-6">
              <h3 className="text-lg font-semibold text-foreground">
                Branding
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Logo
                  </label>
                  <div className="flex gap-4">
                    {logoPreview && (
                      <div className="w-24 h-24 border border-border rounded-lg overflow-hidden bg-muted flex items-center justify-center">
                        <img
                          src={logoPreview}
                          alt="Logo preview"
                          className="w-full h-full object-contain"
                        />
                      </div>
                    )}
                    <div className="flex-1">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleLogoChange}
                        className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                      />
                      <p className="text-xs text-muted-foreground mt-2">
                        Recommended: 200x200px, PNG or JPG
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Primary Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={settings.primary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          primary_color: e.target.value,
                        })
                      }
                      className="w-12 h-10 border border-border rounded-lg cursor-pointer"
                    />
                    <input
                      type="text"
                      value={settings.primary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          primary_color: e.target.value,
                        })
                      }
                      className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Secondary Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={settings.secondary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          secondary_color: e.target.value,
                        })
                      }
                      className="w-12 h-10 border border-border rounded-lg cursor-pointer"
                    />
                    <input
                      type="text"
                      value={settings.secondary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          secondary_color: e.target.value,
                        })
                      }
                      className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Booking Settings */}
            <div className="space-y-4 border-t border-border pt-6">
              <h3 className="text-lg font-semibold text-foreground">
                Booking Settings
              </h3>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground">
                    Allow Online Booking
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.allow_online_booking}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        allow_online_booking: e.target.checked,
                      })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground">
                    Auto-Confirm Bookings
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.auto_confirm_bookings}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        auto_confirm_bookings: e.target.checked,
                      })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground">
                    Require Customer Approval
                  </label>
                  <input
                    type="checkbox"
                    checked={settings.require_customer_approval}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        require_customer_approval: e.target.checked,
                      })
                    }
                    className="w-4 h-4"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Appointment Reminder (hours before)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="168"
                    value={settings.appointment_reminder_hours}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        appointment_reminder_hours:
                          parseInt(e.target.value) || 24,
                      })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            {/* Save Button */}
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
        </>
      )}
    </div>
  );
}
