import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon } from "@/components/icons";
import {
  useCreateCampaign,
  useUpdateCampaign,
  Campaign,
  CampaignCreate,
} from "@/lib/api/hooks/useCampaigns";

interface CampaignFormData {
  name: string;
  campaign_type: "birthday" | "seasonal" | "custom" | "win_back";
  message_template: string;
  discount_code?: string;
  discount_value?: number;
  scheduled_at?: string;
  auto_send: boolean;
}

interface CampaignFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  campaign?: Campaign;
}

const CAMPAIGN_TYPES = [
  { value: "birthday", label: "Birthday Campaign" },
  { value: "seasonal", label: "Seasonal Campaign" },
  { value: "custom", label: "Custom Campaign" },
  { value: "win_back", label: "Win Back Campaign" },
];

export function CampaignFormModal({
  isOpen,
  onClose,
  onSuccess,
  campaign,
}: CampaignFormModalProps) {
  const isEdit = !!campaign;

  const getInitialFormData = (): CampaignFormData => ({
    name: campaign?.name || "",
    campaign_type: campaign?.campaign_type || "custom",
    message_template: campaign?.message_template || "",
    discount_code: campaign?.discount_code || "",
    discount_value: campaign?.discount_value || 0,
    scheduled_at: campaign?.scheduled_at || "",
    auto_send: campaign?.auto_send || false,
  });

  const [formData, setFormData] = useState<CampaignFormData>(
    getInitialFormData()
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createCampaignMutation = useCreateCampaign();
  const updateCampaignMutation = useUpdateCampaign(campaign?.id || "");

  const loading =
    createCampaignMutation.isPending || updateCampaignMutation.isPending;

  useEffect(() => {
    if (isOpen) {
      setFormData(getInitialFormData());
      setErrors({});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, campaign?.id]);

  const handleChange = (
    field: keyof CampaignFormData,
    value: string | number | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Campaign name is required";
    }
    if (!formData.message_template.trim()) {
      newErrors.message_template = "Message template is required";
    }
    if (formData.discount_value && formData.discount_value < 0) {
      newErrors.discount_value = "Discount value must be positive";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    try {
      const payload: CampaignCreate = {
        name: formData.name,
        campaign_type: formData.campaign_type,
        message_template: formData.message_template,
        discount_code: formData.discount_code || undefined,
        discount_value: formData.discount_value || undefined,
        scheduled_at: formData.scheduled_at || undefined,
        auto_send: formData.auto_send,
      };

      if (isEdit && campaign) {
        await updateCampaignMutation.mutateAsync(payload);
      } else {
        await createCampaignMutation.mutateAsync(payload);
      }

      onSuccess();
      onClose();
    } catch (error) {
      console.error("Submit error:", error);
      const errorMessage =
        error instanceof Error ? error.message : "An error occurred";
      setErrors({
        submit: errorMessage,
      });
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          {isEdit ? "Edit Campaign" : "Create Campaign"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.submit && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm font-semibold mb-1">Error</p>
                <p className="text-sm">{errors.submit}</p>
              </div>
            </Alert>
          )}

          {/* Campaign Name */}
          <div>
            <Label htmlFor="name" required>
              Campaign Name
            </Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleChange("name", e.target.value)}
              placeholder="e.g., Summer Sale 2024"
              error={!!errors.name}
            />
            {errors.name && (
              <p className="text-sm text-[var(--error)] mt-1">{errors.name}</p>
            )}
          </div>

          {/* Campaign Type */}
          <div>
            <Label htmlFor="campaign_type" required>
              Campaign Type
            </Label>
            <select
              id="campaign_type"
              value={formData.campaign_type}
              onChange={(e) =>
                handleChange(
                  "campaign_type",
                  e.target.value as CampaignFormData["campaign_type"]
                )
              }
              className="w-full px-3 py-2 border-2 border-[var(--border)] rounded-lg bg-background text-foreground"
            >
              {CAMPAIGN_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Message Template */}
          <div>
            <Label htmlFor="message_template" required>
              Message Template
            </Label>
            <Textarea
              id="message_template"
              value={formData.message_template}
              onChange={(e) => handleChange("message_template", e.target.value)}
              placeholder="Hi {name}, we have a special offer for you..."
              rows={4}
              error={!!errors.message_template}
            />
            {errors.message_template && (
              <p className="text-sm text-[var(--error)] mt-1">
                {errors.message_template}
              </p>
            )}
            <p className="text-xs text-muted-foreground mt-1">
              Use {"{name}"} for client name, {"{discount}"} for discount code
            </p>
          </div>

          {/* Discount Code and Value */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="discount_code">Discount Code</Label>
              <Input
                id="discount_code"
                value={formData.discount_code}
                onChange={(e) => handleChange("discount_code", e.target.value)}
                placeholder="SUMMER20"
              />
            </div>
            <div>
              <Label htmlFor="discount_value">Discount Value (%)</Label>
              <Input
                id="discount_value"
                type="number"
                value={formData.discount_value || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  handleChange(
                    "discount_value",
                    value === "" ? 0 : parseFloat(value)
                  );
                }}
                placeholder="20"
                error={!!errors.discount_value}
              />
              {errors.discount_value && (
                <p className="text-sm text-[var(--error)] mt-1">
                  {errors.discount_value}
                </p>
              )}
            </div>
          </div>

          {/* Scheduled Date */}
          <div>
            <Label htmlFor="scheduled_at">Schedule For (Optional)</Label>
            <Input
              id="scheduled_at"
              type="datetime-local"
              value={formData.scheduled_at}
              onChange={(e) => handleChange("scheduled_at", e.target.value)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Leave empty to send immediately
            </p>
          </div>

          {/* Auto Send */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="auto_send"
              checked={formData.auto_send}
              onChange={(e) => handleChange("auto_send", e.target.checked)}
              className="rounded border-[var(--border)]"
            />
            <Label htmlFor="auto_send" className="cursor-pointer">
              Auto-send when scheduled time arrives
            </Label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? (
                <>
                  <Spinner size="sm" />
                  {isEdit ? "Updating..." : "Creating..."}
                </>
              ) : (
                <>{isEdit ? "Update Campaign" : "Create Campaign"}</>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
