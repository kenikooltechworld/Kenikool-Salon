import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  TrashIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  LinkIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";
import type { Service } from "@/lib/api/types";

interface DependencyManagerProps {
  serviceId: string;
  initialPrerequisites?: string[];
  initialMandatoryAddons?: string[];
}

export function DependencyManager({
  serviceId,
  initialPrerequisites = [],
  initialMandatoryAddons = [],
}: DependencyManagerProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [prerequisites, setPrerequisites] =
    useState<string[]>(initialPrerequisites);
  const [mandatoryAddons, setMandatoryAddons] = useState<string[]>(
    initialMandatoryAddons,
  );
  const [selectedPrerequisite, setSelectedPrerequisite] = useState<string>("");
  const [selectedAddon, setSelectedAddon] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fetch all services for selection
  const { data: servicesData, isLoading: servicesLoading } = useQuery<
    Service[]
  >({
    queryKey: ["services"],
    queryFn: async () => {
      const response = await apiClient.get("/api/services");
      return response.data;
    },
  });

  const availableServices =
    servicesData?.filter((s) => s.id !== serviceId && s.is_active) || [];

  const handleAddPrerequisite = () => {
    if (!selectedPrerequisite) return;
    if (prerequisites.includes(selectedPrerequisite)) {
      setError("This service is already a prerequisite");
      return;
    }
    setPrerequisites([...prerequisites, selectedPrerequisite]);
    setSelectedPrerequisite("");
    setError(null);
  };

  const handleRemovePrerequisite = (id: string) => {
    setPrerequisites(prerequisites.filter((p) => p !== id));
  };

  const handleAddAddon = () => {
    if (!selectedAddon) return;
    if (mandatoryAddons.includes(selectedAddon)) {
      setError("This service is already a mandatory addon");
      return;
    }
    setMandatoryAddons([...mandatoryAddons, selectedAddon]);
    setSelectedAddon("");
    setError(null);
  };

  const handleRemoveAddon = (id: string) => {
    setMandatoryAddons(mandatoryAddons.filter((a) => a !== id));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.patch(`/api/services/${serviceId}`, {
        prerequisite_services: prerequisites,
        mandatory_addons: mandatoryAddons,
      });

      setSuccess("Dependencies updated successfully");
      setIsEditing(false);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to update dependencies");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setPrerequisites(initialPrerequisites);
    setMandatoryAddons(initialMandatoryAddons);
    setIsEditing(false);
    setError(null);
  };

  const getServiceName = (id: string) => {
    const service = availableServices.find((s) => s.id === id);
    return service?.name || "Unknown Service";
  };

  if (servicesLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-foreground">
            Service Dependencies
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Configure prerequisite services and mandatory add-ons
          </p>
        </div>
        {!isEditing ? (
          <Button onClick={() => setIsEditing(true)} className="cursor-pointer">
            Edit Dependencies
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={isSaving}
              className="cursor-pointer"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving}
              className="cursor-pointer"
            >
              {isSaving ? <Spinner size="sm" /> : "Save Changes"}
            </Button>
          </div>
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
            <p className="text-sm">{success}</p>
          </div>
        </Alert>
      )}

      {/* Prerequisite Services */}
      <Card className="p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
            <LinkIcon size={20} className="text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-foreground mb-1">
              Prerequisite Services
            </h3>
            <p className="text-sm text-muted-foreground">
              Services that must be completed before this service can be booked
            </p>
          </div>
        </div>

        {isEditing && (
          <div className="flex gap-2 mb-4">
            <select
              value={selectedPrerequisite}
              onChange={(e) => setSelectedPrerequisite(e.target.value)}
              className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground cursor-pointer"
            >
              <option value="">Select a service...</option>
              {availableServices
                .filter((s) => !prerequisites.includes(s.id))
                .map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
            </select>
            <Button
              onClick={handleAddPrerequisite}
              disabled={!selectedPrerequisite}
              className="cursor-pointer"
            >
              <PlusIcon size={16} />
              Add
            </Button>
          </div>
        )}

        {prerequisites.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p className="text-sm">No prerequisite services configured</p>
            {!isEditing && (
              <p className="text-xs mt-1">
                Click "Edit Dependencies" to add prerequisites
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {prerequisites.map((prereqId) => (
              <div
                key={prereqId}
                className="flex items-center justify-between p-3 bg-muted rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Badge variant="secondary">Required</Badge>
                  <span className="text-sm font-medium text-foreground">
                    {getServiceName(prereqId)}
                  </span>
                </div>
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRemovePrerequisite(prereqId)}
                    className="cursor-pointer"
                  >
                    <TrashIcon size={14} />
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Mandatory Add-ons */}
      <Card className="p-6">
        <div className="flex items-start gap-3 mb-4">
          <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
            <PlusIcon
              size={20}
              className="text-green-600 dark:text-green-400"
            />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-foreground mb-1">
              Mandatory Add-ons
            </h3>
            <p className="text-sm text-muted-foreground">
              Services that are automatically included when this service is
              booked
            </p>
          </div>
        </div>

        {isEditing && (
          <div className="flex gap-2 mb-4">
            <select
              value={selectedAddon}
              onChange={(e) => setSelectedAddon(e.target.value)}
              className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground cursor-pointer"
            >
              <option value="">Select a service...</option>
              {availableServices
                .filter((s) => !mandatoryAddons.includes(s.id))
                .map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name} - ₦{service.price.toLocaleString()}
                  </option>
                ))}
            </select>
            <Button
              onClick={handleAddAddon}
              disabled={!selectedAddon}
              className="cursor-pointer"
            >
              <PlusIcon size={16} />
              Add
            </Button>
          </div>
        )}

        {mandatoryAddons.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <p className="text-sm">No mandatory add-ons configured</p>
            {!isEditing && (
              <p className="text-xs mt-1">
                Click "Edit Dependencies" to add mandatory add-ons
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {mandatoryAddons.map((addonId) => {
              const service = availableServices.find((s) => s.id === addonId);
              return (
                <div
                  key={addonId}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Badge variant="default">Auto-included</Badge>
                    <div>
                      <span className="text-sm font-medium text-foreground">
                        {getServiceName(addonId)}
                      </span>
                      {service && (
                        <span className="text-xs text-muted-foreground ml-2">
                          +₦{service.price.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  {isEditing && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRemoveAddon(addonId)}
                      className="cursor-pointer"
                    >
                      <TrashIcon size={14} />
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Info Card */}
      <Card className="p-4 bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
        <div className="flex gap-3">
          <AlertTriangleIcon
            size={20}
            className="text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5"
          />
          <div className="text-sm text-blue-900 dark:text-blue-100">
            <p className="font-medium mb-1">How Dependencies Work:</p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>
                <strong>Prerequisites:</strong> Clients must complete these
                services before booking this one
              </li>
              <li>
                <strong>Mandatory Add-ons:</strong> These services are
                automatically added to the booking
              </li>
              <li>
                Dependencies help ensure proper service sequences and upsell
                complementary services
              </li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}
