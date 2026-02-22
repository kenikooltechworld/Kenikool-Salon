import { useState, lazy, Suspense, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
// Image removed;
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { ImageLightbox } from "@/components/ui/image-lightbox";
import { StatCardSkeleton } from "@/components/ui/skeleton";
import { ServiceDetailsPageSkeleton } from "@/components/ui/service-details-skeleton";
import {
  ArrowLeftIcon,
  EditIcon,
  TrashIcon,
  ScissorsIcon,
  AlertTriangleIcon,
  DollarIcon,
  CalendarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  StarIcon,
} from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { Service } from "@/lib/api/types";
import { RecentBookingsList } from "@/components/services/recent-bookings-list";
import { StylistPerformanceWidget } from "@/components/services/stylist-performance-widget";
import { useStylists } from "@/lib/api/hooks/useStylists";
import { showToast } from "@/lib/utils/toast";

// Lazy load heavy components and modals
const ServiceFormModal = lazy(() =>
  import("@/components/services").then((mod) => ({
    default: mod.ServiceFormModal,
  })),
);
const AuditLogViewer = lazy(() =>
  import("@/components/services/audit-log-viewer").then((mod) => ({
    default: mod.AuditLogViewer,
  })),
);
const ServiceVariantManager = lazy(() =>
  import("@/components/services/service-variant-manager").then((mod) => ({
    default: mod.ServiceVariantManager,
  })),
);
const TieredPricingEditor = lazy(() =>
  import("@/components/services/tiered-pricing-editor").then((mod) => ({
    default: mod.TieredPricingEditor,
  })),
);
const BookingRulesEditor = lazy(() =>
  import("@/components/services/booking-rules-editor").then((mod) => ({
    default: mod.BookingRulesEditor,
  })),
);
const AvailabilityScheduler = lazy(() =>
  import("@/components/services/availability-scheduler").then((mod) => ({
    default: mod.AvailabilityScheduler,
  })),
);
const CapacityManager = lazy(() =>
  import("@/components/services/capacity-manager").then((mod) => ({
    default: mod.CapacityManager,
  })),
);
const CommissionEditor = lazy(() =>
  import("@/components/services/commission-editor").then((mod) => ({
    default: mod.CommissionEditor,
  })),
);
const ResourceManager = lazy(() =>
  import("@/components/services/resource-manager").then((mod) => ({
    default: mod.ResourceManager,
  })),
);
const ServiceRecommendations = lazy(() =>
  import("@/components/services/service-recommendations").then((mod) => ({
    default: mod.ServiceRecommendations,
  })),
);
const MarketingSettings = lazy(() =>
  import("@/components/services/marketing-settings").then((mod) => ({
    default: mod.MarketingSettings,
  })),
);
const ServiceReviewsSection = lazy(() =>
  import("@/components/services/service-reviews-section").then((mod) => ({
    default: mod.ServiceReviewsSection,
  })),
);
const DependencyManager = lazy(() =>
  import("@/components/services/dependency-manager").then((mod) => ({
    default: mod.DependencyManager,
  })),
);
const PerformanceReport = lazy(() =>
  import("@/components/services/performance-report").then((mod) => ({
    default: mod.PerformanceReport,
  })),
);
const ServiceLocationsSection = lazy(() =>
  import("@/components/services/service-locations-section").then((mod) => ({
    default: mod.ServiceLocationsSection,
  })),
);

interface ServiceStatistics {
  totalBookings: number;
  completedBookings: number;
  cancelledBookings: number;
  totalRevenue: number;
  averageBookingValue: number;
  revenueTrend: number | null;
  popularityRank?: number;
  averageRating?: number;
  conversionRate?: number;
}

interface ServiceDetails {
  service: Service;
  statistics: ServiceStatistics;
}

export default function ServiceDetailsPage() {
  const params = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const serviceId = params.id as string;

  // Get initial tab from URL query parameter, default to "overview"
  const initialTab = (searchParams.get("tab") || "overview") as any;
  const [activeTab, setActiveTab] = useState<
    | "overview"
    | "variants"
    | "pricing"
    | "rules"
    | "availability"
    | "capacity"
    | "commission"
    | "resources"
    | "marketing"
    | "reports"
    | "dependencies"
    | "locations"
    | "audit"
  >(initialTab);

  // Modal states
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDuplicateModalOpen, setIsDuplicateModalOpen] = useState(false);
  const [isSaveTemplateModalOpen, setIsSaveTemplateModalOpen] = useState(false);
  const [isImageLightboxOpen, setIsImageLightboxOpen] = useState(false);
  const [templateName, setTemplateName] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const { data, isLoading, error, refetch } = useQuery<ServiceDetails>({
    queryKey: ["service-details", serviceId],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/services/${serviceId}/details`,
      );
      return response.data;
    },
  });

  // Fetch staff for edit modal
  const { data: stylistsData = [] } = useStylists({ is_active: true });
  const stylists = Array.isArray(stylistsData) ? stylistsData : [];

  // Update URL when tab changes
  useEffect(() => {
    setSearchParams({ tab: activeTab }, { replace: true });
  }, [activeTab, setSearchParams]);

  const handleBack = () => {
    navigate("/dashboard/services");
  };

  const handleEdit = () => {
    setIsEditModalOpen(true);
  };

  const handleDelete = async () => {
    setIsProcessing(true);
    try {
      await apiClient.delete(`/api/services/${serviceId}`);
      showToast("Service deleted successfully", "success");
      navigate("/dashboard/services");
    } catch (err) {
      console.error("Error deleting service:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete service";
      showToast(errorMessage, "error");
    } finally {
      setIsProcessing(false);
      setIsDeleteModalOpen(false);
    }
  };

  const handleDuplicate = async () => {
    setIsProcessing(true);
    try {
      const response = await apiClient.post(
        `/api/services/${serviceId}/duplicate`,
      );
      const duplicatedService = response.data;
      showToast("Service duplicated successfully", "success");
      navigate(`/dashboard/services/${duplicatedService.id}`);
    } catch (err) {
      console.error("Error duplicating service:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to duplicate service";
      showToast(errorMessage, "error");
    } finally {
      setIsProcessing(false);
      setIsDuplicateModalOpen(false);
    }
  };

  const handleSaveAsTemplate = async () => {
    if (!templateName.trim()) {
      showToast("Please enter a template name", "warning");
      return;
    }

    if (!data) return;

    const { service } = data;

    setIsProcessing(true);
    try {
      await apiClient.post("/api/services/templates", {
        name: templateName,
        description: service.description || `Template for ${service.name}`,
        category: service.category,
        template_data: {
          price: service.price,
          duration_minutes: service.duration_minutes,
          description: service.description,
          category: service.category,
          tiered_pricing: service.tiered_pricing,
          booking_rules: service.booking_rules,
          availability: service.availability,
          max_concurrent_bookings: service.max_concurrent_bookings,
          commission_structure: service.commission_structure,
        },
      });
      showToast("Template saved successfully!", "success");
      setTemplateName("");
    } catch (err) {
      console.error("Error saving template:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to save template";
      showToast(errorMessage, "error");
    } finally {
      setIsProcessing(false);
      setIsSaveTemplateModalOpen(false);
    }
  };

  if (isLoading) {
    return <ServiceDetailsPageSkeleton />;
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading service</h3>
            <p className="text-sm">
              {error instanceof Error ? error.message : "Service not found"}
            </p>
          </div>
        </Alert>
        <Button onClick={handleBack}>
          <ArrowLeftIcon size={20} />
          Back to Services
        </Button>
      </div>
    );
  }

  const { service, statistics } = data;

  return (
    <div className="w-full min-h-screen bg-background">
      {/* Header - Mobile First */}
      <div className="space-y-3 mb-4">
        <Button variant="outline" onClick={handleBack} className="w-full">
          <ArrowLeftIcon size={16} />
          Back to Services
        </Button>
        <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:gap-2">
          <Button
            variant="outline"
            onClick={() => setIsSaveTemplateModalOpen(true)}
            className="text-xs sm:text-sm h-9 sm:h-10"
          >
            <ScissorsIcon size={14} />
            <span className="hidden sm:inline">Save as Template</span>
            <span className="sm:hidden">Template</span>
          </Button>
          <Button
            variant="outline"
            onClick={() => setIsDuplicateModalOpen(true)}
            className="text-xs sm:text-sm h-9 sm:h-10"
          >
            <ScissorsIcon size={14} />
            <span className="hidden sm:inline">Duplicate</span>
            <span className="sm:hidden">Dup</span>
          </Button>
          <Button
            variant="outline"
            onClick={handleEdit}
            className="text-xs sm:text-sm h-9 sm:h-10"
          >
            <EditIcon size={14} />
            Edit
          </Button>
          <Button
            variant="outline"
            onClick={() => setIsDeleteModalOpen(true)}
            className="text-xs sm:text-sm h-9 sm:h-10"
          >
            <TrashIcon size={14} />
            Delete
          </Button>
        </div>
      </div>

      {/* Service Header Card - Mobile First */}
      <Card className="p-3 sm:p-4 md:p-6 mb-4">
        <div className="flex flex-col gap-4">
          {/* Service Photo - Full width on mobile */}
          <div
            className="w-full h-48 sm:h-40 md:h-48 lg:h-56 rounded-lg overflow-hidden bg-muted relative cursor-pointer group"
            onClick={() => service.photo_url && setIsImageLightboxOpen(true)}
          >
            {service.photo_url ? (
              <>
                <img
                  src={service.photo_url}
                  alt={service.name}
                  className="object-cover w-full h-full transition-transform duration-300 group-hover:scale-110"
                  sizes="(max-width: 640px) 100vw, (max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  loading="eager"
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors duration-300 flex items-center justify-center">
                  <span className="text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-xs sm:text-sm font-medium">
                    Click to view
                  </span>
                </div>
              </>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <ScissorsIcon
                  size={40}
                  className="sm:w-12 sm:h-12 md:w-16 md:h-16 text-muted-foreground"
                />
              </div>
            )}
          </div>

          {/* Service Info */}
          <div className="space-y-3">
            <div>
              <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-foreground mb-2 line-clamp-2">
                {service.name}
              </h1>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="secondary" className="text-xs">
                  {service.category}
                </Badge>
                <Badge
                  variant={service.is_active ? "default" : "destructive"}
                  className="text-xs"
                >
                  {service.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-muted-foreground line-clamp-3">
              {service.description || "No description available"}
            </p>

            {/* Key Stats - 3 columns on all sizes */}
            <div className="grid grid-cols-3 gap-2 sm:gap-3 pt-2">
              <div className="bg-muted/50 rounded-lg p-2 sm:p-3">
                <p className="text-xs text-muted-foreground mb-1">Price</p>
                <p className="text-sm sm:text-base md:text-lg font-bold text-foreground truncate">
                  ₦{(service.price / 1000).toFixed(0)}k
                </p>
              </div>
              <div className="bg-muted/50 rounded-lg p-2 sm:p-3">
                <p className="text-xs text-muted-foreground mb-1">Duration</p>
                <p className="text-sm sm:text-base md:text-lg font-bold text-foreground">
                  {service.duration_minutes}m
                </p>
              </div>
              <div className="bg-muted/50 rounded-lg p-2 sm:p-3">
                <p className="text-xs text-muted-foreground mb-1">Stylists</p>
                <p className="text-sm sm:text-base md:text-lg font-bold text-foreground">
                  {service.assigned_stylists.length}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Tabs - Scrollable on mobile */}
      <Card className="p-0 mb-4">
        <div className="border-b border-border overflow-x-auto scrollbar-hide">
          <div className="flex gap-1 p-1 min-w-min">
            {[
              { id: "overview", label: "Overview", short: "Over" },
              { id: "variants", label: "Variants", short: "Var" },
              { id: "pricing", label: "Pricing", short: "Price" },
              { id: "rules", label: "Rules", short: "Rules" },
              { id: "availability", label: "Avail", short: "Avail" },
              { id: "capacity", label: "Capacity", short: "Cap" },
              { id: "commission", label: "Commission", short: "Comm" },
              { id: "resources", label: "Resources", short: "Res" },
              { id: "marketing", label: "Marketing", short: "Mkt" },
              { id: "reports", label: "Reports", short: "Rep" },
              { id: "dependencies", label: "Dependencies", short: "Dep" },
              { id: "locations", label: "Locations", short: "Loc" },
              { id: "audit", label: "Audit", short: "Audit" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-2 sm:px-3 md:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 whitespace-nowrap cursor-pointer flex-shrink-0 ${
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted hover:shadow-sm"
                }`}
              >
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden">{tab.short}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content - Responsive padding */}
        <div className="p-3 sm:p-4 md:p-6">
          {activeTab === "overview" && (
            <div className="space-y-4 sm:space-y-6">
              {/* Statistics Cards - Mobile first grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
                {!statistics ? (
                  <>
                    <StatCardSkeleton />
                    <StatCardSkeleton />
                    <StatCardSkeleton />
                  </>
                ) : (
                  <>
                    <Card className="p-3 sm:p-4 md:p-6 animate-fade-in hover:shadow-lg transition-all duration-300">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                            Total Revenue
                          </p>
                          <p className="text-lg sm:text-xl md:text-2xl font-bold text-foreground truncate">
                            ₦{(statistics.totalRevenue || 0).toLocaleString()}
                          </p>
                          {statistics.revenueTrend !== null &&
                            statistics.revenueTrend !== undefined && (
                              <div className="flex items-center gap-1 mt-2 flex-wrap">
                                {statistics.revenueTrend >= 0 ? (
                                  <TrendingUpIcon
                                    size={12}
                                    className="sm:w-4 sm:h-4 text-green-500"
                                  />
                                ) : (
                                  <TrendingDownIcon
                                    size={12}
                                    className="sm:w-4 sm:h-4 text-red-500"
                                  />
                                )}
                                <span
                                  className={`text-xs font-medium ${
                                    statistics.revenueTrend >= 0
                                      ? "text-green-500"
                                      : "text-red-500"
                                  }`}
                                >
                                  {statistics.revenueTrend >= 0 ? "+" : ""}
                                  {(statistics.revenueTrend || 0).toFixed(1)}%
                                </span>
                              </div>
                            )}
                        </div>
                        <div className="p-2 sm:p-3 bg-primary/10 rounded-lg flex-shrink-0">
                          <DollarIcon
                            size={18}
                            className="sm:w-5 sm:h-5 md:w-6 md:h-6 text-primary"
                          />
                        </div>
                      </div>
                    </Card>

                    <Card
                      className="p-3 sm:p-4 md:p-6 animate-fade-in hover:shadow-lg transition-all duration-300"
                      style={{ animationDelay: "100ms" }}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                            Total Bookings
                          </p>
                          <p className="text-lg sm:text-xl md:text-2xl font-bold text-foreground">
                            {statistics.totalBookings || 0}
                          </p>
                          <p className="text-xs sm:text-sm text-muted-foreground mt-2">
                            {statistics.completedBookings || 0} completed
                          </p>
                        </div>
                        <div className="p-2 sm:p-3 bg-primary/10 rounded-lg flex-shrink-0">
                          <CalendarIcon
                            size={18}
                            className="sm:w-5 sm:h-5 md:w-6 md:h-6 text-primary"
                          />
                        </div>
                      </div>
                    </Card>

                    <Card
                      className="p-3 sm:p-4 md:p-6 animate-fade-in hover:shadow-lg transition-all duration-300"
                      style={{ animationDelay: "150ms" }}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                            Avg Booking Value
                          </p>
                          <p className="text-lg sm:text-xl md:text-2xl font-bold text-foreground truncate">
                            ₦
                            {(
                              statistics.averageBookingValue || 0
                            ).toLocaleString()}
                          </p>
                          <p className="text-xs sm:text-sm text-muted-foreground mt-2">
                            Per booking
                          </p>
                        </div>
                        <div className="p-2 sm:p-3 bg-primary/10 rounded-lg flex-shrink-0">
                          <StarIcon
                            size={18}
                            className="sm:w-5 sm:h-5 md:w-6 md:h-6 text-primary"
                          />
                        </div>
                      </div>
                    </Card>
                  </>
                )}
              </div>

              {/* Recent Bookings and Stylist Performance - Stack on mobile */}
              <div className="space-y-4 sm:space-y-6">
                <RecentBookingsList serviceId={serviceId} />
                <StylistPerformanceWidget serviceId={serviceId} />
              </div>

              {/* Service Recommendations */}
              <Card className="p-3 sm:p-4 md:p-6">
                <Suspense fallback={<Spinner />}>
                  <ServiceRecommendations
                    serviceId={serviceId}
                    isEditing={false}
                  />
                </Suspense>
              </Card>

              {/* Service Reviews */}
              <Card className="p-3 sm:p-4 md:p-6">
                <Suspense fallback={<Spinner />}>
                  <ServiceReviewsSection serviceId={serviceId} />
                </Suspense>
              </Card>
            </div>
          )}

          {activeTab === "variants" && (
            <Suspense fallback={<Spinner />}>
              <ServiceVariantManager
                serviceId={serviceId}
                basePrice={service.price}
                baseDuration={service.duration_minutes}
              />
            </Suspense>
          )}

          {activeTab === "pricing" && (
            <Suspense fallback={<Spinner />}>
              <div>
                <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
                  Tiered Pricing Configuration
                </h2>
                <p className="text-xs sm:text-sm text-muted-foreground mb-6">
                  Set different price multipliers based on stylist experience
                  level.
                </p>
                <TieredPricingEditor
                  basePrice={service.price}
                  tiers={service.tiered_pricing || []}
                  onChange={async (newTiers) => {
                    try {
                      await apiClient.patch(`/api/services/${serviceId}`, {
                        tiered_pricing: newTiers,
                      });
                      refetch();
                    } catch (error) {
                      console.error("Error updating tiered pricing:", error);
                    }
                  }}
                />
              </div>
            </Suspense>
          )}

          {activeTab === "rules" && (
            <Suspense fallback={<Spinner />}>
              <BookingRulesEditor
                serviceId={serviceId}
                initialRules={service.booking_rules}
              />
            </Suspense>
          )}

          {activeTab === "availability" && (
            <Suspense fallback={<Spinner />}>
              <AvailabilityScheduler
                serviceId={serviceId}
                initialAvailability={service.availability}
              />
            </Suspense>
          )}

          {activeTab === "capacity" && (
            <Suspense fallback={<Spinner />}>
              <CapacityManager
                serviceId={serviceId}
                initialCapacity={service.max_concurrent_bookings}
              />
            </Suspense>
          )}

          {activeTab === "commission" && (
            <Suspense fallback={<Spinner />}>
              <CommissionEditor
                serviceId={serviceId}
                servicePrice={service.price}
                assignedStylists={service.assigned_stylists}
              />
            </Suspense>
          )}

          {activeTab === "resources" && (
            <Suspense fallback={<Spinner />}>
              <ResourceManager
                serviceId={serviceId}
                initialResources={service.required_resources || []}
              />
            </Suspense>
          )}

          {activeTab === "marketing" && (
            <Suspense fallback={<Spinner />}>
              <MarketingSettings
                serviceId={serviceId}
                initialSettings={service.marketing_settings}
              />
            </Suspense>
          )}

          {activeTab === "reports" && (
            <Suspense fallback={<Spinner />}>
              <PerformanceReport serviceId={serviceId} />
            </Suspense>
          )}

          {activeTab === "dependencies" && (
            <Suspense fallback={<Spinner />}>
              <DependencyManager
                serviceId={serviceId}
                initialPrerequisites={service.prerequisite_services || []}
                initialMandatoryAddons={service.mandatory_addons || []}
              />
            </Suspense>
          )}

          {activeTab === "locations" && (
            <Suspense fallback={<Spinner />}>
              <ServiceLocationsSection
                availableAtLocations={service.available_at_locations}
                locationPricing={service.location_pricing}
              />
            </Suspense>
          )}

          {activeTab === "audit" && (
            <Suspense fallback={<Spinner />}>
              <AuditLogViewer serviceId={serviceId} />
            </Suspense>
          )}
        </div>
      </Card>

      {/* Edit Service Modal */}
      <Suspense fallback={null}>
        <ServiceFormModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSuccess={() => {
            setIsEditModalOpen(false);
            refetch();
          }}
          service={service}
          availableStylists={stylists}
        />
      </Suspense>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title="Delete Service"
        description={`Are you sure you want to delete "${service?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={isProcessing}
      />

      {/* Duplicate Confirmation Modal */}
      <ConfirmationModal
        isOpen={isDuplicateModalOpen}
        onClose={() => setIsDuplicateModalOpen(false)}
        onConfirm={handleDuplicate}
        title="Duplicate Service"
        description={`Create a copy of "${service?.name}"?`}
        confirmText="Duplicate"
        cancelText="Cancel"
        isLoading={isProcessing}
      />

      {/* Save as Template Modal */}
      <ConfirmationModal
        isOpen={isSaveTemplateModalOpen}
        onClose={() => {
          setIsSaveTemplateModalOpen(false);
          setTemplateName("");
        }}
        onConfirm={handleSaveAsTemplate}
        title="Save as Template"
        description={
          <>
            <span className="text-sm text-muted-foreground block mb-2">
              Enter a name for this template:
            </span>
            <Input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="Template name"
              autoFocus
            />
          </>
        }
        confirmText="Save Template"
        cancelText="Cancel"
        isLoading={isProcessing}
      />

      {/* Image Lightbox */}
      {service?.photo_url && (
        <ImageLightbox
          src={service.photo_url}
          alt={service.name}
          isOpen={isImageLightboxOpen}
          onClose={() => setIsImageLightboxOpen(false)}
        />
      )}
    </div>
  );
}
