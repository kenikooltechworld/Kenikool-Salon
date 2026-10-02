import { useState } from "react";
import {
  useResources,
  useDeleteResource,
  useMarkResourceMaintenance,
} from "@/hooks/useResources";
import { Edit, Trash2, WrenchIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";
import { Skeleton } from "@/components/ui/skeleton";

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
        return "bg-success text-success-foreground";
      case "inactive":
        return "bg-muted text-muted-foreground";
      case "maintenance":
        return "bg-warning text-warning-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "room":
        return "bg-info text-info-foreground";
      case "chair":
        return "bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200";
      case "equipment":
        return "bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200";
      case "tool":
        return "bg-destructive text-destructive-foreground";
      case "supply":
        return "bg-success text-success-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Type
          </label>
          <select
            value={selectedType || ""}
            onChange={(e) => setSelectedType(e.target.value || undefined)}
            className="px-3 py-2 rounded-lg border border-border bg-background text-foreground"
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
          <label className="block text-sm font-medium text-foreground mb-2">
            Status
          </label>
          <select
            value={selectedStatus || ""}
            onChange={(e) => setSelectedStatus(e.target.value || undefined)}
            className="px-3 py-2 rounded-lg border border-border bg-background text-foreground"
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
        <div className="p-8 text-center text-muted-foreground">
          <p>No resources found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {resources.map((resource) => (
            <div
              key={resource.id}
              className="p-4 bg-background rounded-lg border border-border"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground">
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
              <div className="space-y-2 mb-4 text-sm text-muted-foreground">
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
                  <Edit className="w-4 h-4" />
                  Edit
                </button>
                {resource.status !== "maintenance" && (
                  <button
                    onClick={() => handleMarkMaintenance(resource.id)}
                    disabled={markMaintenance.isPending}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:bg-muted text-sm font-medium"
                  >
                    <WrenchIcon className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(resource.id)}
                  disabled={deleteResource.isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-muted text-sm font-medium"
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
