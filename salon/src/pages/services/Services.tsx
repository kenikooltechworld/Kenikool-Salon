import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { PlusIcon, SearchIcon, TrashIcon, EditIcon } from "@/components/icons";
import { useServices, useDeleteService } from "@/hooks/useServices";
import { ServiceForm } from "@/components/services/ServiceForm";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import type { Service } from "@/types/service";

export default function Services() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingService, setEditingService] = useState<Service | undefined>();
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    serviceId?: string;
  }>({
    isOpen: false,
  });
  const { data: services = [], isLoading, refetch } = useServices();
  const { mutate: deleteService } = useDeleteService();

  // Refetch services when form closes
  useEffect(() => {
    if (!showForm) {
      refetch();
    }
  }, [showForm, refetch]);

  const filteredServices = services.filter(
    (service: Service) =>
      service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.category.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const handleDelete = (id: string) => {
    setDeleteConfirm({ isOpen: true, serviceId: id });
  };

  const handleConfirmDelete = () => {
    if (deleteConfirm.serviceId) {
      deleteService(deleteConfirm.serviceId, {
        onSuccess: (deletedService: any) => {
          showToast({
            variant: "success",
            title: "Success",
            description: `${deletedService.name || "Service"} has been deleted successfully`,
          });
          setDeleteConfirm({ isOpen: false });
        },
        onError: (error: any) => {
          showToast({
            variant: "error",
            title: "Error",
            description:
              error instanceof Error
                ? error.message
                : "Failed to delete service",
          });
        },
      });
    }
  };

  const handleAddService = () => {
    setEditingService(undefined);
    setShowForm(true);
  };

  const handleEditService = (service: Service) => {
    setEditingService(service);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingService(undefined);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Services</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your salon services
          </p>
        </div>
        <Button
          onClick={handleAddService}
          className="gap-2 w-full sm:w-auto cursor-pointer"
        >
          <PlusIcon size={18} />
          Add Service
        </Button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <SearchIcon
          size={18}
          className="absolute left-3 top-3 text-muted-foreground"
        />
        <input
          type="text"
          placeholder="Search services..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>

      {/* Services Grid - Responsive */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          <>
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="bg-card border border-border rounded-lg overflow-hidden"
              >
                <Skeleton className="w-full h-40" />
                <div className="p-4 space-y-3">
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                  <Skeleton className="h-12 w-full" />
                  <div className="flex items-center justify-between pt-2 border-t border-border">
                    <Skeleton className="h-8 w-16" />
                    <Skeleton className="h-8 w-20" />
                  </div>
                </div>
              </div>
            ))}
          </>
        ) : filteredServices.length > 0 ? (
          filteredServices.map((service: Service) => (
            <div
              key={service.id}
              className="bg-card border border-border rounded-lg overflow-hidden hover:shadow-md transition cursor-pointer"
              onClick={() => navigate(`/services/${service.id}`)}
            >
              {/* Image */}
              {service.public_image_url ? (
                <div className="w-full h-40 overflow-hidden bg-muted">
                  <img
                    src={service.public_image_url}
                    alt={service.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-full h-40 bg-muted flex items-center justify-center">
                  <p className="text-muted-foreground text-sm">No image</p>
                </div>
              )}

              {/* Content */}
              <div className="p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">
                      {service.name}
                    </h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {service.category}
                    </p>
                  </div>
                  <div
                    className="flex items-center gap-2 shrink-0"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => handleEditService(service)}
                      className="p-2 hover:bg-muted rounded-lg transition cursor-pointer"
                    >
                      <EditIcon size={16} className="text-muted-foreground" />
                    </button>
                    <button
                      onClick={() => handleDelete(service.id)}
                      className="p-2 hover:bg-destructive/10 rounded-lg transition cursor-pointer"
                    >
                      <TrashIcon size={16} className="text-destructive" />
                    </button>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground line-clamp-2">
                  {service.description}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-border">
                  <div>
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="text-sm font-medium text-foreground">
                      {service.duration_minutes || 0} min
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Price</p>
                    <p className="text-sm font-medium text-foreground">
                      ₦
                      {typeof service.price === "number"
                        ? service.price.toLocaleString()
                        : parseFloat(String(service.price)).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-8 text-muted-foreground">
            No services found
          </div>
        )}
      </div>

      {/* Service Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-background rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
            <ServiceForm
              service={editingService}
              existingServices={services}
              onSuccess={handleFormClose}
              onCancel={handleFormClose}
            />
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirm.isOpen}
        onClose={() => setDeleteConfirm({ isOpen: false })}
        onConfirm={handleConfirmDelete}
        title="Delete Service"
        description="Are you sure you want to delete this service? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
      />
    </div>
  );
}
