import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CheckCircleIcon,
  AlertTriangleIcon,
  SparklesIcon,
  EyeIcon,
  TagIcon,
  StarIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";

interface MarketingSettings {
  is_featured?: boolean;
  promotional_banner?: string;
  visibility?: string;
  is_new?: boolean;
  new_until?: string;
  seo_metadata?: {
    meta_title?: string;
    meta_description?: string;
    keywords?: string[];
  };
}

interface MarketingSettingsProps {
  serviceId: string;
  initialSettings?: MarketingSettings;
}

export function MarketingSettings({
  serviceId,
  initialSettings,
}: MarketingSettingsProps) {
  const [settings, setSettings] = useState<MarketingSettings>(
    initialSettings || {}
  );
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [keywordInput, setKeywordInput] = useState("");

  useEffect(() => {
    if (initialSettings) {
      setSettings(initialSettings);
    }
  }, [initialSettings]);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await apiClient.patch(`/api/services/${serviceId}`, {
        marketing_settings: settings,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error("Error saving marketing settings:", err);
      setError("Failed to save marketing settings");
    } finally {
      setIsSaving(false);
    }
  };

  const addKeyword = () => {
    if (!keywordInput.trim()) return;
    const keywords = settings.seo_metadata?.keywords || [];
    if (!keywords.includes(keywordInput.trim())) {
      setSettings({
        ...settings,
        seo_metadata: {
          ...settings.seo_metadata,
          keywords: [...keywords, keywordInput.trim()],
        },
      });
    }
    setKeywordInput("");
  };

  const removeKeyword = (keyword: string) => {
    const keywords = settings.seo_metadata?.keywords || [];
    setSettings({
      ...settings,
      seo_metadata: {
        ...settings.seo_metadata,
        keywords: keywords.filter((k) => k !== keyword),
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <SparklesIcon size={20} className="text-primary" />
            Marketing Settings
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Configure how this service is promoted and displayed
          </p>
        </div>
        <Button
          onClick={handleSave}
          disabled={isSaving}
          className="cursor-pointer transition-all duration-200"
        >
          {isSaving ? (
            <Spinner size="sm" />
          ) : (
            <>
              <CheckCircleIcon size={16} />
              Save Settings
            </>
          )}
        </Button>
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          <CheckCircleIcon size={20} />
          <div>
            <h3 className="font-semibold">Success</h3>
            <p className="text-sm">Marketing settings saved successfully</p>
          </div>
        </Alert>
      )}

      {/* Featured Service */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
            <StarIcon
              size={24}
              className="text-yellow-600 dark:text-yellow-400"
            />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-foreground mb-2">
              Featured Service
            </h4>
            <p className="text-sm text-muted-foreground mb-4">
              Display this service prominently on your website and booking pages
            </p>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.is_featured || false}
                onChange={(e) =>
                  setSettings({ ...settings, is_featured: e.target.checked })
                }
                className="w-4 h-4 rounded border-border"
              />
              <span className="text-sm text-foreground">
                Mark as featured service
              </span>
            </label>
          </div>
        </div>
      </Card>

      {/* Promotional Banner */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
            <TagIcon size={24} className="text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-foreground mb-2">
              Promotional Banner
            </h4>
            <p className="text-sm text-muted-foreground mb-4">
              Add a promotional message to attract customers
            </p>
            <input
              type="text"
              value={settings.promotional_banner || ""}
              onChange={(e) =>
                setSettings({ ...settings, promotional_banner: e.target.value })
              }
              placeholder="e.g., 20% off this month!"
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
            />
          </div>
        </div>
      </Card>

      {/* Visibility Settings */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
            <EyeIcon size={24} className="text-green-600 dark:text-green-400" />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-foreground mb-2">Visibility</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Control who can see and book this service
            </p>
            <select
              value={settings.visibility || "public"}
              onChange={(e) =>
                setSettings({ ...settings, visibility: e.target.value })
              }
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
            >
              <option value="public">Public - Everyone can see</option>
              <option value="members_only">
                Members Only - Registered users
              </option>
              <option value="private">Private - Hidden from listings</option>
            </select>
          </div>
        </div>
      </Card>

      {/* New Badge */}
      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
            <SparklesIcon
              size={24}
              className="text-purple-600 dark:text-purple-400"
            />
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-foreground mb-2">New Badge</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Show a &quot;New&quot; badge to highlight this service
            </p>
            <div className="space-y-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.is_new || false}
                  onChange={(e) =>
                    setSettings({ ...settings, is_new: e.target.checked })
                  }
                  className="w-4 h-4 rounded border-border"
                />
                <span className="text-sm text-foreground">
                  Show &quot;New&quot; badge
                </span>
              </label>
              {settings.is_new && (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Show badge until
                  </label>
                  <input
                    type="date"
                    value={settings.new_until || ""}
                    onChange={(e) =>
                      setSettings({ ...settings, new_until: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* SEO Metadata */}
      <Card className="p-6">
        <h4 className="font-semibold text-foreground mb-4">SEO Metadata</h4>
        <p className="text-sm text-muted-foreground mb-6">
          Optimize this service for search engines
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Meta Title (60 characters max)
            </label>
            <input
              type="text"
              maxLength={60}
              value={settings.seo_metadata?.meta_title || ""}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  seo_metadata: {
                    ...settings.seo_metadata,
                    meta_title: e.target.value,
                  },
                })
              }
              placeholder="Service name for search results"
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {(settings.seo_metadata?.meta_title || "").length}/60 characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Meta Description (160 characters max)
            </label>
            <textarea
              maxLength={160}
              rows={3}
              value={settings.seo_metadata?.meta_description || ""}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  seo_metadata: {
                    ...settings.seo_metadata,
                    meta_description: e.target.value,
                  },
                })
              }
              placeholder="Brief description for search results"
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {(settings.seo_metadata?.meta_description || "").length}/160
              characters
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Keywords
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && addKeyword()}
                placeholder="Add keyword and press Enter"
                className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground"
              />
              <Button
                onClick={addKeyword}
                className="cursor-pointer transition-all duration-200"
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {(settings.seo_metadata?.keywords || []).map((keyword) => (
                <Badge
                  key={keyword}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeKeyword(keyword)}
                >
                  {keyword} ×
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Info Card */}
      <Card className="p-4 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <div className="flex gap-3">
          <SparklesIcon
            size={20}
            className="text-blue-600 flex-shrink-0 mt-0.5"
          />
          <div>
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
              Marketing Tips
            </h4>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• Featured services appear at the top of listings</li>
              <li>• Use promotional banners for limited-time offers</li>
              <li>• SEO metadata helps customers find your services online</li>
              <li>
                • &quot;New&quot; badges attract attention to recently added
                services
              </li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
