/**
 * TemplateManager Component
 * Displays saved templates with creation date and usage count, handles deletion
 * Validates: Requirements 4.4, 4.5
 */
import React, { useState } from "react";
import {
  Trash2,
  Clock,
  DollarSign,
  AlertCircle,
  MoreVertical,
} from "lucide-react";
import type { BookingTemplate } from "../../lib/api/hooks/useBookingTemplates";

interface TemplateManagerProps {
  templates: BookingTemplate[];
  onDelete: (templateId: string) => Promise<void>;
  onEdit?: (template: BookingTemplate) => void;
  loading?: boolean;
  error?: string;
}

/**
 * Component for managing saved booking templates
 */
export const TemplateManager: React.FC<TemplateManagerProps> = ({
  templates,
  onDelete,
  onEdit,
  loading = false,
  error,
}) => {
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  const handleDeleteClick = (templateId: string) => {
    setDeleteConfirm(templateId);
    setOpenMenu(null);
  };

  const handleConfirmDelete = async (templateId: string) => {
    setDeleting(templateId);
    try {
      await onDelete(templateId);
      setDeleteConfirm(null);
    } finally {
      setDeleting(null);
    }
  };

  const handleCancelDelete = () => {
    setDeleteConfirm(null);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (templates.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 font-semibold text-gray-900">No saved templates</h3>
        <p className="mt-1 text-sm text-gray-600">
          Create your first template by saving a booking
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Error Alert */}
      {error && (
        <div className="flex gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold">Error managing templates</h3>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Templates List */}
      <div className="space-y-3">
        {templates.map((template) => (
          <div
            key={template.id}
            className="rounded-lg border border-gray-200 bg-white p-4 hover:shadow-md transition-shadow"
          >
            {/* Delete Confirmation Dialog */}
            {deleteConfirm === template.id && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4">
                <h4 className="font-semibold text-red-900">Delete template?</h4>
                <p className="mt-1 text-sm text-red-800">
                  Are you sure you want to delete "{template.name}"? This action
                  cannot be undone.
                </p>
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={handleCancelDelete}
                    disabled={deleting === template.id}
                    className="flex-1 rounded-lg border border-red-300 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleConfirmDelete(template.id)}
                    disabled={deleting === template.id}
                    className="flex-1 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                  >
                    {deleting === template.id ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </div>
            )}

            {/* Template Header */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{template.name}</h3>
                <p className="mt-1 text-sm text-gray-600">
                  {template.description}
                </p>
              </div>

              {/* Menu Button */}
              <div className="relative">
                <button
                  onClick={() =>
                    setOpenMenu(openMenu === template.id ? null : template.id)
                  }
                  disabled={loading || deleting === template.id}
                  className="rounded-lg p-2 hover:bg-gray-100 disabled:opacity-50"
                  aria-label="Template options"
                >
                  <MoreVertical className="h-5 w-5 text-gray-600" />
                </button>

                {/* Dropdown Menu */}
                {openMenu === template.id && (
                  <div className="absolute right-0 top-full mt-1 w-48 rounded-lg border border-gray-200 bg-white shadow-lg z-10">
                    {onEdit && (
                      <button
                        onClick={() => {
                          onEdit(template);
                          setOpenMenu(null);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                      >
                        Edit
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteClick(template.id)}
                      className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 last:rounded-b-lg flex items-center gap-2"
                    >
                      <Trash2 className="h-4 w-4" />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Template Details */}
            <div className="mt-3 grid grid-cols-2 gap-3 border-t border-gray-200 pt-3 sm:grid-cols-4">
              <div>
                <p className="text-xs font-medium text-gray-600">Category</p>
                <p className="mt-1 text-sm text-gray-900">
                  {template.category}
                </p>
              </div>

              <div>
                <p className="text-xs font-medium text-gray-600">Duration</p>
                <div className="mt-1 flex items-center gap-1 text-sm text-gray-900">
                  <Clock className="h-4 w-4 text-gray-500" />
                  {template.duration} min
                </div>
              </div>

              <div>
                <p className="text-xs font-medium text-gray-600">Price</p>
                <div className="mt-1 flex items-center gap-1 text-sm text-gray-900">
                  <DollarSign className="h-4 w-4 text-gray-500" />
                  {template.pricing.toFixed(2)}
                </div>
              </div>

              <div>
                <p className="text-xs font-medium text-gray-600">Used</p>
                <p className="mt-1 text-sm text-gray-900">
                  {template.usage_count} times
                </p>
              </div>
            </div>

            {/* Created Date */}
            <div className="mt-3 border-t border-gray-200 pt-3">
              <p className="text-xs text-gray-500">
                Created on {formatDate(template.created_at)}
              </p>
            </div>

            {/* Services Preview */}
            {template.services && template.services.length > 0 && (
              <div className="mt-3 border-t border-gray-200 pt-3">
                <p className="text-xs font-medium text-gray-600">
                  Services ({template.services.length})
                </p>
                <div className="mt-2 space-y-1">
                  {template.services.slice(0, 2).map((service, idx) => (
                    <p key={idx} className="text-xs text-gray-600">
                      • {service.service_name}
                    </p>
                  ))}
                  {template.services.length > 2 && (
                    <p className="text-xs text-gray-500">
                      +{template.services.length - 2} more
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">{templates.length}</span> template(s)
          saved • Total usage:{" "}
          <span className="font-semibold">
            {templates.reduce((sum, t) => sum + t.usage_count, 0)}
          </span>{" "}
          times
        </p>
      </div>
    </div>
  );
};

export default TemplateManager;
