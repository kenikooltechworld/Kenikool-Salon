/**
 * TemplateSaver Component
 * Allows saving current booking as a template
 * Validates: Requirements 4.3
 */
import React, { useState } from "react";
import { Save, AlertCircle } from "lucide-react";

interface TemplateSaverProps {
  onSave: (data: {
    name: string;
    description: string;
    category: string;
  }) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
  error?: string;
}

/**
 * Component for saving current booking as a template
 */
export const TemplateSaver: React.FC<TemplateSaverProps> = ({
  onSave,
  onCancel,
  loading = false,
  error,
}) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "General",
  });

  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = "Template name is required";
    } else if (formData.name.length < 3) {
      errors.name = "Template name must be at least 3 characters";
    } else if (formData.name.length > 100) {
      errors.name = "Template name must be less than 100 characters";
    }

    if (formData.description.length > 500) {
      errors.description = "Description must be less than 500 characters";
    }

    if (!formData.category.trim()) {
      errors.category = "Category is required";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await onSave(formData);
    } catch (err) {
      // Error is handled by parent component
    }
  };

  const categories = [
    "General",
    "Hair Care",
    "Skin Care",
    "Nail Care",
    "Makeup",
    "Wellness",
    "Other",
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Save as Template</h2>
        <p className="mt-1 text-sm text-gray-600">
          Save this booking as a template for quick reuse in the future
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="flex gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold">Error saving template</h3>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Template Name */}
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-gray-700"
          >
            Template Name *
          </label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleChange("name", e.target.value)}
            disabled={loading}
            placeholder="e.g., Monthly Hair Treatment"
            className={`mt-1 w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-100 ${
              validationErrors.name
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            }`}
          />
          {validationErrors.name && (
            <p className="mt-1 text-sm text-red-600">{validationErrors.name}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            {formData.name.length}/100 characters
          </p>
        </div>

        {/* Description */}
        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700"
          >
            Description
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => handleChange("description", e.target.value)}
            disabled={loading}
            placeholder="Describe what this template includes..."
            rows={3}
            className={`mt-1 w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-100 ${
              validationErrors.description
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            }`}
          />
          {validationErrors.description && (
            <p className="mt-1 text-sm text-red-600">
              {validationErrors.description}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            {formData.description.length}/500 characters
          </p>
        </div>

        {/* Category */}
        <div>
          <label
            htmlFor="category"
            className="block text-sm font-medium text-gray-700"
          >
            Category *
          </label>
          <select
            id="category"
            value={formData.category}
            onChange={(e) => handleChange("category", e.target.value)}
            disabled={loading}
            className={`mt-1 w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-100 ${
              validationErrors.category
                ? "border-red-300 focus:border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            }`}
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          {validationErrors.category && (
            <p className="mt-1 text-sm text-red-600">
              {validationErrors.category}
            </p>
          )}
        </div>
      </form>

      {/* Info Box */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <h4 className="mb-2 font-semibold text-blue-900">Template Benefits</h4>
        <ul className="space-y-1 text-sm text-blue-800">
          <li>• Quickly create similar bookings in the future</li>
          <li>• Maintain consistent service packages</li>
          <li>• Save time on recurring bookings</li>
          <li>• Share templates with your team</li>
        </ul>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading || !formData.name.trim()}
          className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {loading ? "Saving..." : "Save Template"}
        </button>
      </div>
    </div>
  );
};

export default TemplateSaver;
