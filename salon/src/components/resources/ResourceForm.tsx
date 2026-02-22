import { useState, useEffect } from "react";
import {
  useCreateResource,
  useUpdateResource,
  useResource,
} from "@/hooks/useResources";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface ResourceFormProps {
  resourceId?: string;
  onSuccess?: () => void;
}

export default function ResourceForm({
  resourceId,
  onSuccess,
}: ResourceFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    type: "room" as const,
    description: "",
    quantity: 1,
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
      className="max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        {resourceId ? "Edit Resource" : "Create Resource"}
      </h2>

      {showSuccess && (
        <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-800 dark:text-green-200">
            Resource {resourceId ? "updated" : "created"} successfully!
          </p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      <div className="space-y-4">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Resource Name *
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Treatment Room A"
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
            )}
          />
        </div>

        {/* Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Type *
          </label>
          <select
            name="type"
            value={formData.type}
            onChange={handleChange}
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
            )}
          >
            <option value="room">Room</option>
            <option value="chair">Chair</option>
            <option value="equipment">Equipment</option>
            <option value="tool">Tool</option>
            <option value="supply">Supply</option>
          </select>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter resource description"
            rows={3}
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
            )}
          />
        </div>

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quantity *
          </label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            min="1"
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
            )}
          />
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            name="tags"
            value={formData.tags}
            onChange={handleChange}
            placeholder="e.g., premium, new, high-priority"
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
            )}
          />
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Notes
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Additional notes about this resource"
            rows={2}
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
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
              ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700",
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
