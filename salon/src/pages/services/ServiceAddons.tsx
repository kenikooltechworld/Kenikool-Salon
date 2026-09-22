import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { PlusIcon, SearchIcon, TrashIcon, EditIcon, FilterIcon } from "@/components/icons";
import { useAllServiceAddons, useDeleteServiceAddon } from "@/hooks/useServiceAddonsAdmin";
import { ServiceAddonForm } from "@/components/services/ServiceAddonForm";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import type { ServiceAddon } from "@/hooks/useServiceAddons";

export default function ServiceAddons() {
  const { showToast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [showForm, setShowForm] = useState(false);
  const [editingAddon, setEditingAddon] = useState<ServiceAddon | undefined>();
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    addonId?: string;
    addonName?: string;
  }>({
    isOpen: false,
  });

  const filters = {
    search: searchTerm || undefined,
    category: categoryFilter || undefined,
    is_active: activeFilter === "all" ? undefined : activeFilter === "active",
  };

  const { data: addons = [], isLoading, refetch } = useAllServiceAddons(filters);
  const { mutate: deleteAddon } = useDeleteServiceAddon();

  // Refetch addons when form closes
  useEffect(() => {
    if (!showForm) {
      refetch();
    }
  }, [showForm, refetch]);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "product":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "upgrade":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "treatment":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const handleDelete = (id: string, name: string) => {
    setDeleteConfirm({ isOpen: true, addonId: id, addonName: name });
  };

  const handleConfirmDelete = () => {
    if (deleteConfirm.addonId) {
      deleteAddon(deleteConfirm.addonId, {
        onSuccess: () => {
          showToast({
            variant: "success",
            title: "Success",
            description: `${deleteConfirm.addonName || "Service addon"} has been deleted successfully`,
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
                : "Failed to delete service addon",
          });
        },
      });
    }
  };

  const handleAddAddon = () => {
    setEditingAddon(undefined);
    setShowForm(true);
  };

  const handleEditAddon = (addon: ServiceAddon) => {
    setEditingAddon(addon);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingAddon(undefined);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Service Add-ons</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage additional services and products your customers can add to their bookings
          </p>
        </div>
        <Button
          onClick={handleAddAddon}
          className="gap-2 w-full sm:w-auto cursor-pointer"
        >
          <PlusIcon size={18} />
          Add Service Add-on
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <SearchIcon
            size={18}
            className="absolute left-3 top-3 text-muted-foreground"
          />
          <input
            type="text"
            placeholder="Search addons..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Category Filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All Categories</option>
          <option value="product">Product</option>
          <option value="upgrade">Upgrade</option>
          <option value="treatment">Treatment</option>
        </select>

        {/* Status Filter */}
        <select
          value={activeFilter}
          onChange={(e) => setActiveFilter(e.target.value)}
          className="px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {/* Addons Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          <>
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="bg-card border border-border rounded-lg overflow-hidden"
              >
                <Skeleton className="w-full h-32" />
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
        ) : addons.length > 0 ? (
          addons.map((addon: ServiceAddon) => (
            <div
              key={addon.id}
              className={`bg-card border border-border rounded-lg overflow-hidden hover:shadow-md transition ${
                !addon.is_active ? "opacity-60" : ""
              }`}
            >
              {/* Image */}
              {addon.image_url ? (
                <div className="w-full h-32 overflow-hidden bg-muted">
                  <img
                    src={addon.image_url}
                    alt={addon.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-full h-32 bg-muted flex items-center justify-center">
                  <p className="text-muted-foreground text-sm">No image</p>
                </div>
              )}

              {/* Content */}
              <div className="p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-foreground">
                        {addon.name}
                      </h3>
                      {!addon.is_active && (
                        <Badge variant="secondary" className="text-xs">
                          Inactive
                        </Badge>
                      )}
                    </div>
                    <Badge className={`${getCategoryColor(addon.category)} text-xs mb-2`}>
                      {addon.category}
                    </Badge>
                  </div>
                  <div
                    className="flex items-center gap-2 shrink-0"
                  >
                    <button
                      onClick={() => handleEditAddon(addon)}
                      className="p-2 hover:bg-muted rounded-lg transition cursor-pointer"
                    >
                      <EditIcon size={16} className="text-muted-foreground" />
                    </button>
                    <button
                      onClick={() => handleDelete(addon.id, addon.name)}
                      className="p-2 hover:bg-destructive/10 rounded-lg transition cursor-pointer"
                    >
                      <TrashIcon size={16} className="text-destructive" />
                    </button>
                  </div>
                </div>

                <p className="text-sm text-muted-foreground line-clamp-2">
                  {addon.description}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-border">
                  <div>
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="text-sm font-medium text-foreground">
                      {addon.duration_minutes} min
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Price</p>
                    <p className="text-sm font-medium text-foreground">
                      ₦{typeof addon.price === "number"
                        ? addon.price.toLocaleString()
                        : parseFloat(String(addon.price)).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-8 text-muted-foreground">
            {searchTerm || categoryFilter || activeFilter !== "all"
              ? "No addons found matching your filters"
              : "No service addons found. Create your first addon to get started."}
          </div>
        )}
      </div>

      {/* Service Addon Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-background rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <ServiceAddonForm
              addon={editingAddon}
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
        title="Delete Service Add-on"
        description={`Are you sure you want to delete "${deleteConfirm.addonName}"? This action cannot be undone and will affect any existing bookings that include this add-on.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
      />
    </div>
  );
}