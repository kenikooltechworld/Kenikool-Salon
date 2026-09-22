import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/components/ui/toast";
import { SaveIcon, XIcon, UploadIcon } from "@/components/icons";
import { useCreateServiceAddon, useUpdateServiceAddon } from "@/hooks/useServiceAddonsAdmin";
import { useImageUpload } from "@/hooks/useImageUpload";
import type { ServiceAddon } from "@/hooks/useServiceAddons";

interface ServiceAddonFormProps {
  addon?: ServiceAddon;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ServiceAddonForm({
  addon,
  onSuccess,
  onCancel,
}: ServiceAddonFormProps) {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    name: addon?.name || "",
    description: addon?.description || "",
    price: addon?.price || 0,
    duration_minutes: addon?.duration_minutes || 15,
    category: addon?.category || "product" as "product" | "upgrade" | "treatment",
    image_url: addon?.image_url || "",
    display_order: addon?.display_order || 1,
    is_active: addon?.is_active ?? true,
  });

  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const { mutate: createAddon, isPending: isCreating } = useCreateServiceAddon();
  const { mutate: updateAddon, isPending: isUpdating } = useUpdateServiceAddon();
  const { uploadImage } = useImageUpload();

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      setUploadError("Please select an image file");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError("Image size must be less than 5MB");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const imageUrl = await uploadImage(file, "service-addons");
      handleInputChange("image_url", imageUrl);
      showToast({
        variant: "success",
        title: "Success",
        description: "Image uploaded successfully",
      });
    } catch (error) {
      console.error("Upload error:", error);
      setUploadError("Failed to upload image. Please try again.");
      showToast({
        variant: "error",
        title: "Upload failed",
        description: "Failed to upload image. Please try again.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      showToast({
        variant: "error",
        title: "Validation Error",
        description: "Name is required",
      });
      return;
    }

    if (!formData.description.trim()) {
      showToast({
        variant: "error",
        title: "Validation Error",
        description: "Description is required",
      });
      return;
    }

    if (formData.price <= 0) {
      showToast({
        variant: "error",
        title: "Validation Error",
        description: "Price must be greater than 0",
      });
      return;
    }

    if (formData.duration_minutes <= 0) {
      showToast({
        variant: "error",
        title: "Validation Error",
        description: "Duration must be greater than 0",
      });
      return;
    }

    const submitData = {
      ...formData,
      name: formData.name.trim(),
      description: formData.description.trim(),
    };

    if (addon) {
      // Update existing addon
      updateAddon(
        { id: addon.id, ...submitData },
        {
          onSuccess: () => {
            showToast({
              variant: "success",
              title: "Success",
              description: "Service add-on updated successfully",
            });
            onSuccess?.();
          },
          onError: (error: any) => {
            showToast({
              variant: "error",
              title: "Error",
              description:
                error instanceof Error
                  ? error.message
                  : "Failed to update service add-on",
            });
          },
        }
      );
    } else {
      // Create new addon
      createAddon(submitData, {
        onSuccess: () => {
          showToast({
            variant: "success",
            title: "Success",
            description: "Service add-on created successfully",
          });
          onSuccess?.();
        },
        onError: (error: any) => {
          showToast({
            variant: "error",
            title: "Error",
            description:
              error instanceof Error
                ? error.message
                : "Failed to create service add-on",
          });
        },
      });
    }
  };

  const isSubmitting = isCreating || isUpdating;

  return (
    <Card className="w-full">
      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            {addon ? "Edit Service Add-on" : "Create Service Add-on"}
          </h3>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            className="p-2"
          >
            <XIcon size={16} />
          </Button>
        </div>

        {/* Basic Information */}
        <div className="space-y-4">
          <h4 className="font-medium text-foreground">Basic Information</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Name <span className="text-destructive">*</span>
              </label>
              <Input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="e.g., Hair Mask Treatment"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Category <span className="text-destructive">*</span>
              </label>
              <select
                value={formData.category}
                onChange={(e) => handleInputChange("category", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                required
              >
                <option value="product">Product</option>
                <option value="upgrade">Upgrade</option>
                <option value="treatment">Treatment</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Description <span className="text-destructive">*</span>
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange("description", e.target.value)}
              placeholder="Describe what this add-on includes..."
              rows={3}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              required
            />
          </div>
        </div>

        {/* Pricing & Duration */}
        <div className="space-y-4">
          <h4 className="font-medium text-foreground">Pricing & Duration</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Price (₦) <span className="text-destructive">*</span>
              </label>
              <Input
                type="number"
                min="0"
                step="0.01"
                value={formData.price}
                onChange={(e) => handleInputChange("price", parseFloat(e.target.value) || 0)}
                placeholder="0.00"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Duration (minutes) <span className="text-destructive">*</span>
              </label>
              <Input
                type="number"
                min="1"
                value={formData.duration_minutes}
                onChange={(e) => handleInputChange("duration_minutes", parseInt(e.target.value) || 0)}
                placeholder="15"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Display Order
              </label>
              <Input
                type="number"
                min="1"
                value={formData.display_order}
                onChange={(e) => handleInputChange("display_order", parseInt(e.target.value) || 1)}
                placeholder="1"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Lower numbers appear first
              </p>
            </div>
          </div>
        </div>

        {/* Image Upload */}
        <div className="space-y-4">
          <h4 className="font-medium text-foreground">Image</h4>
          
          <div className="space-y-4">
            {formData.image_url && (
              <div className="flex items-center gap-4">
                <img
                  src={formData.image_url}
                  alt="Preview"
                  className="w-20 h-20 object-cover rounded-lg border border-border"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handleInputChange("image_url", "")}
                >
                  Remove Image
                </Button>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">
                Upload Image
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={isUploading}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className={`
                    inline-flex items-center gap-2 px-4 py-2 border border-border rounded-lg 
                    bg-background hover:bg-muted cursor-pointer transition
                    ${isUploading ? "opacity-50 cursor-not-allowed" : ""}
                  `}
                >
                  <UploadIcon size={16} />
                  {isUploading ? "Uploading..." : "Choose Image"}
                </label>
              </div>
              {uploadError && (
                <p className="text-sm text-destructive mt-1">{uploadError}</p>
              )}
              <p className="text-xs text-muted-foreground mt-1">
                Recommended: 400x300px, max 5MB
              </p>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="space-y-4">
          <h4 className="font-medium text-foreground">Status</h4>
          
          <div className="flex items-center space-x-2">
            <Checkbox
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={(checked) => handleInputChange("is_active", checked)}
            />
            <label
              htmlFor="is_active"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Active (customers can select this add-on)
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-6 border-t border-border">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting}
            className="gap-2"
          >
            <SaveIcon size={16} />
            {isSubmitting 
              ? (addon ? "Updating..." : "Creating...") 
              : (addon ? "Update Add-on" : "Create Add-on")
            }
          </Button>
        </div>
      </form>
    </Card>
  );
}