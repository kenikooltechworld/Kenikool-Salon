import { useState, lazy, Suspense } from "react";
import { useNavigate } from "react-router-dom";
// Image removed;
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  SearchIcon,
  UserIcon,
  AlertTriangleIcon,
  EditIcon,
  TrashIcon,
  DollarIcon,
  ChartIcon,
} from "@/components/icons";
import { useStylists, useDeleteStylist } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";
import { useConfirmation } from "@/hooks/use-confirmation";
import { useLocations } from "@/lib/api/hooks/useLocations";

// Lazy load modals
const StaffFormModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.StaffFormModal,
  })),
);
const ScheduleModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.ScheduleModal,
  })),
);
const PerformanceModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.PerformanceModal,
  })),
);
const CommissionModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.CommissionModal,
  })),
);
const AttendanceModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.AttendanceModal,
  })),
);
const ServiceAssignmentModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.ServiceAssignmentModal,
  })),
);
const EmergencyContactModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.EmergencyContactModal,
  })),
);
const LocationAssignmentModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.LocationAssignmentModal,
  })),
);

export default function StaffPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [isStaffModalOpen, setIsStaffModalOpen] = useState(false);
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [isPerformanceModalOpen, setIsPerformanceModalOpen] = useState(false);
  const [isCommissionModalOpen, setIsCommissionModalOpen] = useState(false);
  const [isAttendanceModalOpen, setIsAttendanceModalOpen] = useState(false);
  const [isServiceAssignmentModalOpen, setIsServiceAssignmentModalOpen] =
    useState(false);
  const [isEmergencyContactModalOpen, setIsEmergencyContactModalOpen] =
    useState(false);
  const [isLocationAssignmentModalOpen, setIsLocationAssignmentModalOpen] =
    useState(false);
  const [editingStylist, setEditingStylist] = useState<Stylist>();
  const [selectedStylist, setSelectedStylist] = useState<Stylist>();

  const { data: stylists = [], isLoading, error, refetch } = useStylists();
  const deleteStylistMutation = useDeleteStylist();
  const { confirm, ConfirmationDialog } = useConfirmation();
  const { data: locations = [] } = useLocations();

  // Ensure stylists is always an array
  const stylistsArray = Array.isArray(stylists) ? stylists : [];

  const filteredStylists = stylistsArray.filter((stylist: Stylist) =>
    stylist.name?.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleOpenStaffModal = (stylist?: Stylist) => {
    setEditingStylist(stylist);
    setIsStaffModalOpen(true);
  };

  const handleCloseStaffModal = () => {
    setEditingStylist(undefined);
    setIsStaffModalOpen(false);
  };

  const handleOpenScheduleModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsScheduleModalOpen(true);
  };

  const handleCloseScheduleModal = () => {
    setSelectedStylist(undefined);
    setIsScheduleModalOpen(false);
  };

  const handleOpenPerformanceModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsPerformanceModalOpen(true);
  };

  const handleClosePerformanceModal = () => {
    setSelectedStylist(undefined);
    setIsPerformanceModalOpen(false);
  };

  const handleOpenCommissionModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsCommissionModalOpen(true);
  };

  const handleCloseCommissionModal = () => {
    setSelectedStylist(undefined);
    setIsCommissionModalOpen(false);
  };

  const handleOpenAttendanceModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsAttendanceModalOpen(true);
  };

  const handleCloseAttendanceModal = () => {
    setSelectedStylist(undefined);
    setIsAttendanceModalOpen(false);
  };

  const handleOpenServiceAssignmentModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsServiceAssignmentModalOpen(true);
  };

  const handleCloseServiceAssignmentModal = () => {
    setSelectedStylist(undefined);
    setIsServiceAssignmentModalOpen(false);
  };

  const handleOpenEmergencyContactModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsEmergencyContactModalOpen(true);
  };

  const handleCloseEmergencyContactModal = () => {
    setSelectedStylist(undefined);
    setIsEmergencyContactModalOpen(false);
  };

  const handleOpenLocationAssignmentModal = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    setIsLocationAssignmentModalOpen(true);
  };

  const handleCloseLocationAssignmentModal = () => {
    setSelectedStylist(undefined);
    setIsLocationAssignmentModalOpen(false);
  };

  const handleDelete = async (id: string) => {
    const confirmed = await confirm({
      title: "Remove Staff Member",
      message:
        "Are you sure you want to remove this staff member? This action cannot be undone.",
      confirmText: "Remove",
      cancelText: "Cancel",
      variant: "danger",
    });

    if (!confirmed) return;

    try {
      await deleteStylistMutation.mutateAsync(id);
      refetch();
    } catch (error) {
      console.error("Error deleting stylist:", error);
    }
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading staff</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-4 sm:space-y-6 px-2 sm:px-0">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl font-bold text-foreground truncate">
            Staff
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground truncate">
            Manage your team and track performance
          </p>
        </div>
        <Button
          onClick={() => handleOpenStaffModal()}
          className="w-full sm:w-auto"
        >
          <PlusIcon size={16} className="sm:size-5" />
          <span className="ml-2">Add Staff</span>
        </Button>
      </div>

      {/* Search */}
      <Card className="p-2 sm:p-4">
        <div className="relative">
          <SearchIcon
            size={16}
            className="absolute left-2 sm:left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Search staff..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 sm:pl-10 text-sm"
          />
        </div>
      </Card>

      {/* Staff Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : filteredStylists.length === 0 ? (
        <Card className="p-6 sm:p-12">
          <div className="text-center">
            <UserIcon
              size={32}
              className="mx-auto text-muted-foreground mb-3 sm:mb-4 sm:size-12"
            />
            <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2">
              No staff members found
            </h3>
            <p className="text-xs sm:text-sm text-muted-foreground mb-4">
              {searchQuery
                ? "Try adjusting your search"
                : "Get started by adding your first staff member"}
            </p>
            {!searchQuery && (
              <Button
                onClick={() => handleOpenStaffModal()}
                className="w-full sm:w-auto"
              >
                <PlusIcon size={16} className="sm:size-5" />
                Add Staff
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
          {filteredStylists.map((stylist: Stylist) => (
            <Card
              key={stylist.id}
              className="overflow-hidden flex flex-col h-full"
            >
              {/* Photo */}
              <div className="relative w-full aspect-square sm:aspect-video bg-[var(--muted)]">
                {stylist.photo_url ? (
                  <img
                    src={stylist.photo_url}
                    alt={stylist.name}
                    className="w-full h-full object-cover"
                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, (max-width: 1280px) 33vw, 25vw"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <UserIcon
                      size={32}
                      className="sm:size-48 text-muted-foreground"
                    />
                  </div>
                )}
                <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                  <Badge
                    variant={stylist.is_active ? "default" : "destructive"}
                    className="text-xs"
                  >
                    {stylist.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </div>

              {/* Details */}
              <div className="p-2 sm:p-3 lg:p-4 flex-1 flex flex-col">
                <h3 className="font-semibold text-sm sm:text-base text-foreground mb-1 truncate">
                  {stylist.name}
                </h3>
                {stylist.bio && (
                  <p className="text-xs sm:text-sm text-muted-foreground mb-2 sm:mb-3 line-clamp-2">
                    {stylist.bio}
                  </p>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 gap-1 sm:gap-2 mb-2 sm:mb-3">
                  <div className="p-2 sm:p-3 bg-[var(--muted)]/50 rounded">
                    <div className="flex items-center gap-1 mb-1">
                      <DollarIcon
                        size={12}
                        className="sm:size-3 text-muted-foreground"
                      />
                      <span className="text-xs text-muted-foreground line-clamp-1">
                        Commission
                      </span>
                    </div>
                    <p className="font-semibold text-xs sm:text-sm text-foreground truncate">
                      {stylist.commission_value
                        ? stylist.commission_type === "percentage"
                          ? `${stylist.commission_value}%`
                          : `₦${stylist.commission_value.toLocaleString()}`
                        : "N/A"}
                    </p>
                  </div>
                  <div className="p-2 sm:p-3 bg-[var(--muted)]/50 rounded">
                    <div className="flex items-center gap-1 mb-1">
                      <ChartIcon
                        size={12}
                        className="sm:size-3 text-muted-foreground"
                      />
                      <span className="text-xs text-muted-foreground line-clamp-1">
                        Specialties
                      </span>
                    </div>
                    <p className="font-semibold text-xs sm:text-sm text-foreground">
                      {stylist.specialties?.length || 0}
                    </p>
                  </div>
                </div>

                {/* Actions - Only View, Edit, Delete */}
                <div className="space-y-1 sm:space-y-2 mt-auto">
                  <div className="grid grid-cols-2 gap-1">
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs h-8 sm:h-9 px-1 sm:px-2"
                      onClick={() => navigate(`/dashboard/staff/${stylist.id}`)}
                      title="View details"
                    >
                      <span>View</span>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs h-8 sm:h-9 px-1 sm:px-2"
                      onClick={() => handleOpenStaffModal(stylist)}
                      title="Edit"
                    >
                      <EditIcon size={12} className="sm:size-4 sm:mr-1" />
                      <span className="hidden sm:inline">Edit</span>
                    </Button>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-xs h-8 sm:h-9 px-1 sm:px-2 w-full"
                    onClick={() => handleDelete(stylist.id)}
                    title="Delete"
                  >
                    <TrashIcon size={12} className="sm:size-4" />
                    <span className="hidden sm:inline ml-1">Delete</span>
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Staff Form Modal */}
      <Suspense fallback={null}>
        <StaffFormModal
          isOpen={isStaffModalOpen}
          onClose={handleCloseStaffModal}
          onSuccess={refetch}
          stylist={editingStylist}
        />
      </Suspense>

      {/* Schedule Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <ScheduleModal
            isOpen={isScheduleModalOpen}
            onClose={handleCloseScheduleModal}
            onSuccess={refetch}
            stylist={selectedStylist}
          />
        </Suspense>
      )}

      {/* Performance Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <PerformanceModal
            isOpen={isPerformanceModalOpen}
            onClose={handleClosePerformanceModal}
            stylist={selectedStylist}
          />
        </Suspense>
      )}

      {/* Commission Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <CommissionModal
            isOpen={isCommissionModalOpen}
            onClose={handleCloseCommissionModal}
            stylist={selectedStylist}
          />
        </Suspense>
      )}

      {/* Attendance Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <AttendanceModal
            isOpen={isAttendanceModalOpen}
            onClose={handleCloseAttendanceModal}
            stylist={selectedStylist}
          />
        </Suspense>
      )}

      {/* Service Assignment Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <ServiceAssignmentModal
            isOpen={isServiceAssignmentModalOpen}
            onClose={handleCloseServiceAssignmentModal}
            onSuccess={refetch}
            stylist={selectedStylist}
          />
        </Suspense>
      )}

      {/* Emergency Contact Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <EmergencyContactModal
            isOpen={isEmergencyContactModalOpen}
            onClose={handleCloseEmergencyContactModal}
            staffId={selectedStylist.id}
            staffName={selectedStylist.name}
            userRole="manager"
            onUpdate={() => refetch()}
          />
        </Suspense>
      )}

      {/* Location Assignment Modal */}
      {selectedStylist && (
        <Suspense fallback={null}>
          <LocationAssignmentModal
            isOpen={isLocationAssignmentModalOpen}
            onClose={handleCloseLocationAssignmentModal}
            staffId={selectedStylist.id}
            staffName={selectedStylist.name}
            availableLocations={locations.map((loc: any) => ({
              id: loc._id || loc.id,
              name: loc.name,
              address: loc.address,
            }))}
            onUpdate={() => refetch()}
          />
        </Suspense>
      )}

      {/* Confirmation Dialog */}
      <ConfirmationDialog />
    </div>
  );
}
