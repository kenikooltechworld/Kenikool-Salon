import { useState } from "react";
import {
  useResources,
  useDeleteResource,
  useMarkResourceMaintenance,
} from "@/hooks/useResources";
import { Edit2Icon, Trash2Icon, WrenchIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface ResourceListProps {
  onEdit?: (resourceId: string) => void;
}

export default function ResourceList({ onEdit }: ResourceListProps) {
  const [selectedType, setSelectedType] = useState<string | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>();

  const { data: resources = [], isLoading } = useResources({
    type: selectedType,
    status: selectedStatus,
  });

  const deleteResource = useDeleteResource();
  const markMaintenance = useMarkResourceMaintenance();

  const handleDelete = (resourceId: string) => {
    if (window.confirm("Are you sure you want to delete this resource?")) {
      deleteResource.mutate(resourceId);
    }
  };

  const handleMarkMaintenance = (resourceId: string) => {
    markMaintenance.mutate(resourceId);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200";
      case "inactive":
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
      case "maintenance":
        return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "room":
        return "bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200";
      case "chair":
        return "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200";
      case "equipment":
        return "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200";
      case "tool":
        return "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200";
      case "supply":
        return "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200";
      default:
        return "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200";
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="h-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Type
          </label>
          <select
            value={selectedType || ""}
            onChange={(e) => setSelectedType(e.target.value || undefined)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Types</option>
            <option value="room">Room</option>
            <option value="chair">Chair</option>
            <option value="equipment">Equipment</option>
            <option value="tool">Tool</option>
            <option value="supply">Supply</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Status
          </label>
          <select
            value={selectedStatus || ""}
            onChange={(e) => setSelectedStatus(e.target.value || undefined)}
            className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>
      </div>

      {/* Resources List */}
      {resources.length === 0 ? (
        <div className="p-8 text-center text-gray-500 dark:text-gray-400">
          <p>No resources found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {resources.map((resource) => (
            <div
              key={resource.id}
              className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {resource.name}
                  </h3>
                  <div className="flex gap-2 mt-2">
                    <span
                      className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        getTypeColor(resource.type),
                      )}
                    >
                      {resource.type}
                    </span>
                    <span
                      className={cn(
                        "px-2 py-1 rounded-full text-xs font-medium",
                        getStatusColor(resource.status),
                      )}
                    >
                      {resource.status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
                <p>
                  <span className="font-medium">Quantity:</span>{" "}
                  {resource.available_quantity}/{resource.quantity}
                </p>
                {resource.description && (
                  <p className="text-xs">{resource.description}</p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={() => onEdit?.(resource.id)}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                {resource.status !== "maintenance" && (
                  <button
                    onClick={() => handleMarkMaintenance(resource.id)}
                    disabled={markMaintenance.isPending}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:bg-gray-400 text-sm font-medium"
                  >
                    <Wrench className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(resource.id)}
                  disabled={deleteResource.isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400 text-sm font-medium"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
