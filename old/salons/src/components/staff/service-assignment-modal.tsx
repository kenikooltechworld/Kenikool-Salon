import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { CheckIcon, SearchIcon, AlertTriangleIcon } from "@/components/icons";
import { useServices } from "@/lib/api/hooks/useServices";
import { useAssignServices } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";

interface ServiceAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  stylist: Stylist;
}

export function ServiceAssignmentModal({
  isOpen,
  onClose,
  onSuccess,
  stylist,
}: ServiceAssignmentModalProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedServices, setSelectedServices] = useState<string[]>([]);

  const { data: services = [], isLoading: servicesLoading } = useServices();
  const assignServicesMutation = useAssignServices();

  useEffect(() => {
    if (stylist && isOpen) {
      // Load currently assigned services from the stylist's assigned_services field
      setSelectedServices(stylist.assigned_services || []);
    }
  }, [stylist, isOpen]);

  // Ensure services is always an array
  const servicesArray = Array.isArray(services) ? services : [];

  const filteredServices = servicesArray.filter((service: any) =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const toggleService = (serviceId: string) => {
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId],
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await assignServicesMutation.mutateAsync({
        stylistId: stylist.id,
        serviceIds: selectedServices,
      });
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Error assigning services:", error);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Assign Services - {stylist.name}
        </h2>
        <p className="text-sm text-muted-foreground mb-6">
          Select which services this stylist can perform. Clients will only be
          able to book these services with this stylist.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Search */}
          <div className="relative">
            <SearchIcon
              size={20}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <Input
              placeholder="Search services..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Selected Count */}
          <div className="flex items-center justify-between p-3 bg-[var(--muted)]/50 rounded-lg">
            <span className="text-sm text-foreground">Selected Services</span>
            <Badge variant="primary">{selectedServices.length}</Badge>
          </div>

          {/* Service List */}
          {servicesLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : filteredServices.length === 0 ? (
            <Alert variant="warning">
              <AlertTriangleIcon size={20} />
              <div>
                <h3 className="font-semibold">No services found</h3>
                <p className="text-sm">
                  {searchQuery
                    ? "Try adjusting your search"
                    : "Create services first before assigning them"}
                </p>
              </div>
            </Alert>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredServices.map((service: any) => {
                const isSelected = selectedServices.includes(service.id);

                return (
                  <button
                    key={service.id}
                    type="button"
                    onClick={() => toggleService(service.id)}
                    className={`w-full p-3 rounded-lg border-2 transition-all text-left ${
                      isSelected
                        ? "border-[var(--primary)] bg-[var(--primary)]/10"
                        : "border-[var(--border)] hover:border-[var(--primary)]/50"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-foreground">
                            {service.name}
                          </h3>
                          {service.category && (
                            <Badge variant="secondary" size="sm">
                              {service.category}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-3 text-sm text-muted-foreground">
                          <span>₦{service.price?.toLocaleString()}</span>
                          <span>•</span>
                          <span>{service.duration} min</span>
                        </div>
                      </div>
                      {isSelected && (
                        <div className="ml-3 w-6 h-6 rounded-full bg-[var(--primary)] flex items-center justify-center">
                          <CheckIcon size={14} className="text-white" />
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={assignServicesMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={assignServicesMutation.isPending}
            >
              {assignServicesMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Saving...
                </>
              ) : (
                "Save Assignments"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
