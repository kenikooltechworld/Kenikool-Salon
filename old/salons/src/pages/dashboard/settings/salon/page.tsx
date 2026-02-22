import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  BuildingIcon,
  MailIcon,
  PhoneIcon,
  MapPinIcon,
  CheckIcon,
  ImageIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useTenant } from "@/lib/api/hooks/useTenant";
import { apiClient } from "@/lib/api/client";

export default function SalonSettingsPage() {
  const { data: tenant, isLoading, refetch } = useTenant();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [formData, setFormData] = useState({
    salon_name: "",
    owner_name: "",
    email: "",
    phone: "",
    address: "",
    description: "",
    logo_url: "",
    brand_color: "#6366f1",
    bank_name: "",
    account_name: "",
    account_number: "",
  });

  useEffect(() => {
    if (tenant) {
      setFormData({
        salon_name: tenant.salon_name || "",
        owner_name: tenant.owner_name || "",
        email: tenant.email || "",
        phone: tenant.phone || "",
        address: tenant.address || "",
        description: tenant.description || "",
        logo_url: tenant.logo_url || "",
        brand_color: tenant.brand_color || "#6366f1",
        bank_name: tenant.bank_account?.bank_name || "",
        account_name: tenant.bank_account?.account_name || "",
        account_number: tenant.bank_account?.account_number || "",
      });
    }
  }, [tenant]);

  const handleSave = async () => {
    setIsSaving(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      // Call API to update tenant
      await apiClient.patch("/api/tenants/me", {
        salon_name: formData.salon_name,
        owner_name: formData.owner_name,
        email: formData.email,
        phone: formData.phone,
        address: formData.address,
        description: formData.description,
        brand_color: formData.brand_color,
        bank_account: {
          bank_name: formData.bank_name,
          account_name: formData.account_name,
          account_number: formData.account_number,
        },
      });

      setSuccessMessage("Salon settings updated successfully!");
      setIsEditing(false);

      // Refresh tenant data
      await refetch();

      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (error: unknown) {
      console.error("Error updating salon settings:", error);
      const err = error as { response?: { data?: { detail?: string } } };
      const message =
        err.response?.data?.detail ||
        "Failed to update settings. Please try again.";
      setErrorMessage(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogoClick = () => {
    fileInputRef.current?.click();
  };

  const handleLogoUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      setErrorMessage("Please select an image file");
      setTimeout(() => setErrorMessage(""), 3000);
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage("File size must be less than 5MB");
      setTimeout(() => setErrorMessage(""), 3000);
      return;
    }

    setIsUploading(true);
    setSuccessMessage("");
    setErrorMessage("");

    try {
      // Create form data
      const uploadFormData = new FormData();
      uploadFormData.append("file", file);

      // Upload to backend
      const response = await apiClient.post<{ logo_url: string }>(
        "/api/tenants/me/logo",
        uploadFormData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Update local state with new logo URL
      setFormData((prev) => ({
        ...prev,
        logo_url: response.data.logo_url,
      }));

      setSuccessMessage("Logo uploaded successfully!");

      // Refresh tenant data
      await refetch();

      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (error: unknown) {
      console.error("Error uploading logo:", error);
      const err = error as { response?: { data?: { detail?: string } } };
      const message =
        err.response?.data?.detail ||
        "Failed to upload logo. Please try again.";
      setErrorMessage(message);
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Salon Settings</h1>
        <p className="text-muted-foreground">
          Manage your salon information and branding
        </p>
      </div>

      {/* Success Message */}
      {successMessage && (
        <Alert variant="success">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {/* Error Message */}
      {errorMessage && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      {/* Business Information */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-foreground">
            Business Information
          </h2>
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)}>Edit Settings</Button>
          )}
        </div>

        <div className="space-y-4">
          {/* Salon Name */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <BuildingIcon size={16} className="inline mr-2" />
              Salon Name *
            </label>
            <Input
              value={formData.salon_name}
              onChange={(e) =>
                setFormData({ ...formData, salon_name: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Enter salon name"
            />
          </div>

          {/* Owner Name */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Owner Name *
            </label>
            <Input
              value={formData.owner_name}
              onChange={(e) =>
                setFormData({ ...formData, owner_name: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Enter owner name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <MailIcon size={16} className="inline mr-2" />
              Business Email *
            </label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Enter business email"
            />
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <PhoneIcon size={16} className="inline mr-2" />
              Business Phone *
            </label>
            <Input
              type="tel"
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Enter business phone"
            />
          </div>

          {/* Address */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <MapPinIcon size={16} className="inline mr-2" />
              Address
            </label>
            <textarea
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Enter business address"
              rows={3}
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground resize-none"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              disabled={!isEditing}
              placeholder="Brief description of your salon"
              rows={4}
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground resize-none"
            />
          </div>

          {/* Bank Details Section */}
          <div className="pt-4 border-t border-[var(--border)]">
            <h3 className="text-md font-semibold text-foreground mb-4">
              Bank Account Details (for Online Payments)
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Clients will see these details when they choose to pay online via
              bank transfer
            </p>

            {/* Bank Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-foreground mb-2">
                Bank Name
              </label>
              <Input
                value={formData.bank_name}
                onChange={(e) =>
                  setFormData({ ...formData, bank_name: e.target.value })
                }
                disabled={!isEditing}
                placeholder="e.g., GTBank, Access Bank, First Bank"
              />
            </div>

            {/* Account Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-foreground mb-2">
                Account Name
              </label>
              <Input
                value={formData.account_name}
                onChange={(e) =>
                  setFormData({ ...formData, account_name: e.target.value })
                }
                disabled={!isEditing}
                placeholder="Account holder name"
              />
            </div>

            {/* Account Number */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Account Number
              </label>
              <Input
                value={formData.account_number}
                onChange={(e) =>
                  setFormData({ ...formData, account_number: e.target.value })
                }
                disabled={!isEditing}
                placeholder="10-digit account number"
                maxLength={10}
              />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {isEditing && (
          <div className="flex gap-3 mt-6">
            <Button
              variant="outline"
              onClick={() => {
                setIsEditing(false);
                setFormData({
                  salon_name: tenant?.salon_name || "",
                  owner_name: tenant?.owner_name || "",
                  email: tenant?.email || "",
                  phone: tenant?.phone || "",
                  address: tenant?.address || "",
                  description: tenant?.description || "",
                  logo_url: tenant?.logo_url || "",
                  brand_color: tenant?.brand_color || "#6366f1",
                  bank_name: tenant?.bank_account?.bank_name || "",
                  account_name: tenant?.bank_account?.account_name || "",
                  account_number: tenant?.bank_account?.account_number || "",
                });
              }}
              disabled={isSaving}
            >
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Spinner size="sm" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        )}
      </Card>

      {/* Branding */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-6">Branding</h2>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleLogoUpload}
          style={{ display: "none" }}
        />

        <div className="space-y-4">
          {/* Logo */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <ImageIcon size={16} className="inline mr-2" />
              Logo
            </label>
            {formData.logo_url ? (
              <div className="flex items-center gap-4">
                <img
                  src={formData.logo_url}
                  alt="Salon logo"
                  className="w-20 h-20 object-cover rounded-lg border border-[var(--border)]"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogoClick}
                  disabled={isUploading}
                >
                  {isUploading ? (
                    <>
                      <Spinner size="sm" />
                      Uploading...
                    </>
                  ) : (
                    "Change Logo"
                  )}
                </Button>
              </div>
            ) : (
              <div className="border-2 border-dashed border-[var(--border)] rounded-lg p-8 text-center">
                <ImageIcon
                  size={48}
                  className="mx-auto text-muted-foreground mb-2"
                />
                <p className="text-sm text-muted-foreground mb-3">
                  No logo uploaded
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogoClick}
                  disabled={isUploading}
                >
                  {isUploading ? (
                    <>
                      <Spinner size="sm" />
                      Uploading...
                    </>
                  ) : (
                    "Upload Logo"
                  )}
                </Button>
              </div>
            )}
            <p className="text-xs text-muted-foreground mt-2">
              Recommended: Square image (500x500px), PNG or JPG, max 2MB
            </p>
          </div>

          {/* Brand Color */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Brand Color
            </label>
            <div className="flex items-center gap-3">
              <input
                type="color"
                value={formData.brand_color}
                onChange={(e) =>
                  setFormData({ ...formData, brand_color: e.target.value })
                }
                disabled={!isEditing}
                className="w-16 h-10 rounded border border-[var(--border)] cursor-pointer"
              />
              <Input
                value={formData.brand_color}
                onChange={(e) =>
                  setFormData({ ...formData, brand_color: e.target.value })
                }
                disabled={!isEditing}
                placeholder="#6366f1"
                className="flex-1"
              />
            </div>
          </div>

          {/* Subdomain (Read-only) */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Booking Page URL
            </label>
            <div className="flex gap-2">
              <Input
                value={
                  tenant?.subdomain ? `/book/${tenant.subdomain}` : "Loading..."
                }
                disabled
                className="flex-1"
              />
              {tenant?.subdomain && (
                <Link to={`/book/${tenant.subdomain}`} target="_blank">
                  <Button variant="outline" size="sm">
                    Visit
                  </Button>
                </Link>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              This is your public booking page URL
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
