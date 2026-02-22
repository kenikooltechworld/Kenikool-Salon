import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeftIcon, EditIcon, TrashIcon } from "@/components/icons";
import { useService, useDeleteService } from "@/hooks/useServices";
import { useServiceCategories } from "@/hooks/useServiceCategories";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { ImageLightbox } from "@/components/services/ImageLightbox";
import { ServiceForm } from "@/components/services/ServiceForm";
import { getIconComponent } from "@/lib/utils/icon-utils";
import { useState } from "react";

export default function ServiceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  const { data: service, isLoading, refetch } = useService(id || "");
  const { data: categories = [] } = useServiceCategories();
  const { mutate: deleteService, isPending: isDeleting } = useDeleteService();

  const category = categories.find(
    (cat: any) => cat.name === service?.category,
  );

  if (isLoading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-start gap-2 sm:gap-4">
            <Skeleton className="h-10 w-10 rounded" />
            <div className="min-w-0 flex items-start gap-3">
              <Skeleton className="h-12 w-12 rounded-lg flex-shrink-0" />
              <div className="min-w-0 flex-1">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-4 w-32 mt-2" />
              </div>
            </div>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            <Skeleton className="h-10 w-20" />
            <Skeleton className="h-10 w-20" />
          </div>
        </div>

        {/* Content Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6">
            {/* Image */}
            <Card className="overflow-hidden">
              <Skeleton className="w-full h-48 sm:h-64 lg:h-96" />
            </Card>

            {/* Description Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </Card>

            {/* Details Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-24 mb-4" />
              <div className="grid grid-cols-2 gap-4 sm:gap-6">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-6 w-24" />
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4 sm:space-y-6">
            {/* Quick Info Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-28 mb-4" />
              <div className="space-y-3 sm:space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-5 w-32" />
                  </div>
                ))}
              </div>
            </Card>

            {/* Tags Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-20 mb-4" />
              <div className="flex flex-wrap gap-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-6 w-16 rounded-full" />
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-muted-foreground">Service not found</div>
      </div>
    );
  }

  const handleDelete = () => {
    if (id) {
      deleteService(id, {
        onSuccess: () => {
          navigate("/services");
        },
      });
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header - Mobile Responsive */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-start gap-2 sm:gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/services")}
            className="gap-2 cursor-pointer flex-shrink-0"
          >
            <ArrowLeftIcon size={18} />
            <span className="hidden sm:inline">Back</span>
          </Button>
          <div className="min-w-0 flex items-start gap-3">
            {/* Service Icon */}
            {service.icon &&
              (() => {
                const IconComponent = getIconComponent(service.icon);
                return IconComponent ? (
                  <div
                    className="flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: service.color || "#3B82F6" }}
                  >
                    <IconComponent size={24} className="text-white" />
                  </div>
                ) : null;
              })()}
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl font-bold text-foreground break-words">
                {service.name}
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                {service.category}
              </p>
            </div>
          </div>
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setEditModalOpen(true)}
            className="gap-2 cursor-pointer text-xs sm:text-sm"
          >
            <EditIcon size={16} />
            <span className="hidden sm:inline">Edit</span>
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setDeleteConfirm(true)}
            className="gap-2 cursor-pointer text-xs sm:text-sm"
          >
            <TrashIcon size={16} />
            <span className="hidden sm:inline">Delete</span>
          </Button>
        </div>
      </div>

      {/* Content - Mobile Responsive */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6">
          {/* Image */}
          {service.public_image_url && (
            <Card className="overflow-hidden">
              <img
                src={service.public_image_url}
                alt={service.name}
                className="w-full h-48 sm:h-64 lg:h-96 object-cover cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => setLightboxOpen(true)}
              />
            </Card>
          )}

          {/* Description */}
          <Card className="p-4 sm:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
              Description
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground">
              {service.description || "No description provided"}
            </p>
          </Card>

          {/* Details */}
          <Card className="p-4 sm:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
              Details
            </h2>
            <div className="grid grid-cols-2 gap-4 sm:gap-6">
              <div className="space-y-1">
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Duration
                </p>
                <p className="text-base sm:text-lg font-semibold text-foreground">
                  {service.duration_minutes} min
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Price
                </p>
                <p className="text-base sm:text-lg font-semibold text-foreground">
                  ₦
                  {typeof service.price === "number"
                    ? service.price.toLocaleString("en-NG")
                    : parseFloat(String(service.price)).toLocaleString("en-NG")}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Status
                </p>
                <Badge variant={service.is_active ? "default" : "secondary"}>
                  {service.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Published
                </p>
                <Badge variant={service.is_published ? "default" : "secondary"}>
                  {service.is_published ? "Yes" : "No"}
                </Badge>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar - Mobile Responsive */}
        <div className="space-y-4 sm:space-y-6">
          {/* Quick Info */}
          <Card className="p-4 sm:p-6">
            <h3 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
              Quick Info
            </h3>
            <div className="space-y-3 sm:space-y-4">
              <div>
                <p className="text-xs text-muted-foreground">Category</p>
                <div className="flex items-center gap-2 mt-1">
                  {category?.icon &&
                    (() => {
                      const IconComponent = getIconComponent(category.icon);
                      return IconComponent ? (
                        <div
                          className="w-6 h-6 rounded flex items-center justify-center flex-shrink-0"
                          style={{
                            backgroundColor: category.color || "#3B82F6",
                          }}
                        >
                          <IconComponent size={14} className="text-white" />
                        </div>
                      ) : null;
                    })()}
                  <p className="text-sm font-medium text-foreground">
                    {service.category}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Created</p>
                <p className="text-sm font-medium text-foreground">
                  {new Date(service.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Last Updated</p>
                <p className="text-sm font-medium text-foreground">
                  {new Date(service.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </Card>

          {/* Tags */}
          {service.tags && service.tags.length > 0 && (
            <Card className="p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {service.tags.map((tag: any) => (
                  <span
                    key={tag}
                    className="px-2 sm:px-3 py-1 bg-primary/10 text-primary rounded-full text-xs sm:text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirm}
        onClose={() => setDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Delete Service"
        description="Are you sure you want to delete this service? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={isDeleting}
      />

      {/* Edit Service Modal */}
      {editModalOpen && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-foreground mb-6">
                Edit Service
              </h2>
              <ServiceForm
                service={service}
                onSuccess={() => {
                  setEditModalOpen(false);
                  refetch();
                }}
                onCancel={() => setEditModalOpen(false)}
              />
            </div>
          </Card>
        </div>
      )}

      {/* Image Lightbox */}
      {service.public_image_url && (
        <ImageLightbox
          isOpen={lightboxOpen}
          imageUrl={service.public_image_url}
          onClose={() => setLightboxOpen(false)}
        />
      )}
    </div>
  );
}
