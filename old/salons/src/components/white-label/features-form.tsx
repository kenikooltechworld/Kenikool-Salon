"use client";

import { WhiteLabelFeatures } from "@/lib/api/hooks/useWhiteLabel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";

interface FeaturesFormProps {
  features: WhiteLabelFeatures;
  onChange: (features: WhiteLabelFeatures) => void;
}

export function FeaturesForm({ features, onChange }: FeaturesFormProps) {
  const handleChange = (field: keyof WhiteLabelFeatures, value: any) => {
    onChange({ ...features, [field]: value });
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Features</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-[var(--muted)] rounded-[var(--radius-md)]">
          <div>
            <p className="font-semibold">Hide "Powered By" Branding</p>
            <p className="text-sm text-[var(--muted-foreground)]">
              Remove platform branding from your pages
            </p>
          </div>
          <Switch
            checked={features.hide_powered_by}
            onCheckedChange={(checked) =>
              handleChange("hide_powered_by", checked)
            }
          />
        </div>

        <div className="flex items-center justify-between p-3 bg-[var(--muted)] rounded-[var(--radius-md)]">
          <div>
            <p className="font-semibold">Enable Custom CSS</p>
            <p className="text-sm text-[var(--muted-foreground)]">
              Add custom styling to your pages
            </p>
          </div>
          <Switch
            checked={features.enable_custom_css}
            onCheckedChange={(checked) =>
              handleChange("enable_custom_css", checked)
            }
          />
        </div>

        {features.enable_custom_css && (
          <div>
            <Label htmlFor="custom_css">Custom CSS</Label>
            <textarea
              id="custom_css"
              value={features.custom_css || ""}
              onChange={(e) => handleChange("custom_css", e.target.value)}
              placeholder="/* Your custom CSS here */"
              className="w-full h-32 p-3 border rounded-[var(--radius-md)] font-mono text-sm"
            />
          </div>
        )}

        <div>
          <Label htmlFor="custom_email_domain">Custom Email Domain</Label>
          <Input
            id="custom_email_domain"
            value={features.custom_email_domain || ""}
            onChange={(e) =>
              handleChange("custom_email_domain", e.target.value)
            }
            placeholder="yoursalon.com"
          />
        </div>

        <div>
          <Label htmlFor="custom_support_email">Support Email</Label>
          <Input
            id="custom_support_email"
            type="email"
            value={features.custom_support_email || ""}
            onChange={(e) =>
              handleChange("custom_support_email", e.target.value)
            }
            placeholder="support@yoursalon.com"
          />
        </div>

        <div>
          <Label htmlFor="custom_support_phone">Support Phone</Label>
          <Input
            id="custom_support_phone"
            type="tel"
            value={features.custom_support_phone || ""}
            onChange={(e) =>
              handleChange("custom_support_phone", e.target.value)
            }
            placeholder="+234 123 456 7890"
          />
        </div>

        <div>
          <Label htmlFor="custom_terms_url">Terms of Service URL</Label>
          <Input
            id="custom_terms_url"
            type="url"
            value={features.custom_terms_url || ""}
            onChange={(e) => handleChange("custom_terms_url", e.target.value)}
            placeholder="https://yoursalon.com/terms"
          />
        </div>

        <div>
          <Label htmlFor="custom_privacy_url">Privacy Policy URL</Label>
          <Input
            id="custom_privacy_url"
            type="url"
            value={features.custom_privacy_url || ""}
            onChange={(e) => handleChange("custom_privacy_url", e.target.value)}
            placeholder="https://yoursalon.com/privacy"
          />
        </div>
      </div>
    </Card>
  );
}
