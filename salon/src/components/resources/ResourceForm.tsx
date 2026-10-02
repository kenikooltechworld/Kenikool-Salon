import { useState, useEffect } from "react";
import {
  useCreateResource,
  useUpdateResource,
  useResource,
} from "@/hooks/useResources";
import { AlertCircle, CheckCircle } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface ResourceFormProps {
  resourceId?: string;
  onSuccess?: () => void;
}

export default function ResourceForm({
  resourceId,
  onSuccess,
}: ResourceFormProps) {
  const [formData, setFormData] = useState<{
    name: string;
    type: "room" | "chair" | "equipment" | "tool" | "supply";
    description: string;
    quantity: number;
    status: "active" | "inactive" | "maintenance";
    location_id: string;
    tags: string;
    notes: string;
  }>({
    name: "",
    type: "room",
    description: "",
    quantity: 1,
    status: "active",
    location_id: "",
    tags: "",
    notes: "",
  });

  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: existingResource } = useResource(resourceId || "");
  const createResource = useCreateResource();
  const updateResource = useUpdateResource();

  useEffect(() => {
    if (existingResource) {
      setFormData({
        name: existingResource.name,
        type: existingResource.type,
        description: existingResource.description || "",
        quantity: existingResource.quantity,
        status: existingResource.status,
        location_id: existingResource.location_id || "",
        tags: existingResource.tags.join(", "),
        notes: existingResource.notes || "",
      });
    }
  }, [existingResource]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "quantity" ? parseInt(value) : value,
    }));
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim()) {
      setError("Resource name is required");
      return;
    }

    if (formData.quantity < 1) {
      setError("Quantity must be at least 1");
      return;
    }

    const payload = {
      name: formData.name,
      type: formData.type,
      description: formData.description || undefined,
      quantity: formData.quantity,
      status: formData.status,
      location_id: formData.location_id || undefined,
      tags: formData.tags
        .split(",")
        .map((t) => t.trim())
        .filter((t) => t),
      notes: formData.notes || undefined,
    };

    if (resourceId) {
      updateResource.mutate(
        { id: resourceId, data: payload },
        {
          onSuccess: () => {
            setShowSuccess(true);
            setTimeout(() => {
              setShowSuccess(false);
              onSuccess?.();
            }, 2000);
          },
          onError: (err: any) => {
            setError(err.response?.data?.detail || "Failed to update resource");
          },
        },
      );
    } else {
      createResource.mutate(payload, {
        onSuccess: () => {
          setShowSuccess(true);
          setFormData({
            name: "",
            type: "room",
            description: "",
            quantity: 1,
            status: "active",
            location_id: "",
            tags: "",
            notes: "",
          });
          setTimeout(() => {
            setShowSuccess(false);
            onSuccess?.();
          }, 2000);
        },
        onError: (err: any) => {
          setError(err.response?.data?.detail || "Failed to create resource");
        },
      });
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-2xl mx-auto p-4 sm:p-6 bg-background rounded-lg border border-border"
    >
      <h2 className="text-xl sm:text-2xl font-bold text-foreground mb-4 sm:mb-6">
        {resourceId ? "Edit Resource" : "Create Resource"}
      </h2>

      {showSuccess && (
        <div className="mb-3 sm:mb-4 p-3 sm:p-4 bg-success/10 border border-success/20 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-success shrink-0 mt-0.5" />
          <p className="text-sm text-success-foreground">
            Resource {resourceId ? "updated" : "created"} successfully!
          </p>
        </div>
      )}

      {error && (
        <div className="mb-3 sm:mb-4 p-3 sm:p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-destructive shrink-0 mt-0.5" />
          <p className="text-sm text-destructive-foreground">{error}</p>
        </div>
      )}

      <div className="space-y-3 sm:space-y-4">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Resource Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Treatment Room A"
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          />
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Type *
          </label>
          <select
            name="type"
            value={formData.type}
            onChange={handleChange}
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          >
            <option value="room">Room</option>
            <option value="chair">Chair</option>
            <option value="equipment">Equipment</option>
            <option value="tool">Tool</option>
            <option value="supply">Supply</option>
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Status *
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Location ID
          </label>
          <input
            type="text"
            name="location_id"
            value={formData.location_id}
            onChange={handleChange}
            placeholder="e.g., location-123"
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter resource description"
            rows={3}
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          />
        </div>

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Quantity *
          </label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            min="1"
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            name="tags"
            value={formData.tags}
            onChange={handleChange}
            placeholder="e.g., premium, new, high-priority"
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          />
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Notes
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Additional notes about this resource"
            rows={2}
            className={cn(
              "w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
            )}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={createResource.isPending || updateResource.isPending}
          className={cn(
            "w-full px-4 py-3 rounded-lg font-semibold transition-colors",
            createResource.isPending || updateResource.isPending
              ? "bg-muted text-muted-foreground cursor-not-allowed"
              : "bg-primary text-primary-foreground hover:bg-primary/90",
          )}
        >
          {createResource.isPending || updateResource.isPending
            ? "Saving..."
            : resourceId
              ? "Update Resource"
              : "Create Resource"}
        </button>
      </div>
    </form>
  );
}
