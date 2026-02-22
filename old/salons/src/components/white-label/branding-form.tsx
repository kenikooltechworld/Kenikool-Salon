"use client";

import { WhiteLabelBranding, useUploadLogo, useUploadFavicon } from "@/lib/api/hooks/useWhiteLabel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Upload, X, Loader2 } from "lucide-react";

interface BrandingFormProps {
  branding: WhiteLabelBranding;
  onChange: (branding: WhiteLabelBranding) => void;
  onUploadLogo?: (file: File) => Promise<string>;
  onUploadFavicon?: (file: File) => Promise<string>;
  onValidationError?: (error: string) => void;
  useHooks?: boolean;
}

export function BrandingForm({ 
  branding, 
  onChange,
  onUploadLogo,
  onUploadFavicon,
  onValidationError,
  useHooks = false
}: BrandingFormProps) {
  const uploadLogoMutation = useUploadLogo();
  const uploadFaviconMutation = useUploadFavicon();
  
  const [logoUploading, setLogoUploading] = useState(false);
  const [faviconUploading, setFaviconUploading] = useState(false);
  const [logoPreview, setLogoPreview] = useState<string | null>(branding.logo_url || null);
  const [faviconPreview, setFaviconPreview] = useState<string | null>(branding.favicon_url || null);
  const [logoError, setLogoError] = useState<string | null>(null);
  const [faviconError, setFaviconError] = useState<string | null>(null);

  const handleChange = (field: keyof WhiteLabelBranding, value: string) => {
    onChange({ ...branding, [field]: value });
  };

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/png", "image/jpeg", "image/svg+xml"];
    if (!validTypes.includes(file.type)) {
      const error = "Invalid file type. Please upload PNG, JPG, or SVG.";
      setLogoError(error);
      onValidationError?.(error);
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      const error = "File too large. Maximum size is 5MB.";
      setLogoError(error);
      onValidationError?.(error);
      return;
    }

    try {
      setLogoUploading(true);
      setLogoError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setLogoPreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);

      // Upload file using hook or callback
      let url: string;
      if (useHooks) {
        const result = await uploadLogoMutation.mutateAsync(file);
        url = result.asset_url;
      } else if (onUploadLogo) {
        url = await onUploadLogo(file);
      } else {
        throw new Error("No upload handler available");
      }
      
      handleChange("logo_url", url);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Failed to upload logo";
      setLogoError(errorMsg);
      onValidationError?.(errorMsg);
    } finally {
      setLogoUploading(false);
    }
  };

  const handleFaviconUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/png", "image/jpeg", "image/svg+xml"];
    if (!validTypes.includes(file.type)) {
      const error = "Invalid file type. Please upload PNG, JPG, or SVG.";
      setFaviconError(error);
      onValidationError?.(error);
      return;
    }

    // Validate file size (1MB max)
    if (file.size > 1 * 1024 * 1024) {
      const error = "File too large. Maximum size is 1MB.";
      setFaviconError(error);
      onValidationError?.(error);
      return;
    }

    try {
      setFaviconUploading(true);
      setFaviconError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setFaviconPreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);

      // Upload file using hook or callback
      let url: string;
      if (useHooks) {
        const result = await uploadFaviconMutation.mutateAsync(file);
        url = result.asset_url;
      } else if (onUploadFavicon) {
        url = await onUploadFavicon(file);
      } else {
        throw new Error("No upload handler available");
      }
      
      handleChange("favicon_url", url);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Failed to upload favicon";
      setFaviconError(errorMsg);
      onValidationError?.(errorMsg);
    } finally {
      setFaviconUploading(false);
    }
  };

  const clearLogo = () => {
    setLogoPreview(null);
    handleChange("logo_url", "");
  };

  const clearFavicon = () => {
    setFaviconPreview(null);
    handleChange("favicon_url", "");
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Branding</h3>
      <div className="space-y-4">
        <div>
          <Label htmlFor="company_name">Company Name</Label>
          <Input
            id="company_name"
            value={branding.company_name || ""}
            onChange={(e) => handleChange("company_name", e.target.value)}
            placeholder="Your Salon Name"
          />
        </div>

        <div>
          <Label htmlFor="tagline">Tagline</Label>
          <Input
            id="tagline"
            value={branding.tagline || ""}
            onChange={(e) => handleChange("tagline", e.target.value)}
            placeholder="Your salon's tagline"
          />
        </div>

        {/* Logo Upload */}
        <div>
          <Label>Logo</Label>
          <div className="space-y-2">
            {logoPreview && (
              <div className="relative w-32 h-32 border rounded-lg overflow-hidden bg-gray-50">
                <img 
                  src={logoPreview} 
                  alt="Logo preview" 
                  className="w-full h-full object-contain p-2"
                />
                <button
                  onClick={clearLogo}
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                >
                  <X size={16} />
                </button>
              </div>
            )}
            {logoError && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                {logoError}
              </div>
            )}
            <div className="flex gap-2">
              <label className="flex-1">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/svg+xml"
                  onChange={handleLogoUpload}
                  disabled={logoUploading}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={logoUploading}
                  onClick={(e) => {
                    e.preventDefault();
                    (e.currentTarget.parentElement?.querySelector('input[type="file"]') as HTMLInputElement)?.click();
                  }}
                >
                  {logoUploading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload Logo
                    </>
                  )}
                </Button>
              </label>
            </div>
            <p className="text-sm text-gray-500">PNG, JPG, or SVG (max 5MB)</p>
          </div>
        </div>

        {/* Favicon Upload */}
        <div>
          <Label>Favicon</Label>
          <div className="space-y-2">
            {faviconPreview && (
              <div className="relative w-16 h-16 border rounded-lg overflow-hidden bg-gray-50">
                <img 
                  src={faviconPreview} 
                  alt="Favicon preview" 
                  className="w-full h-full object-contain p-1"
                />
                <button
                  onClick={clearFavicon}
                  className="absolute top-0 right-0 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                >
                  <X size={12} />
                </button>
              </div>
            )}
            {faviconError && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                {faviconError}
              </div>
            )}
            <div className="flex gap-2">
              <label className="flex-1">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/svg+xml"
                  onChange={handleFaviconUpload}
                  disabled={faviconUploading}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={faviconUploading}
                  onClick={(e) => {
                    e.preventDefault();
                    (e.currentTarget.parentElement?.querySelector('input[type="file"]') as HTMLInputElement)?.click();
                  }}
                >
                  {faviconUploading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload Favicon
                    </>
                  )}
                </Button>
              </label>
            </div>
            <p className="text-sm text-gray-500">PNG, JPG, or SVG - 16x16, 32x32, or 64x64 (max 1MB)</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label htmlFor="primary_color">Primary Color</Label>
            <div className="flex gap-2">
              <Input
                id="primary_color"
                value={branding.primary_color || ""}
                onChange={(e) => handleChange("primary_color", e.target.value)}
                placeholder="#FF6B6B"
              />
              <input
                type="color"
                value={branding.primary_color || "#FF6B6B"}
                onChange={(e) => handleChange("primary_color", e.target.value)}
                className="w-12 h-10 rounded border"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="secondary_color">Secondary Color</Label>
            <div className="flex gap-2">
              <Input
                id="secondary_color"
                value={branding.secondary_color || ""}
                onChange={(e) =>
                  handleChange("secondary_color", e.target.value)
                }
                placeholder="#4ECDC4"
              />
              <input
                type="color"
                value={branding.secondary_color || "#4ECDC4"}
                onChange={(e) =>
                  handleChange("secondary_color", e.target.value)
                }
                className="w-12 h-10 rounded border"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="accent_color">Accent Color</Label>
            <div className="flex gap-2">
              <Input
                id="accent_color"
                value={branding.accent_color || ""}
                onChange={(e) => handleChange("accent_color", e.target.value)}
                placeholder="#FFE66D"
              />
              <input
                type="color"
                value={branding.accent_color || "#FFE66D"}
                onChange={(e) => handleChange("accent_color", e.target.value)}
                className="w-12 h-10 rounded border"
              />
            </div>
          </div>
        </div>

        <div>
          <Label htmlFor="font_family">Font Family</Label>
          <Input
            id="font_family"
            value={branding.font_family || ""}
            onChange={(e) => handleChange("font_family", e.target.value)}
            placeholder="Inter, sans-serif"
          />
        </div>
      </div>
    </Card>
  );
}
