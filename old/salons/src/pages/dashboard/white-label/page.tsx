import { useState, useEffect } from "react";
import {
  useGetWhiteLabelConfig,
  useCreateWhiteLabelConfig,
  useUpdateWhiteLabelConfig,
  useGetWhiteLabelStatus,
  WhiteLabelBranding,
  WhiteLabelDomain,
  WhiteLabelFeatures,
} from "@/lib/api/hooks/useWhiteLabel";
import {
  BrandingForm,
  DomainForm,
  FeaturesForm,
} from "@/components/white-label";
import { SparklesIcon, CheckIcon, AlertCircleIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { showToast } from "@/lib/utils/toast";
import { FeatureGate } from "@/components/subscriptions/feature-gate";

export default function WhiteLabelPage() {
  const { data: config, isLoading } = useGetWhiteLabelConfig();
  const { data: status } = useGetWhiteLabelStatus();
  const createMutation = useCreateWhiteLabelConfig();
  const updateMutation = useUpdateWhiteLabelConfig();

  const [branding, setBranding] = useState<WhiteLabelBranding>({});
  const [domain, setDomain] = useState<WhiteLabelDomain>({
    ssl_enabled: true,
    dns_configured: false,
  });
  const [features, setFeatures] = useState<WhiteLabelFeatures>({
    hide_powered_by: false,
    enable_custom_css: false,
  });
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (config) {
      setBranding(config.branding);
      setDomain(config.domain);
      setFeatures(config.features);
      setIsActive(config.is_active);
    }
  }, [config]);

  const handleSave = async () => {
    const data = {
      branding,
      domain,
      features,
      is_active: isActive,
    };

    try {
      if (config) {
        await updateMutation.mutateAsync(data);
        showToast("White-label configuration updated successfully", "success");
      } else {
        await createMutation.mutateAsync(data);
        showToast("White-label configuration created successfully", "success");
      }
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to save configuration",
        "error"
      );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <FeatureGate feature="White Label" requiredPlan="enterprise">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <SparklesIcon size={32} className="text-[var(--primary)]" />
              White Label
            </h1>
            <p className="text-[var(--muted-foreground)] mt-1">
              Customize your salon's branding and domain
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">Active</span>
              <Switch checked={isActive} onCheckedChange={setIsActive} />
            </div>
            <Button
              onClick={handleSave}
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              Save Changes
            </Button>
          </div>
        </div>

        {status && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Configuration Status</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                {status.branding_complete ? (
                  <CheckIcon size={20} className="text-green-600" />
                ) : (
                  <AlertCircleIcon size={20} className="text-yellow-600" />
                )}
                <span className="text-sm">Branding</span>
              </div>
              <div className="flex items-center gap-2">
                {status.has_custom_domain ? (
                  <CheckIcon size={20} className="text-green-600" />
                ) : (
                  <AlertCircleIcon size={20} className="text-yellow-600" />
                )}
                <span className="text-sm">Custom Domain</span>
              </div>
              <div className="flex items-center gap-2">
                {status.domain_verified ? (
                  <CheckIcon size={20} className="text-green-600" />
                ) : (
                  <AlertCircleIcon size={20} className="text-yellow-600" />
                )}
                <span className="text-sm">Domain Verified</span>
              </div>
              <div className="flex items-center gap-2">
                {status.ssl_enabled ? (
                  <CheckIcon size={20} className="text-green-600" />
                ) : (
                  <AlertCircleIcon size={20} className="text-yellow-600" />
                )}
                <span className="text-sm">SSL Enabled</span>
              </div>
              <div className="flex items-center gap-2">
                {status.is_active ? (
                  <CheckIcon size={20} className="text-green-600" />
                ) : (
                  <AlertCircleIcon size={20} className="text-yellow-600" />
                )}
                <span className="text-sm">Active</span>
              </div>
            </div>

            {status.issues.length > 0 && (
              <div className="mt-4 p-3 bg-yellow-50 rounded-[var(--radius-md)]">
                <p className="text-sm font-semibold text-yellow-900 mb-2">
                  Configuration Issues:
                </p>
                <ul className="text-sm text-yellow-800 space-y-1">
                  {status.issues.map((issue, index) => (
                    <li key={index}>• {issue}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        )}

        <div className="space-y-6">
          <BrandingForm branding={branding} onChange={setBranding} />
          <DomainForm domain={domain} onChange={setDomain} />
          <FeaturesForm features={features} onChange={setFeatures} />
        </div>

        <div className="flex justify-end">
          <Button
            onClick={handleSave}
            disabled={createMutation.isPending || updateMutation.isPending}
            size="lg"
          >
            Save All Changes
          </Button>
        </div>
      </div>
    </FeatureGate>
  );
}
