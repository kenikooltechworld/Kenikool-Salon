import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  PlusIcon,
  TrashIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";

interface Resource {
  name: string;
  quantity: number;
  unit: string;
}

interface ResourceManagerProps {
  serviceId: string;
  initialResources?: Resource[];
}

export function ResourceManager({
  serviceId,
  initialResources = [],
}: ResourceManagerProps) {
  const [resources, setResources] = useState<Resource[]>(initialResources);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // New resource form state
  const [newResource, setNewResource] = useState<Resource>({
    name: "",
    quantity: 1,
    unit: "",
  });

  const handleAddResource = () => {
    if (!newResource.name || !newResource.unit || newResource.quantity <= 0) {
      setError("Please in all resource fields");
      return;
    }

    setResources([...resources, { ...newResource }]);
    setNewResource({ name: "", quantity: 1, unit: "" });
    setError(null);
  };

  const handleRemoveResource = (index: number) => {
    setResources(resources.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await apiClient.patch(`/api/services/${serviceId}`, {
        required_resources: resources,
      });
      setSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error("Error saving resources:", err);
      setError("Failed to save resources. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setResources(initialResources);
    setIsEditing(false);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-foreground">
            Resource Tracking
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage resources required for this service
          </p>
        </div>
        {!isEditing && (
          <Button
            onClick={() => setIsEditing(true)}
            className="cursor-pointer transition-all duration-200"
          >
            Edit Resources
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      )}

      {success && (
        <Alert variant="success">
          <CheckCircleIcon size={20} />
          <div>
            <h3 className="font-semibold">Success</h3>
            <p className="text-sm">Resources updated successfully</p>
          </div>
        </Alert>
      )}

      <Card className="p-6">
        {resources.length === 0 && !isEditing ? (
          <div className="text-center py-12">
            <AlertTriangleIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No Resources Configured
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Add resources to track inventory usage for this service
            </p>
            <Button
              onClick={() => setIsEditing(true)}
              className="cursor-pointer transition-all duration-200"
            >
              <PlusIcon size={16} />
              Add Resource
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Resource List */}
            {resources.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground">
                  Required Resources
                </h3>
                {resources.map((resource, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-muted rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-foreground">
                        {resource.name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {resource.quantity} {resource.unit}
                      </p>
                    </div>
                    {isEditing && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveResource(index)}
                        className="cursor-pointer transition-all duration-200"
                      >
                        <TrashIcon size={16} />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Add New Resource Form */}
            {isEditing && (
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-semibold text-foreground mb-3">
                  Add New Resource
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Resource Name
                    </label>
                    <Input
                      value={newResource.name}
                      onChange={(e) =>
                        setNewResource({ ...newResource, name: e.target.value })
                      }
                      placeholder="e.g., Shampoo, Conditioner"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Quantity
                    </label>
                    <Input
                      type="number"
                      min="0.01"
                      step="0.01"
                      value={newResource.quantity}
                      onChange={(e) =>
                        setNewResource({
                          ...newResource,
                          quantity: parseFloat(e.target.value) || 0,
                        })
                      }
                      placeholder="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Unit
                    </label>
                    <Input
                      value={newResource.unit}
                      onChange={(e) =>
                        setNewResource({ ...newResource, unit: e.target.value })
                      }
                      placeholder="e.g., ml, oz, units"
                    />
                  </div>
                </div>
                <Button
                  onClick={handleAddResource}
                  className="mt-4 cursor-pointer transition-all duration-200"
                >
                  <PlusIcon size={16} />
                  Add Resource
                </Button>
              </div>
            )}

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex gap-2 pt-4 border-t">
                <Button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="cursor-pointer transition-all duration-200"
                >
                  {isSaving ? (
                    <>
                      <Spinner size="sm" />
                      Saving...
                    </>
                  ) : (
                    "Save Changes"
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="cursor-pointer transition-all duration-200"
                >
                  Cancel
                </Button>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Resource Usage Info */}
      {resources.length > 0 && !isEditing && (
        <Card className="p-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <div className="flex gap-3">
            <AlertTriangleIcon
              size={20}
              className="text-blue-600 flex-shrink-0 mt-0.5"
            />
            <div>
              <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                Resource Tracking
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                These resources will be automatically deducted from inventory
                when a booking is completed. Make sure to maintain adequate
                stock levels to avoid service disruptions.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
