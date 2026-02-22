import { useState, lazy, Suspense } from "react";
import { useNavigate } from "react-router-dom";
// Image removed;
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Switch } from "@/components/ui/switch";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { CardSkeleton } from "@/components/ui/skeleton";
import {
  PlusIcon,
  SearchIcon,
  ScissorsIcon,
  EditIcon,
  TrashIcon,
  AlertTriangleIcon,
  FilterIcon,
  EyeIcon,
} from "@/components/icons";
import { useServices, useDeleteService } from "@/lib/api/hooks/useServices";
import { useStylists } from "@/lib/api/hooks/useStylists";
import type { Service } from "@/lib/api/types";
import { apiClient } from "@/lib/api/client";
import { showToast } from "@/lib/utils/toast";

// Lazy load heavy components
const ServiceFormModal = lazy(() =>
  import("@/components/services").then((mod) => ({
    default: mod.ServiceFormModal,
  })),
);
const BulkOperationsPanel = lazy(() =>
  import("@/components/services/bulk-operations-panel").then((mod) => ({
    default: mod.BulkOperationsPanel,
  })),
);
const TemplateLibrary = lazy(() =>
  import("@/components/services/template-library").then((mod) => ({
    default: mod.TemplateLibrary,
  })),
);

const CATEGORIES = [
  "All",
  "Hair",
  "Nails",
  "Makeup",
  "Spa",
  "Massage",
  "Other",
];

