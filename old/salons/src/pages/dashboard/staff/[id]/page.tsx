import { lazy, Suspense, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { ImageLightbox } from "@/components/ui/image-lightbox";
import { ArrowLeftIcon, AlertTriangleIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useConfirmation } from "@/hooks/use-confirmation";
import { useDeleteStylist } from "@/lib/api/hooks/useStylists";
import { useStaffStore } from "@/lib/store/staffStore";
import type { Stylist } from "@/lib/api/types";

// Import components
import { StylistHeader } from "@/components/staff/stylist-header";
import { TabNavigation } from "@/components/staff/tab-navigation";
import { StatisticsCards } from "@/components/staff/statistics-cards";
import { PerformanceTab } from "@/components/staff/performance-tab";
import { CommissionTab } from "@/components/staff/commission-tab";
import { AttendanceTab } from "@/components/staff/attendance-tab";
import { ScheduleTab } from "@/components/staff/schedule-tab";
import { ServicesTab } from "@/components/staff/services-tab";
import { LocationsTab } from "@/components/staff/locations-tab";

// Lazy load heavy components
const StylistReviewsSection = lazy(() =>
  import("@/components/staff/stylist-reviews-section").then((mod) => ({
    default: mod.StylistReviewsSection,
  })),
);

const StaffFormModal = lazy(() =>
  import("@/components/staff").then((mod) => ({
    default: mod.StaffFormModal,
  })),
);

interface StylistDetails {
  stylist: Stylist;
  statistics?: {
    totalBookings: number;
    completedBookings: number;
    cancelledBookings: number;
    totalRevenue: number;
    averageRating?: number;
  };
}

interface AttendanceRecord {
  id: string;
  date: string;
  clock_in_time?: string;
  clock_out_time?: string;
  hours_worked: number;
  status: string;
}

export default function StylistDetailsPage() {
  const params = useParams();
  const navigate = useNavigate();
  const stylistId = params.id as string;
  const { confirm, ConfirmationDialog } = useConfirmation();
  const deleteStylistMutation = useDeleteStylist();

  // Zustand store
  const {
    activeTab,
    isEditModalOpen,
    isImageLightboxOpen,
    attendancePage,
    currentMonth,
    serviceNames,
    attendanceStatus,
    currentHoursWorked,
    currentTime,
    attendanceRecords,
    setActiveTab,
    setIsEditModalOpen,
    setIsImageLightboxOpen,
    setAttendancePage,
    setServiceNames,
    setAttendanceStatus,
    setCurrentHoursWorked,
    setCurrentTime,
    setAttendanceRecords,
  } = useStaffStore();

  const { data, isLoading, error, refetch } = useQuery<StylistDetails>({
    queryKey: ["stylist-details", stylistId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/stylists/${stylistId}`);
      if (response.data && response.data.id) {
        return { stylist: response.data };
      }
      return response.data;
    },
  });

  const handleBack = () => {
    navigate("/dashboard/staff");
  };

  const handleEdit = () => {
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
  };

  const handleDelete = async () => {
    const confirmed = await confirm({
      title: "Delete Staff Member",
      message:
        "Are you sure you want to delete this staff member? This action cannot be undone.",
      confirmText: "Delete",
      cancelText: "Cancel",
      variant: "danger",
    });

    if (!confirmed) return;

    try {
      await deleteStylistMutation.mutateAsync(stylistId);
      navigate("/dashboard/staff");
    } catch (error) {
      console.error("Error deleting stylist:", error);
    }
  };

  // Fetch service names
  const { data: serviceNamesData, isLoading: isLoadingServiceNames } = useQuery(
    {
      queryKey: ["service-names", data?.stylist?.assigned_services],
      queryFn: async () => {
        const names: Record<string, string> = {};
        for (const serviceId of data?.stylist?.assigned_services || []) {
          try {
            const response = await apiClient.get(`/api/services/${serviceId}`);
            names[serviceId] = response.data?.name || serviceId;
          } catch (err) {
            names[serviceId] = serviceId;
          }
        }
        return names;
      },
      enabled:
        activeTab === "services" && !!data?.stylist?.assigned_services?.length,
      staleTime: 10 * 60 * 1000,
    },
  );

  useEffect(() => {
    if (serviceNamesData) {
      setServiceNames(serviceNamesData);
    }
  }, [serviceNamesData, setServiceNames]);

  // Initialize attendance state from Zustand (already persisted)
  // No need for manual localStorage - Zustand handles it

  // Fetch attendance data
  const {
    data: attendanceQueryData,
    isLoading: isLoadingAttendance,
    refetch: refetchAttendance,
  } = useQuery({
    queryKey: ["stylist-attendance", stylistId, currentMonth],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/stylists/${stylistId}/attendance?month=${currentMonth}`,
      );
      return response.data || [];
    },
    enabled: !!stylistId,
    staleTime: 30000,
    gcTime: 5 * 60 * 1000,
  });

  // Update attendance data and status from backend
  useEffect(() => {
    if (attendanceQueryData && attendanceQueryData.length > 0) {
      setAttendanceRecords(attendanceQueryData);

      const today = new Date().toDateString();
      const todayRecord = attendanceQueryData.find((r: AttendanceRecord) => {
        const recordDate = new Date(r.date).toDateString();
        return recordDate === today;
      });

      let newStatus: "not_clocked_in" | "clocked_in" | "clocked_out" =
        "not_clocked_in";

      if (todayRecord && !todayRecord.clock_out_time) {
        newStatus = "clocked_in";
      } else if (todayRecord && todayRecord.clock_out_time) {
        newStatus = "clocked_out";
      }

      setAttendanceStatus(newStatus);
    }
  }, [attendanceQueryData, setAttendanceRecords, setAttendanceStatus]);

  // Update clock every second
  useEffect(() => {
    const clockTimer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(clockTimer);
  }, [setCurrentTime]);

  // Update hours worked every 30 seconds when clocked in
  useEffect(() => {
    if (activeTab === "attendance" && attendanceStatus === "clocked_in") {
      const hoursTimer = setInterval(async () => {
        try {
          const response = await apiClient.get(
            `/api/stylists/${stylistId}/current-hours`,
          );
          setCurrentHoursWorked(response.data?.hours_worked || 0);
        } catch (err) {
          console.error("Error fetching current hours:", err);
        }
      }, 30000);

      return () => clearInterval(hoursTimer);
    }
  }, [activeTab, stylistId, attendanceStatus, setCurrentHoursWorked]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading stylist</h3>
            <p className="text-sm">
              {error instanceof Error ? error.message : "Stylist not found"}
            </p>
          </div>
        </Alert>
        <Button onClick={handleBack}>
          <ArrowLeftIcon size={20} />
          Back to Staff
        </Button>
      </div>
    );
  }

  const { stylist, statistics } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Button
          variant="outline"
          onClick={handleBack}
          className="w-full sm:w-auto"
        >
          <ArrowLeftIcon size={16} className="sm:w-5 sm:h-5" />
          Back to Staff
        </Button>
      </div>

      {/* Stylist Header */}
      <StylistHeader
        stylist={stylist}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onPhotoClick={() => stylist.photo_url && setIsImageLightboxOpen(true)}
      />

      {/* Tab Navigation */}
      <div className="bg-background rounded-lg p-4">
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {/* Statistics Cards */}
      {statistics && <StatisticsCards statistics={statistics || null} />}

      {/* Tab Content */}
      {activeTab === "performance" && (
        <PerformanceTab statistics={statistics || null} />
      )}

      {activeTab === "commission" && (
        <CommissionTab stylist={stylist} statistics={statistics || null} />
      )}

      {activeTab === "attendance" && (
        <AttendanceTab
          stylistId={stylistId}
          attendanceRecords={attendanceRecords}
          isLoading={isLoadingAttendance}
          attendanceStatus={attendanceStatus}
          currentHoursWorked={currentHoursWorked}
          currentTime={currentTime}
          attendancePage={attendancePage}
          onPageChange={setAttendancePage}
          onStatusChange={setAttendanceStatus}
          onHoursChange={setCurrentHoursWorked}
          onRefetch={refetchAttendance}
        />
      )}

      {activeTab === "schedule" && <ScheduleTab stylist={stylist} />}

      {activeTab === "services" && (
        <ServicesTab
          stylist={stylist}
          serviceNames={serviceNames}
          isLoading={isLoadingServiceNames}
        />
      )}

      {activeTab === "locations" && <LocationsTab stylist={stylist} />}

      {/* Stylist Reviews Section */}
      <Suspense fallback={<Spinner />}>
        <StylistReviewsSection stylistId={stylistId} />
      </Suspense>

      {/* Edit Modal */}
      <Suspense fallback={null}>
        <StaffFormModal
          isOpen={isEditModalOpen}
          onClose={handleCloseEditModal}
          onSuccess={() => {
            refetch();
            handleCloseEditModal();
          }}
          stylist={stylist}
        />
      </Suspense>

      {/* Confirmation Dialog */}
      <ConfirmationDialog />

      {/* Image Lightbox */}
      {stylist.photo_url && (
        <ImageLightbox
          src={stylist.photo_url}
          alt={stylist.name}
          isOpen={isImageLightboxOpen}
          onClose={() => setIsImageLightboxOpen(false)}
        />
      )}
    </div>
  );
}
