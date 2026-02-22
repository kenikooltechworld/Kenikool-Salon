"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import { useUpdateTenant, useUploadLogo } from "@/lib/api/hooks/useTenant";
import { UploadIcon } from "@/components/icons";

interface ProfileData {
  businessName: string;
  description: string;
  phone: string;
  email: string;
  address: string;
  primaryColor: string;
  secondaryColor: string;
  logo: string | null;
}

interface ProfileSetupProps {
  onComplete: (data: ProfileData) => void;
  initialData: ProfileData | null;
}

export function ProfileSetup({ onComplete, initialData }: ProfileSetupProps) {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    businessName: initialData?.businessName || "",
    description: initialData?.description || "",
    phone: initialData?.phone || "",
    email: initialData?.email || "",
    address: initialData?.address || "",
    primaryColor: initialData?.primaryColor || "#6366f1",
    secondaryColor: initialData?.secondaryColor || "#8b5cf6",
    logo: initialData?.logo || null,
  });
  const [error, setError] = useState("");
  const [logoPreview, setLogoPreview] = useState<string | null>(
    initialData?.logo || null
  );
  const [uploadProgress, setUploadProgress] = useState(0);

  const { mutate: updateTenant, isPending: loading } = useUpdateTenant();
  const { mutate: uploadLogo, isPending: uploadingLogo } = useUploadLogo();

  const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      showToast({
        title: "File Too Large",
        description: "Please upload an image smaller than 5MB",
        variant: "error",
      });
      return;
    }

    // Show preview immediately
    const reader = new FileReader();
    reader.onloadend = () => {
      setLogoPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Reset progress
    setUploadProgress(0);

    // Upload to backend
    uploadLogo(
      {
        file,
        onProgress: (progress) => {
          setUploadProgress(progress);
        },
      },
      {
        onSuccess: (data) => {
          setFormData((prev) => ({ ...prev, logo: data.logo_url || null }));
          setUploadProgress(100);
          showToast({
            title: "Logo Uploaded",
            description: "Your salon logo has been uploaded successfully",
            variant: "success",
          });
        },
        onError: (error) => {
          setUploadProgress(0);
          showToast({
            title: "Upload Failed",
            description:
              error.response?.data?.message ||
              "Failed to upload logo. Please try again.",
            variant: "error",
          });
        },
      }
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.businessName || !formData.phone || !formData.email) {
      setError("Please fill in all required fields");
      return;
    }

    updateTenant(
      {
        salon_name: formData.businessName,
        description: formData.description,
        phone: formData.phone,
        email: formData.email,
        address: formData.address,
        brand_color: formData.primaryColor,
      },
      {
        onSuccess: () => {
          showToast({
            title: "Profile Updated",
            description: "Your salon profile has been saved",
            variant: "success",
          });
          onComplete(formData);
        },
        onError: (error) => {
          const errorMessage =
            error.response?.data?.message ||
            error.message ||
            "An error occurred";
          setError(errorMessage);
          showToast({
            title: "Error",
            description: errorMessage,
            variant: "error",
          });
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-2">
          Customize Your Salon Profile
        </h2>
        <p className="text-[var(--muted-foreground)]">
          Add your branding and business information
        </p>
      </div>

      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}

      {/* Logo Upload */}
      <div>
        <Label>Salon Logo</Label>
        <div className="mt-2 flex items-center gap-4">
          <div className="relative">
            {logoPreview ? (
              <img
                src={logoPreview}
                alt="Logo preview"
                className="w-24 h-24 object-cover rounded-lg border-2 border-[var(--border)]"
              />
            ) : (
              <div className="w-24 h-24 bg-[var(--muted)] rounded-lg flex items-center justify-center border-2 border-dashed border-[var(--border)]">
                <UploadIcon
                  size={32}
                  className="text-[var(--muted-foreground)]"
                />
              </div>
            )}
            {uploadingLogo && (
              <div className="absolute inset-0 bg-black/60 rounded-lg flex items-center justify-center">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin" />
                  <span className="text-xs text-white font-bold">
                    {uploadProgress}%
                  </span>
                </div>
              </div>
            )}
          </div>
          <div className="flex-1">
            <input
              type="file"
              accept="image/*"
              onChange={handleLogoUpload}
              className="hidden"
              id="logo-upload"
              disabled={uploadingLogo}
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => document.getElementById("logo-upload")?.click()}
              disabled={uploadingLogo}
              loading={uploadingLogo}
            >
              {uploadingLogo ? "Uploading..." : "Upload Logo"}
            </Button>
            <p className="text-xs text-[var(--muted-foreground)] mt-1">
              PNG, JPG up to 5MB
            </p>
            {uploadingLogo && (
              <div className="mt-2">
                <div className="w-full bg-[var(--muted)] rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-[var(--primary)] h-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-[var(--muted-foreground)] mt-1">
                  Uploading... {uploadProgress}%
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Business Name */}
      <div>
        <Label htmlFor="businessName" required>
          Business Name
        </Label>
        <Input
          id="businessName"
          value={formData.businessName}
          onChange={(e) =>
            setFormData({ ...formData, businessName: e.target.value })
          }
          placeholder="Your Salon Name"
          disabled={loading}
          className="mt-2"
        />
      </div>

      {/* Description */}
      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          placeholder="Tell clients about your salon..."
          rows={3}
          disabled={loading}
          className="mt-2"
        />
      </div>

      {/* Contact Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="phone" required>
            Phone Number
          </Label>
          <Input
            id="phone"
            type="tel"
            value={formData.phone}
            onChange={(e) =>
              setFormData({ ...formData, phone: e.target.value })
            }
            placeholder="+234 800 000 0000"
            disabled={loading}
            className="mt-2"
          />
        </div>
        <div>
          <Label htmlFor="email" required>
            Email Address
          </Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
            placeholder="salon@example.com"
            disabled={loading}
            className="mt-2"
          />
        </div>
      </div>

      {/* Address */}
      <div>
        <Label htmlFor="address">Address</Label>
        <Input
          id="address"
          value={formData.address}
          onChange={(e) =>
            setFormData({ ...formData, address: e.target.value })
          }
          placeholder="123 Main Street, Lagos"
          disabled={loading}
          className="mt-2"
        />
      </div>

      {/* Brand Colors */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="primaryColor">Primary Color</Label>
          <div className="mt-2 flex items-center gap-2">
            <input
              type="color"
              id="primaryColor"
              value={formData.primaryColor}
              onChange={(e) =>
                setFormData({ ...formData, primaryColor: e.target.value })
              }
              className="w-12 h-12 rounded border-2 border-[var(--border)] cursor-pointer"
            />
            <Input
              value={formData.primaryColor}
              onChange={(e) =>
                setFormData({ ...formData, primaryColor: e.target.value })
              }
              placeholder="#6366f1"
              disabled={loading}
            />
          </div>
        </div>
        <div>
          <Label htmlFor="secondaryColor">Secondary Color</Label>
          <div className="mt-2 flex items-center gap-2">
            <input
              type="color"
              id="secondaryColor"
              value={formData.secondaryColor}
              onChange={(e) =>
                setFormData({ ...formData, secondaryColor: e.target.value })
              }
              className="w-12 h-12 rounded border-2 border-[var(--border)] cursor-pointer"
            />
            <Input
              value={formData.secondaryColor}
              onChange={(e) =>
                setFormData({ ...formData, secondaryColor: e.target.value })
              }
              placeholder="#8b5cf6"
              disabled={loading}
            />
          </div>
        </div>
      </div>

      <Button type="submit" fullWidth loading={loading || uploadingLogo}>
        Continue
      </Button>
    </form>
  );
}