export default function ServicesPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [showInactive, setShowInactive] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingService, setEditingService] = useState<Service | undefined>();
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>(
    {},
  );

  // Confirmation modals
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    serviceId: string;
    serviceName: string;
  }>({ isOpen: false, serviceId: "", serviceName: "" });
  const [duplicateConfirmation, setDuplicateConfirmation] = useState<{
    isOpen: boolean;
    serviceId: string;
    serviceName: string;
  }>({ isOpen: false, serviceId: "", serviceName: "" });

  // Advanced filters
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();
  const [minDuration, setMinDuration] = useState<number | undefined>();
  const [maxDuration, setMaxDuration] = useState<number | undefined>();
  const [sortBy, setSortBy] = useState<string>("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Bulk operations
  const [selectedServices, setSelectedServices] = useState<Set<string>>(
    new Set(),
  );
  const [showBulkPanel, setShowBulkPanel] = useState(false);
  const [showTemplateLibrary, setShowTemplateLibrary] = useState(false);

  // Fetch services
  const {
    data: servicesData = [],
    isLoading,
    error,
    refetch,
  } = useServices({
    category: selectedCategory !== "All" ? selectedCategory : undefined,
    is_active: showInactive ? undefined : true,
    min_price: minPrice,
    max_price: maxPrice,
    min_duration: minDuration,
    max_duration: maxDuration,
    sort_by: sortBy || undefined,
    sort_order: sortOrder,
  });

  const services = Array.isArray(servicesData) ? servicesData : [];

  // Fetch staff for stylist assignment
  const { data: stylistsData = [] } = useStylists({ is_active: true });
  const stylists = Array.isArray(stylistsData) ? stylistsData : [];

  // Delete service mutation
  const deleteServiceMutation = useDeleteService();

  // Filter services by search query
  const filteredServices = services.filter((service: Service) =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleOpenModal = (service?: Service) => {
    setEditingService(service);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setEditingService(undefined);
    setIsModalOpen(false);
  };

  const handleToggleStatus = async (id: string, currentStatus: boolean) => {
    setLoadingStates((prev) => ({ ...prev, [`toggle-${id}`]: true }));
    try {
      await apiClient.patch(`/api/services/${id}`, {
        is_active: !currentStatus,
      });
      refetch();
    } catch (err) {
      console.error("Error toggling service status:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update service status";
      showToast(errorMessage, "error");
    } finally {
      setLoadingStates((prev) => ({ ...prev, [`toggle-${id}`]: false }));
    }
  };

  const handleDelete = async () => {
    const { serviceId } = deleteConfirmation;
    setLoadingStates((prev) => ({ ...prev, [`delete-${serviceId}`]: true }));
    try {
      await deleteServiceMutation.mutateAsync(serviceId);
      // Wait a moment for query invalidation to complete
      await new Promise((resolve) => setTimeout(resolve, 100));
      refetch();
      showToast("Service deleted successfully", "success");
    } catch (err) {
      console.error("Error deleting service:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete service";
      showToast(errorMessage, "error");
    } finally {
      setLoadingStates((prev) => ({ ...prev, [`delete-${serviceId}`]: false }));
      setDeleteConfirmation({ isOpen: false, serviceId: "", serviceName: "" });
    }
  };

  const handleViewDetails = (id: string) => {
    setLoadingStates((prev) => ({ ...prev, [`view-${id}`]: true }));
    try {
      navigate(`/dashboard/services/${id}`);
    } catch (error) {
      console.error("Navigation error:", error);
      setLoadingStates((prev) => ({ ...prev, [`view-${id}`]: false }));
    }
  };

  const clearAllFilters = () => {
    setMinPrice(undefined);
    setMaxPrice(undefined);
    setMinDuration(undefined);
    setMaxDuration(undefined);
    setSortBy("");
    setSortOrder("asc");
    setSelectedCategory("All");
    setShowInactive(false);
    setSearchQuery("");
  };

  const hasActiveFilters =
    minPrice ||
    maxPrice ||
    minDuration ||
    maxDuration ||
    sortBy ||
    selectedCategory !== "All" ||
    showInactive ||
    searchQuery;

  const toggleServiceSelection = (id: string) => {
    const newSelected = new Set(selectedServices);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedServices(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedServices.size === filteredServices.length) {
      setSelectedServices(new Set());
    } else {
      setSelectedServices(new Set(filteredServices.map((s: Service) => s.id)));
    }
  };

  const handleBulkSuccess = () => {
    setSelectedServices(new Set());
    setShowBulkPanel(false);
    refetch();
  };

  const handleDuplicateService = async () => {
    const { serviceId } = duplicateConfirmation;
    setLoadingStates((prev) => ({ ...prev, [`duplicate-${serviceId}`]: true }));
    try {
      const response = await apiClient.post(
        `/api/services/${serviceId}/duplicate`,
      );
      const duplicatedService = response.data;
      refetch();
      navigate(`/dashboard/services/${duplicatedService.id}`);
    } catch (err) {
      console.error("Error duplicating service:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to duplicate service";
      showToast(errorMessage, "error");
    } finally {
      setLoadingStates((prev) => ({
        ...prev,
        [`duplicate-${serviceId}`]: false,
      }));
      setDuplicateConfirmation({
        isOpen: false,
        serviceId: "",
        serviceName: "",
      });
    }
  };

  if (error) {
    return (
      <div className="space-y-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading services</h3>
            <p className="text-sm">{error.message || "An error occurred"}</p>
          </div>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Services</h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Manage your salon services and pricing
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {selectedServices.size > 0 && (
            <Button
              variant="outline"
              onClick={() => setShowBulkPanel(true)}
              className="text-xs sm:text-sm"
            >
              <span className="hidden sm:inline">Bulk Operations</span>
              <span className="sm:hidden">Bulk</span> ({selectedServices.size})
            </Button>
          )}
          <Button
            variant="outline"
            onClick={() => setShowTemplateLibrary(true)}
            className="text-xs sm:text-sm"
          >
            <ScissorsIcon size={16} className="sm:w-5 sm:h-5" />
            <span className="hidden sm:inline">From Template</span>
            <span className="sm:hidden">Template</span>
          </Button>
          <Button
            onClick={() => handleOpenModal()}
            className="text-xs sm:text-sm"
          >
            <PlusIcon size={16} className="sm:w-5 sm:h-5" />
            <span className="hidden sm:inline">Add Service</span>
            <span className="sm:hidden">Add</span>
          </Button>
        </div>
      </div>

      {/* Bulk Operations Panel */}
      {showBulkPanel && (
        <Suspense fallback={<Spinner />}>
          <BulkOperationsPanel
            selectedServiceIds={Array.from(selectedServices)}
            onClose={() => setShowBulkPanel(false)}
            onSuccess={handleBulkSuccess}
          />
        </Suspense>
      )}

      {/* Template Library */}
      {showTemplateLibrary && (
        <Suspense fallback={<Spinner />}>
          <TemplateLibrary
            onClose={() => setShowTemplateLibrary(false)}
            onSuccess={() => {
              setShowTemplateLibrary(false);
              refetch();
            }}
          />
        </Suspense>
      )}

      {/* Filters */}
      <Card className="p-3 sm:p-4">
        <div className="flex flex-col gap-4">
          {/* Basic Filters Row */}
          <div className="flex flex-col gap-3">
            {/* Search */}
            <div className="w-full">
              <div className="relative">
                <SearchIcon
                  size={18}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                />
                <Input
                  placeholder="Search services..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 text-sm"
                />
              </div>
            </div>

            {/* Filters Row */}
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-4">
              {/* Category Filter */}
              <div className="flex items-center gap-2 flex-1">
                <FilterIcon
                  size={16}
                  className="text-muted-foreground flex-shrink-0"
                />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-2 sm:px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-background text-foreground"
                >
                  {CATEGORIES.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </div>

              {/* Show Inactive Toggle */}
              <div className="flex items-center gap-2 whitespace-nowrap">
                <Switch
                  checked={showInactive}
                  onCheckedChange={setShowInactive}
                  label="Show Inactive"
                />
              </div>

              {/* Advanced Filters Toggle */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className="w-full sm:w-auto text-xs sm:text-sm"
              >
                <FilterIcon size={14} />
                <span className="hidden sm:inline">
                  {showAdvancedFilters ? "Hide" : "Show"} Advanced
                </span>
                <span className="sm:hidden">
                  {showAdvancedFilters ? "Hide" : "Show"}
                </span>
              </Button>
            </div>
          </div>

          {/* Advanced Filters Panel */}
          {showAdvancedFilters && (
            <div className="border-t border-border pt-4 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                {/* Price Range */}
                <div>
                  <label className="text-xs sm:text-sm font-medium text-foreground mb-2 block">
                    Min Price (₦)
                  </label>
                  <Input
                    type="number"
                    placeholder="Min"
                    value={minPrice || ""}
                    onChange={(e) =>
                      setMinPrice(
                        e.target.value ? Number(e.target.value) : undefined,
                      )
                    }
                    className="text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs sm:text-sm font-medium text-foreground mb-2 block">
                    Max Price (₦)
                  </label>
                  <Input
                    type="number"
                    placeholder="Max"
                    value={maxPrice || ""}
                    onChange={(e) =>
                      setMaxPrice(
                        e.target.value ? Number(e.target.value) : undefined,
                      )
                    }
                    className="text-sm"
                  />
                </div>

                {/* Duration Range */}
                <div>
                  <label className="text-xs sm:text-sm font-medium text-foreground mb-2 block">
                    Min Duration (mins)
                  </label>
                  <Input
                    type="number"
                    placeholder="Min"
                    value={minDuration || ""}
                    onChange={(e) =>
                      setMinDuration(
                        e.target.value ? Number(e.target.value) : undefined,
                      )
                    }
                    className="text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs sm:text-sm font-medium text-foreground mb-2 block">
                    Max Duration (mins)
                  </label>
                  <Input
                    type="number"
                    placeholder="Max"
                    value={maxDuration || ""}
                    onChange={(e) =>
                      setMaxDuration(
                        e.target.value ? Number(e.target.value) : undefined,
                      )
                    }
                    className="text-sm"
                  />
                </div>
              </div>

              {/* Sort Controls */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div>
                  <label className="text-xs sm:text-sm font-medium text-foreground mb-2 block">
                    Sort By
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-2 sm:px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-background text-foreground"
                  >
                    <option value="">None</option>
                    <option value="price">Price</option>
                    <option value="duration">Duration</option>
                    <option value="name">Name</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs sm:text-sm font-medium text-foreground mb-2 block">
                    Sort Order
                  </label>
                  <select
                    value={sortOrder}
                    onChange={(e) =>
                      setSortOrder(e.target.value as "asc" | "desc")
                    }
                    className="w-full px-2 sm:px-3 py-2 text-sm border border-[var(--border)] rounded-lg bg-background text-foreground"
                  >
                    <option value="asc">Ascending</option>
                    <option value="desc">Descending</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Active Filters Display */}
          {hasActiveFilters && (
            <div className="flex flex-wrap items-center gap-2 border-t border-border pt-4">
              <span className="text-xs sm:text-sm text-muted-foreground">
                Active filters:
              </span>
              {minPrice && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setMinPrice(undefined)}
                >
                  Min: ₦{minPrice} ✕
                </Badge>
              )}
              {maxPrice && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setMaxPrice(undefined)}
                >
                  Max: ₦{maxPrice} ✕
                </Badge>
              )}
              {minDuration && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setMinDuration(undefined)}
                >
                  Min: {minDuration}m ✕
                </Badge>
              )}
              {maxDuration && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setMaxDuration(undefined)}
                >
                  Max: {maxDuration}m ✕
                </Badge>
              )}
              {sortBy && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setSortBy("")}
                >
                  Sort: {sortBy} ({sortOrder}) ✕
                </Badge>
              )}
              {selectedCategory !== "All" && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setSelectedCategory("All")}
                >
                  Category: {selectedCategory} ✕
                </Badge>
              )}
              {showInactive && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setShowInactive(false)}
                >
                  Show Inactive ✕
                </Badge>
              )}
              {searchQuery && (
                <Badge
                  variant="secondary"
                  className="cursor-pointer text-xs"
                  onClick={() => setSearchQuery("")}
                >
                  Search: &quot;{searchQuery}&quot; ✕
                </Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={clearAllFilters}
                className="text-xs"
              >
                Clear All
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Services Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {[...Array(6)].map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : filteredServices.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <ScissorsIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No services found
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery
                ? "Try adjusting your search or filters"
                : "Get started by adding your first service"}
            </p>
            {!searchQuery && (
              <Button onClick={() => handleOpenModal()}>
                <PlusIcon size={20} />
                Add Service
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {filteredServices.length > 0 && (
            <div className="col-span-full flex items-center gap-2 mb-2">
              <input
                type="checkbox"
                checked={
                  selectedServices.size === filteredServices.length &&
                  filteredServices.length > 0
                }
                onChange={toggleSelectAll}
                className="w-4 h-4 cursor-pointer"
              />
              <span className="text-xs sm:text-sm text-muted-foreground">
                Select All ({selectedServices.size}/{filteredServices.length})
              </span>
            </div>
          )}
          {filteredServices.map((service: Service, index: number) => (
            <Card
              key={service.id}
              className="overflow-hidden animate-fade-in hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Service Image */}
              <div className="relative h-40 sm:h-48 bg-[var(--muted)]">
                {service.photo_url ? (
                  <img
                    src={service.photo_url}
                    alt={service.name}
                    className="object-cover w-full h-full"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <ScissorsIcon
                      size={40}
                      className="sm:w-12 sm:h-12 text-muted-foreground"
                    />
                  </div>
                )}
                <div className="absolute top-2 sm:top-3 left-2 sm:left-3">
                  <input
                    type="checkbox"
                    checked={selectedServices.has(service.id)}
                    onChange={() => toggleServiceSelection(service.id)}
                    className="w-4 h-4 sm:w-5 sm:h-5 cursor-pointer"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
                <div className="absolute top-2 sm:top-3 right-2 sm:right-3">
                  <Badge
                    variant={service.is_active ? "default" : "destructive"}
                    className="text-xs"
                  >
                    {service.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </div>

              {/* Service Details */}
              <div className="p-3 sm:p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-sm sm:text-base text-foreground mb-1">
                      {service.name}
                    </h3>
                    <Badge variant="secondary" size="sm" className="text-xs">
                      {service.category}
                    </Badge>
                  </div>
                </div>

                <p className="text-xs sm:text-sm text-muted-foreground mb-3 line-clamp-2">
                  {service.description || "No description"}
                </p>

                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xl sm:text-2xl font-bold text-foreground">
                      ₦{service.price.toLocaleString()}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {service.duration_minutes} mins
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      {service.assigned_stylists.length} stylist
                      {service.assigned_stylists.length !== 1 ? "s" : ""}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-2">
                  <Button
                    variant="primary"
                    size="sm"
                    className="w-full text-xs sm:text-sm"
                    onClick={() => handleViewDetails(service.id)}
                    disabled={loadingStates[`view-${service.id}`]}
                  >
                    {loadingStates[`view-${service.id}`] ? (
                      <>
                        <Spinner size="sm" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <EyeIcon size={14} className="sm:w-4 sm:h-4" />
                        View Details
                      </>
                    )}
                  </Button>
                  <div className="grid grid-cols-4 gap-1 sm:gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="p-1 sm:p-2"
                      onClick={() => handleOpenModal(service)}
                      title="Edit"
                    >
                      <EditIcon size={14} className="sm:w-4 sm:h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="p-1 sm:p-2"
                      onClick={() =>
                        setDuplicateConfirmation({
                          isOpen: true,
                          serviceId: service.id,
                          serviceName: service.name,
                        })
                      }
                      disabled={loadingStates[`duplicate-${service.id}`]}
                      title="Duplicate"
                    >
                      {loadingStates[`duplicate-${service.id}`] ? (
                        <Spinner size="sm" />
                      ) : (
                        <ScissorsIcon size={14} className="sm:w-4 sm:h-4" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="p-1 sm:p-2 text-xs"
                      onClick={() =>
                        handleToggleStatus(service.id, service.is_active)
                      }
                      disabled={loadingStates[`toggle-${service.id}`]}
                      title={service.is_active ? "Deactivate" : "Activate"}
                    >
                      {loadingStates[`toggle-${service.id}`] ? (
                        <Spinner size="sm" />
                      ) : (
                        <>
                          <span className="hidden sm:inline">
                            {service.is_active ? "Off" : "On"}
                          </span>
                          <span className="sm:hidden">
                            {service.is_active ? "Off" : "On"}
                          </span>
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="p-1 sm:p-2"
                      onClick={() =>
                        setDeleteConfirmation({
                          isOpen: true,
                          serviceId: service.id,
                          serviceName: service.name,
                        })
                      }
                      disabled={loadingStates[`delete-${service.id}`]}
                      title="Delete"
                    >
                      {loadingStates[`delete-${service.id}`] ? (
                        <Spinner size="sm" />
                      ) : (
                        <TrashIcon size={14} className="sm:w-4 sm:h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Service Form Modal */}
      <Suspense fallback={null}>
        <ServiceFormModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSuccess={(serviceId?: string) => {
            // If a new service was created, navigate to it
            if (serviceId && !editingService) {
              navigate(`/dashboard/services/${serviceId}`);
            } else {
              // If editing, just refetch the list
              refetch();
            }
          }}
          service={editingService}
          availableStylists={stylists}
        />
      </Suspense>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirmation.isOpen}
        onClose={() =>
          setDeleteConfirmation({
            isOpen: false,
            serviceId: "",
            serviceName: "",
          })
        }
        onConfirm={handleDelete}
        title="Delete Service"
        description={`Are you sure you want to delete "${deleteConfirmation.serviceName}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={loadingStates[`delete-${deleteConfirmation.serviceId}`]}
      />

      {/* Duplicate Confirmation Modal */}
      <ConfirmationModal
        isOpen={duplicateConfirmation.isOpen}
        onClose={() =>
          setDuplicateConfirmation({
            isOpen: false,
            serviceId: "",
            serviceName: "",
          })
        }
        onConfirm={handleDuplicateService}
        title="Duplicate Service"
        description={`Create a copy of "${duplicateConfirmation.serviceName}"?`}
        confirmText="Duplicate"
        cancelText="Cancel"
        isLoading={
          loadingStates[`duplicate-${duplicateConfirmation.serviceId}`]
        }
      />
    </div>
  );
}
