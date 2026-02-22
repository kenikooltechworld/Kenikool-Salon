"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Select } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";
import { useCreateStylist } from "@/lib/api/hooks/useStylists";
import { UploadIcon } from "@/components/icons";

type CommissionType =
  | "percentage"
  | "fixed_per_service"
  | "daily"
  | "weekly"
  | "monthly";

interface StaffData {
  name: string;
  phone: string;
  bio: string;
  commissionType: CommissionType;
  commissionValue: string;
  photo: string | null;
}

interface StaffSetupProps {
  onComplete: (data: StaffData) => void;
  initialData: StaffData | null;
}

export function StaffSetup({ onComplete, initialData }: StaffSetupProps) {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    name: initialData?.name || "",
    phone: initialData?.phone || "",
    bio: initialData?.bio || "",
    commissionType: (initialData?.commissionType ||
      "percentage") as CommissionType,
    commissionValue: initialData?.commissionValue || "",
    photo: initialData?.photo || null,
  });
  const [error, setError] = useState("");
  const [photoPreview, setPhotoPreview] = useState<string | null>(
    initialData?.photo || null
  );
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const commissionTypeOptions = [
    { value: "percentage", label: "Percentage per service (%)" },
    { value: "fixed_per_service", label: "Fixed amount per service (₦)" },
    { value: "daily", label: "Daily salary (₦)" },
    { value: "weekly", label: "Weekly salary (₦)" },
    { value: "monthly", label: "Monthly salary (₦)" },
  ];

  const getCommissionLabel = () => {
    switch (formData.commissionType) {
      case "percentage":
        return "Commission Percentage";
      case "fixed_per_service":
        return "Amount per Service";
      case "daily":
        return "Daily Salary";
      case "weekly":
        return "Weekly Salary";
      case "monthly":
        return "Monthly Salary";
      default:
        return "Commission Value";
    }
  };

  const getCommissionPlaceholder = () => {
    switch (formData.commissionType) {
      case "percentage":
        return "e.g., 30";
      case "fixed_per_service":
        return "e.g., 500";
      case "daily":
        return "e.g., 5000";
      case "weekly":
        return "e.g., 25000";
      case "monthly":
        return "e.g., 100000";
      default:
        return "Enter amount";
    }
  };

  const getCommissionSuffix = () => {
    return formData.commissionType === "percentage" ? "%" : "₦";
  };

  const { mutate: createStaff, isPending: loading } = useCreateStylist();

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      showToast({
        title: "File Too Large",
        description: "Maximum file size is 5MB",
        variant: "error",
      });
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const uploadFormData = new FormData();
      uploadFormData.append("file", file);

      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          const percentComplete = Math.round((e.loaded * 100) / e.total);
          setUploadProgress(percentComplete);
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            setPhotoPreview(data.url);
            setFormData({ ...formData, photo: data.url });
            showToast({
              title: "Photo Uploaded",
              description: "Staff photo uploaded successfully",
              variant: "success",
            });
          } catch (err) {
            throw new Error("Failed to parse response");
          }
        } else {
          throw new Error("Failed to upload photo");
        }
        setUploading(false);
        setUploadProgress(0);
      });

      xhr.addEventListener("error", () => {
        showToast({
          title: "Upload Failed",
          description: "Network error uploading photo",
          variant: "error",
        });
        setUploading(false);
        setUploadProgress(0);
      });

      xhr.open("POST", "http://localhost:8000/upload/service-photo");
      xhr.send(uploadFormData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Upload failed";
      showToast({
        title: "Upload Failed",
        description: errorMessage,
        variant: "error",
      });
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.name) {
      setError("Please enter staff member name");
      return;
    }

    if (!formData.phone) {
      setError("Please enter staff member phone number");
      return;
    }

    if (formData.phone.length < 10) {
      setError("Phone number must be at least 10 characters");
      return;
    }

    createStaff(
      {
        name: formData.name,
        phone: formData.phone,
        bio: formData.bio,
        commission_type:
          formData.commissionType === "percentage" ? "percentage" : "fixed",
        commission_value: formData.commissionValue
          ? parseFloat(formData.commissionValue)
          : 0,
      },
      {
        onSuccess: () => {
          showToast({
            title: "Staff Added",
            description: `${formData.name} has been added to your team`,
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
          Add Your First Team Member
        </h2>
        <p className="text-[var(--muted-foreground)]">
          Add a stylist or staff member to your salon
        </p>
      </div>

      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}

      {/* Photo Upload */}
      <div>
        <Label>Staff Photo</Label>
        <div className="mt-2 flex items-center gap-4">
          <div className="relative">
            {photoPreview ? (
              <img
                src={photoPreview}
                alt="Staff preview"
                className="w-24 h-24 object-cover rounded-full border-2 border-[var(--border)]"
              />
            ) : (
              <div className="w-24 h-24 bg-[var(--muted)] rounded-full flex items-center justify-center border-2 border-dashed border-[var(--border)]">
                <UploadIcon
                  size={32}
                  className="text-[var(--muted-foreground)]"
                />
              </div>
            )}
            {uploading && (
              <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center">
                <div className="text-white text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-1"></div>
                  <span className="text-xs font-bold">{uploadProgress}%</span>
                </div>
              </div>
            )}
          </div>
          <div className="flex-1">
            <input
              type="file"
              accept="image/*"
              onChange={handlePhotoUpload}
              className="hidden"
              id="staff-photo-upload"
              disabled={uploading}
            />
            <Button
              type="button"
              variant="outline"
              onClick={() =>
                document.getElementById("staff-photo-upload")?.click()
              }
              disabled={uploading}
            >
              {uploading ? `Uploading... ${uploadProgress}%` : "Upload Photo"}
            </Button>
            {uploading && (
              <div className="mt-2">
                <div className="w-full bg-[var(--muted)] rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-[var(--primary)] h-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
            <p className="text-xs text-[var(--muted-foreground)] mt-1">
              PNG, JPG up to 5MB
            </p>
          </div>
        </div>
      </div>

      {/* Staff Name */}
      <div>
        <Label htmlFor="name" required>
          Full Name
        </Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="e.g., Jane Doe"
          disabled={loading}
          className="mt-2"
        />
      </div>

      {/* Phone Number */}
      <div>
        <Label htmlFor="phone" required>
          Phone Number
        </Label>
        <Input
          id="phone"
          type="tel"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          placeholder="e.g., 08012345678"
          disabled={loading}
          className="mt-2"
        />
        <p className="text-xs text-[var(--muted-foreground)] mt-1">
          Staff member&apos;s contact number
        </p>
      </div>

      {/* Bio */}
      <div>
        <Label htmlFor="bio">Bio</Label>
        <Textarea
          id="bio"
          value={formData.bio}
          onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
          placeholder="Tell clients about this team member..."
          rows={3}
          disabled={loading}
          className="mt-2"
        />
      </div>

      {/* Commission Structure */}
      <div className="space-y-4">
        <div>
          <Label htmlFor="commissionType">Commission Type</Label>
          <Select
            id="commissionType"
            value={formData.commissionType}
            onChange={(e) =>
              setFormData({
                ...formData,
                commissionType: e.target.value as CommissionType,
              })
            }
            disabled={loading}
            className="mt-2"
          >
            {commissionTypeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
          <p className="text-xs text-[var(--muted-foreground)] mt-1">
            Choose how this staff member will be compensated
          </p>
        </div>

        <div>
          <Label htmlFor="commissionValue">{getCommissionLabel()}</Label>
          <div className="relative mt-2">
            <Input
              id="commissionValue"
              type="number"
              value={formData.commissionValue}
              onChange={(e) =>
                setFormData({ ...formData, commissionValue: e.target.value })
              }
              placeholder={getCommissionPlaceholder()}
              min="0"
              max={formData.commissionType === "percentage" ? "100" : undefined}
              disabled={loading}
              className="pr-12"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--muted-foreground)] font-medium">
              {getCommissionSuffix()}
            </span>
          </div>
          <p className="text-xs text-[var(--muted-foreground)] mt-1">
            {formData.commissionType === "percentage"
              ? "Percentage of each service price"
              : formData.commissionType === "fixed_per_service"
              ? "Fixed amount earned per service completed"
              : "Fixed salary amount"}
          </p>
        </div>
      </div>

      <Button type="submit" fullWidth loading={loading}>
        Continue
      </Button>
    </form>
  );
}
