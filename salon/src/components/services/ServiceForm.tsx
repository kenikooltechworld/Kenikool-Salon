import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/components/ui/toast";
import { PlusIcon, XIcon } from "@/components/icons";
import { Progress } from "@/components/ui/progress";
import { useCreateService, useUpdateService } from "@/hooks/useServices";
import { useServiceCategories } from "@/hooks/useServiceCategories";
import { ServiceCategoryModal } from "@/components/services/ServiceCategoryModal";
import { ColorPicker } from "@/components/services/ColorPicker";
import { IconPicker } from "@/components/services/IconPicker";
import { useImageUpload } from "@/hooks/useImageUpload";
import { StaffMultiSelect } from "@/components/services/StaffMultiSelect";
import type { Service } from "@/types/service";

interface ServiceFormProps {
  service?: Service;
  existingServices?: Service[];
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function ServiceForm({
  service,
  existingServices = [],
  onSuccess,
  onCancel,
}: ServiceFormProps) {
  const { showToast } = useToast();
  const isEditing = !!service?.id;
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: service?.name || "",
    description: service?.description || "",
    duration_minutes: service?.duration_minutes || 30,
    price: service?.price || 0,
    category: service?.category || "",
    color: service?.color || "#3B82F6",
    icon: service?.icon || "Scissors",
    public_image_url: service?.public_image_url || "",
    is_active: service?.is_active ?? true,
    is_published: service?.is_published ?? false,
    staff_ids: service?.staff_ids || [],
  });

  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const formDataRef = useRef(formData);
  const { data: categories = [] } = useServiceCategories();
  const { mutate: createService, isPending: isCreating } = useCreateService();
  const { mutate: updateService, isPending: isUpdating } = useUpdateService();
  const imageUpload = useImageUpload({ folder: "salon-services" });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? (e.target as HTMLInputElement).checked
          : name === "price" || name === "duration_minutes"
            ? Number(value)
            : value,
    }));
  };

  const handleImageChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = imageUpload.handleFileChange(e);
    if (!file) return;

    setUploadError(null);
    try {
      const url = await imageUpload.uploadImage(file);
      setFormData((prev) => ({
        ...prev,
        public_image_url: url,
      }));
      showToast({
        variant: "success",
        title: "Success",
        description: "Service image uploaded successfully",
      });
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to upload service image";
      setUploadError(errorMsg);
      showToast({
        variant: "error",
        title: "Error",
        description: errorMsg,
      });
    }
  };

  const handleRemoveImage = () => {
    imageUpload.clearPreview();
    setFormData((prev) => ({
      ...prev,
      public_image_url: "",
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadError(null);

    if (!service) {
      const isDuplicate = existingServices.some(
        (s: Service) => s.name.toLowerCase() === formData.name.toLowerCase(),
      );

      if (isDuplicate) {
        showToast({
          variant: "error",
          title: "Duplicate Service",
          description: `A service named "${formData.name}" already exists. Please use a different name.`,
        });
        return;
      }
    }

    try {
      const submitData = {
        ...formData,
        public_image_url: formData.public_image_url,
      };

      if (service) {
        updateService(
          {
            id: service.id,
            ...submitData,
          },
          {
            onSuccess: (updatedService: any) => {
              showToast({
                variant: "success",
                title: "Success",
                description: `${updatedService.name || "Service"} has been updated successfully`,
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
                    : "Failed to update service",
              });
            },
          },
        );
      } else {
        createService(submitData as any, {
          onSuccess: (newService: any) => {
            showToast({
              variant: "success",
              title: "Success",
              description: `${newService.name || "Service"} has been created successfully`,
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
                  : "Failed to create service",
            });
          },
        });
      }
    } catch (error) {
      setUploadError(
        error instanceof Error ? error.message : "Failed to process image",
      );
    }
  };

  const isPending = isCreating || isUpdating || imageUpload.isUploading;

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-sm font-medium text-foreground">
            Service Name
          </label>
          <Input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Haircut"
            required
            className="mt-1"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-foreground">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Service description"
            rows={3}
            className="w-full mt-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-foreground">
            Service Image
          </label>
          <div className="mt-2 space-y-2">
            {(imageUpload.error || uploadError) && (
              <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-lg text-sm text-destructive">
                {imageUpload.error || uploadError}
              </div>
            )}
            {imageUpload.preview && (
              <div className="relative w-full h-40 rounded-lg overflow-hidden border border-border">
                <img
                  src={imageUpload.preview}
                  alt="Service preview"
                  className="w-full h-full object-cover"
                />
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="absolute top-2 right-2 bg-destructive/90 hover:bg-destructive text-white rounded-full p-1 transition"
                  aria-label="Remove image"
                >
                  <XIcon size={14} />
                </button>
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              disabled={imageUpload.isUploading}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
            />
            {imageUpload.isUploading && (
              <Progress
                value={imageUpload.uploadProgress}
                size="md"
                variant="default"
                showPercentage={true}
              />
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-foreground">
                Category
              </label>
              <button
                type="button"
                onClick={() => setShowCategoryModal(true)}
                className="text-xs text-primary hover:text-primary/80 flex items-center gap-1 cursor-pointer"
              >
                <PlusIcon size={14} />
                Add
              </button>
            </div>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">Select a category</option>
              {categories.map((cat: any) => (
                <option key={cat.id} value={cat.name}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-foreground">
              Duration (minutes)
            </label>
            <Input
              type="number"
              name="duration_minutes"
              value={formData.duration_minutes}
              onChange={handleChange}
              min="5"
              step="5"
              required
              className="mt-1"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-foreground">
              Service Color
            </label>
            <div className="mt-1">
              <ColorPicker
                value={formData.color}
                onChange={(color: string) =>
                  setFormData((prev) => ({ ...prev, color }))
                }
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-foreground">
              Service Icon
            </label>
            <div className="mt-1">
              <IconPicker
                value={formData.icon}
                onChange={(icon: string) =>
                  setFormData((prev) => ({ ...prev, icon }))
                }
              />
            </div>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium text-foreground">
            Price (₦)
          </label>
          <Input
            type="number"
            name="price"
            value={formData.price}
            onChange={handleChange}
            min="0"
            step="100"
            required
            className="mt-1"
          />
        </div>

        <StaffMultiSelect
          value={formData.staff_ids}
          onChange={(staff_ids) =>
            setFormData((prev) => ({ ...prev, staff_ids }))
          }
        />

        <div className="space-y-3 border-t border-border pt-4">
          <Checkbox
            id="is_active"
            name="is_active"
            checked={formData.is_active}
            onCheckedChange={(checked) =>
              setFormData((prev) => ({
                ...prev,
                is_active: checked as boolean,
              }))
            }
            label="Active"
          />
          <Checkbox
            id="is_published"
            name="is_published"
            checked={formData.is_published}
            onCheckedChange={(checked) =>
              setFormData((prev) => ({
                ...prev,
                is_published: checked as boolean,
              }))
            }
            label="Published"
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isPending}
            className="flex-1 cursor-pointer"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isPending}
            className="flex-1 cursor-pointer"
          >
            {imageUpload.isUploading
              ? "Uploading..."
              : isPending
                ? "Saving..."
                : service
                  ? "Update Service"
                  : "Create Service"}
          </Button>
        </div>
      </form>

      <ServiceCategoryModal
        isOpen={showCategoryModal}
        onClose={() => setShowCategoryModal(false)}
      />
    </Card>
  );
}
