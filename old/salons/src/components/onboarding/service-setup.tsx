"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { useToast } from "@/components/ui/toast";
import { useCreateService } from "@/lib/api/hooks/useServices";
import { UploadIcon } from "@/components/icons";

interface ServiceData {
  name: string;
  category: string;
  price: string;
  duration: string;
  description: string;
  photos: string[];
}

interface ServiceSetupProps {
  onComplete: (data: ServiceData) => void;
  initialData: ServiceData | null;
}

const SERVICE_CATEGORIES = [
  "Haircut",
  "Styling",
  "Coloring",
  "Treatment",
  "Braiding",
  "Nails",
  "Makeup",
  "Spa",
  "Other",
];

export function ServiceSetup({ onComplete, initialData }: ServiceSetupProps) {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    name: initialData?.name || "",
    category: initialData?.category || "",
    price: initialData?.price || "",
    duration: initialData?.duration || "",
    description: initialData?.description || "",
    photos: initialData?.photos || [],
  });
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{
    [key: string]: number;
  }>({});

  const { mutate: createService, isPending: loading } = useCreateService();

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    // Check if adding these files would exceed the limit
    if (formData.photos.length + files.length > 5) {
      showToast({
        title: "Too Many Images",
        description: "You can upload a maximum of 5 images per service",
        variant: "error",
      });
      return;
    }

    setUploading(true);
    setUploadProgress({});

    try {
      const uploadPromises = files.map(async (file) => {
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
          throw new Error(`${file.name} is too large. Maximum size is 5MB`);
        }

        return new Promise<string>((resolve, reject) => {
          const uploadFormData = new FormData();
          uploadFormData.append("file", file);

          const xhr = new XMLHttpRequest();

          // Track upload progress
          xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
              const percentComplete = Math.round((e.loaded * 100) / e.total);
              setUploadProgress((prev) => ({
                ...prev,
                [file.name]: percentComplete,
              }));
            }
          });

          xhr.addEventListener("load", () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                const data = JSON.parse(xhr.responseText);
                resolve(data.url);
              } catch {
                reject(new Error(`Failed to parse response for ${file.name}`));
              }
            } else {
              reject(new Error(`Failed to upload ${file.name}`));
            }
          });

          xhr.addEventListener("error", () => {
            reject(new Error(`Network error uploading ${file.name}`));
          });

          // Get auth token
          const token =
            localStorage.getItem("access_token") ||
            sessionStorage.getItem("access_token");

          // Use the correct API URL
          const apiUrl =
            import.meta.env.VITE_API_URL || "http://localhost:8000";
          xhr.open("POST", `${apiUrl}/api/upload/service-photo`);

          if (token) {
            xhr.setRequestHeader("Authorization", `Bearer ${token}`);
          }

          xhr.send(uploadFormData);
        });
      });

      const uploadedUrls = await Promise.all(uploadPromises);

      setFormData((prev) => ({
        ...prev,
        photos: [...prev.photos, ...uploadedUrls],
      }));

      showToast({
        title: "Images Uploaded",
        description: `${uploadedUrls.length} image(s) uploaded successfully`,
        variant: "success",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Upload failed";
      showToast({
        title: "Upload Failed",
        description: errorMessage,
        variant: "error",
      });
    } finally {
      setUploading(false);
      setUploadProgress({});
    }
  };

  const handleRemovePhoto = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      photos: prev.photos.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (
      !formData.name ||
      !formData.category ||
      !formData.price ||
      !formData.duration
    ) {
      setError("Please fill in all required fields");
      return;
    }

    createService(
      {
        name: formData.name,
        category: formData.category,
        price: parseFloat(formData.price),
        duration_minutes: parseInt(formData.duration),
        description: formData.description,
      },
      {
        onSuccess: () => {
          showToast({
            title: "Service Created",
            description: `${formData.name} has been added`,
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
      },
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-2">
          Add Your First Service
        </h2>
        <p className="text-[var(--muted-foreground)]">
          Create a service that clients can book
        </p>
      </div>

      {error && (
        <Alert variant="error" className="mb-4">
          {error}
        </Alert>
      )}

      {/* Photo Upload */}
      <div>
        <Label>Service Photos (up to 5)</Label>
        <div className="mt-2 space-y-4">
          {/* Photo Grid */}
          {formData.photos.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {formData.photos.map((photo, index) => (
                <div key={index} className="relative group">
                  <img
                    src={photo}
                    alt={`Service photo ${index + 1}`}
                    className="w-full h-24 object-cover rounded-lg border-2 border-[var(--border)]"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemovePhoto(index)}
                    className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Upload Button */}
          {formData.photos.length < 5 && (
            <div>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handlePhotoUpload}
                className="hidden"
                id="photo-upload"
                disabled={uploading}
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => document.getElementById("photo-upload")?.click()}
                disabled={uploading}
                fullWidth
              >
                {uploading ? (
                  "Uploading..."
                ) : (
                  <>
                    <UploadIcon size={16} className="mr-2" />
                    Upload Photos ({formData.photos.length}/5)
                  </>
                )}
              </Button>

              {/* Progress Indicators */}
              {uploading && Object.keys(uploadProgress).length > 0 && (
                <div className="mt-3 space-y-2">
                  {Object.entries(uploadProgress).map(
                    ([fileName, progress]) => (
                      <div key={fileName} className="space-y-1">
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-[var(--muted-foreground)] truncate max-w-[200px]">
                            {fileName}
                          </span>
                          <span className="font-semibold text-[var(--foreground)]">
                            {progress}%
                          </span>
                        </div>
                        <div className="w-full bg-[var(--muted)] rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-[var(--primary)] h-full transition-all duration-300 ease-out"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}

              <p className="text-xs text-[var(--muted-foreground)] mt-1">
                PNG, JPG up to 5MB each. You can select multiple files at once.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Service Name */}
      <div>
        <Label htmlFor="name" required>
          Service Name
        </Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="e.g., Women's Haircut"
          disabled={loading}
          className="mt-2"
        />
      </div>

      {/* Category */}
      <div>
        <Label htmlFor="category" required>
          Category
        </Label>
        <Select
          id="category"
          value={formData.category}
          onChange={(e) =>
            setFormData({ ...formData, category: e.target.value })
          }
          disabled={loading}
          className="mt-2"
        >
          <option value="">Select a category</option>
          {SERVICE_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </Select>
      </div>

      {/* Price and Duration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="price" required>
            Price (₦)
          </Label>
          <Input
            id="price"
            type="number"
            value={formData.price}
            onChange={(e) =>
              setFormData({ ...formData, price: e.target.value })
            }
            placeholder="5000"
            disabled={loading}
            className="mt-2"
          />
        </div>
        <div>
          <Label htmlFor="duration" required>
            Duration (minutes)
          </Label>
          <Input
            id="duration"
            type="number"
            value={formData.duration}
            onChange={(e) =>
              setFormData({ ...formData, duration: e.target.value })
            }
            placeholder="60"
            disabled={loading}
            className="mt-2"
          />
        </div>
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
          placeholder="Describe this service..."
          rows={3}
          disabled={loading}
          className="mt-2"
        />
      </div>

      <Button type="submit" fullWidth loading={loading}>
        Continue
      </Button>
    </form>
  );
}
