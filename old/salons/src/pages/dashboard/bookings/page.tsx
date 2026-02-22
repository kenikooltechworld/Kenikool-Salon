import { lazy, Suspense } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  PlusIcon,
  CalendarIcon,
  ListIcon,
  FilterIcon,
  ChartIcon,
} from "@/components/icons";
import { useUnifiedBookings } from "@/lib/api/hooks/useBookings";
import { GroupSubtype } from "@/lib/api/types";
import { useBookingStore } from "@/lib/store/bookingStore";
import {
  AdvancedSearchForm,
  BulkActionToolbar,
  NoShowPolicyEnforcer,
  AuditLogViewer,
  BookingCalendarView,
  BookingListView,
  WaitlistManagement,
  BookingAnalyticsDashboard,
  BookingDetailsModal,
} from "@/components/booking";

export default function BookingsPage() {
  const navigate = useNavigate();
  // Use Zustand store for state management
  const {
    viewMode,
    setViewMode,
    bookingTypeFilter,
    setBookingTypeFilter,
    groupSubtypeFilter,
    setGroupSubtypeFilter,
    setSelectedBookingId,
    selectedBooking,
    setSelectedBooking,
  } = useBookingStore();

  // Fetch unified bookings with filters
  const { data: unifiedBookingsData, isLoading } = useUnifiedBookings({
    booking_type: bookingTypeFilter === "all" ? undefined : bookingTypeFilter,
    group_subtype: groupSubtypeFilter,
  });

  // Calculate stats from unified bookings
  const stats = {
    total: unifiedBookingsData?.items.length || 0,
    individual:
      unifiedBookingsData?.items.filter((b) => b.bookingType === "individual")
        .length || 0,
    group:
      unifiedBookingsData?.items.filter((b) => b.bookingType === "group")
        .length || 0,
    bySubtype: {
      family:
        unifiedBookingsData?.items.filter(
          (b) => b.groupSubtype === GroupSubtype.FAMILY,
        ).length || 0,
      corporate:
        unifiedBookingsData?.items.filter(
          (b) => b.groupSubtype === GroupSubtype.CORPORATE,
        ).length || 0,
      wedding:
        unifiedBookingsData?.items.filter(
          (b) => b.groupSubtype === GroupSubtype.WEDDING,
        ).length || 0,
      birthday:
        unifiedBookingsData?.items.filter(
          (b) => b.groupSubtype === GroupSubtype.BIRTHDAY,
        ).length || 0,
      general:
        unifiedBookingsData?.items.filter(
          (b) => b.groupSubtype === GroupSubtype.GENERAL,
        ).length || 0,
    },
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-xl sm:text-2xl font-bold text-foreground truncate">
            Bookings
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Manage appointments and schedules
          </p>
        </div>
        <Button
          onClick={() => navigate("/dashboard/bookings/new")}
          className="w-full sm:w-auto shrink-0"
          size="sm"
        >
          <PlusIcon size={16} />
          <span className="ml-1 sm:ml-2">New</span>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
        <Card className="p-3 sm:p-4">
          <div className="text-xs sm:text-sm text-muted-foreground truncate">
            Total
          </div>
          <div className="text-lg sm:text-2xl font-bold mt-1">
            {stats.total}
          </div>
        </Card>
        <Card className="p-3 sm:p-4">
          <div className="text-xs sm:text-sm text-muted-foreground truncate">
            Individual
          </div>
          <div className="text-lg sm:text-2xl font-bold mt-1">
            {stats.individual}
          </div>
        </Card>
        <Card className="p-3 sm:p-4">
          <div className="text-xs sm:text-sm text-muted-foreground truncate">
            Group
          </div>
          <div className="text-lg sm:text-2xl font-bold mt-1">
            {stats.group}
          </div>
        </Card>
        <Card className="p-3 sm:p-4">
          <div className="text-xs sm:text-sm text-muted-foreground truncate">
            Family
          </div>
          <div className="text-lg sm:text-2xl font-bold mt-1">
            {stats.bySubtype.family}
          </div>
        </Card>
      </div>

      {/* Filters - Only show when not in analytics view */}
      {viewMode !== "analytics" && (
        <Card className="p-3 sm:p-4">
          <div className="space-y-3 sm:space-y-4">
            {/* Booking Type Filter */}
            <div className="flex flex-wrap items-center gap-1 sm:gap-2">
              <span className="text-xs sm:text-sm font-medium whitespace-nowrap">
                Type:
              </span>
              <div className="flex flex-wrap gap-1 sm:gap-2">
                <Button
                  variant={bookingTypeFilter === "all" ? "primary" : "outline"}
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => setBookingTypeFilter("all")}
                >
                  All
                </Button>
                <Button
                  variant={
                    bookingTypeFilter === "individual" ? "primary" : "outline"
                  }
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => setBookingTypeFilter("individual")}
                >
                  Indiv.
                </Button>
                <Button
                  variant={
                    bookingTypeFilter === "group" ? "primary" : "outline"
                  }
                  size="sm"
                  className="text-xs sm:text-sm px-2 sm:px-3"
                  onClick={() => setBookingTypeFilter("group")}
                >
                  Group
                </Button>
              </div>
            </div>

            {/* Group Subtype Filter (only show when group is selected) */}
            {(bookingTypeFilter === "group" || bookingTypeFilter === "all") && (
              <div className="flex flex-wrap items-center gap-1 sm:gap-2">
                <span className="text-xs sm:text-sm font-medium whitespace-nowrap">
                  Subtype:
                </span>
                <div className="flex flex-wrap gap-1 sm:gap-2">
                  <Button
                    variant={!groupSubtypeFilter ? "primary" : "outline"}
                    size="sm"
                    className="text-xs sm:text-sm px-2 sm:px-3"
                    onClick={() => setGroupSubtypeFilter(undefined)}
                  >
                    All
                  </Button>
                  <Button
                    variant={
                      groupSubtypeFilter === GroupSubtype.FAMILY
                        ? "primary"
                        : "outline"
                    }
                    size="sm"
                    className="text-xs sm:text-sm px-2 sm:px-3"
                    onClick={() => setGroupSubtypeFilter(GroupSubtype.FAMILY)}
                  >
                    Family
                  </Button>
                  <Button
                    variant={
                      groupSubtypeFilter === GroupSubtype.CORPORATE
                        ? "primary"
                        : "outline"
                    }
                    size="sm"
                    className="text-xs sm:text-sm px-2 sm:px-3"
                    onClick={() =>
                      setGroupSubtypeFilter(GroupSubtype.CORPORATE)
                    }
                  >
                    Corp.
                  </Button>
                  <Button
                    variant={
                      groupSubtypeFilter === GroupSubtype.WEDDING
                        ? "primary"
                        : "outline"
                    }
                    size="sm"
                    className="text-xs sm:text-sm px-2 sm:px-3"
                    onClick={() => setGroupSubtypeFilter(GroupSubtype.WEDDING)}
                  >
                    Wedding
                  </Button>
                  <Button
                    variant={
                      groupSubtypeFilter === GroupSubtype.BIRTHDAY
                        ? "primary"
                        : "outline"
                    }
                    size="sm"
                    className="text-xs sm:text-sm px-2 sm:px-3"
                    onClick={() => setGroupSubtypeFilter(GroupSubtype.BIRTHDAY)}
                  >
                    Birthday
                  </Button>
                  <Button
                    variant={
                      groupSubtypeFilter === GroupSubtype.GENERAL
                        ? "primary"
                        : "outline"
                    }
                    size="sm"
                    className="text-xs sm:text-sm px-2 sm:px-3"
                    onClick={() => setGroupSubtypeFilter(GroupSubtype.GENERAL)}
                  >
                    General
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* View Switcher */}
      <Card className="p-2 sm:p-4 overflow-x-auto">
        <div className="flex items-center gap-1 sm:gap-2 min-w-min sm:min-w-0">
          <Button
            variant={viewMode === "calendar" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("calendar")}
            title="Calendar view"
          >
            <CalendarIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">Calendar</span>
          </Button>
          <Button
            variant={viewMode === "list" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("list")}
            title="List view"
          >
            <ListIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">List</span>
          </Button>
          <Button
            variant={viewMode === "waitlist" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("waitlist")}
            title="Waitlist"
          >
            <FilterIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">Waitlist</span>
          </Button>
          <Button
            variant={viewMode === "analytics" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("analytics")}
            title="Analytics"
          >
            <ChartIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">Analytics</span>
          </Button>
          <Button
            variant={viewMode === "search" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("search")}
            title="Search"
          >
            <FilterIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">Search</span>
          </Button>
          <Button
            variant={viewMode === "audit" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("audit")}
            title="Audit log"
          >
            <ChartIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">Audit</span>
          </Button>
          <Button
            variant={viewMode === "bulk" ? "primary" : "outline"}
            size="sm"
            className="text-xs sm:text-sm px-2 sm:px-3 shrink-0"
            onClick={() => setViewMode("bulk")}
            title="Bulk actions"
          >
            <ListIcon size={14} className="sm:size-4" />
            <span className="hidden sm:inline ml-1">Bulk</span>
          </Button>
        </div>
      </Card>

      {/* Content */}
      <Suspense
        fallback={
          <div className="flex justify-center py-8 sm:py-12">
            <Spinner size="lg" />
          </div>
        }
      >
        {isLoading ? (
          <div className="flex justify-center py-8 sm:py-12">
            <Spinner size="lg" />
          </div>
        ) : (
          <>
            {viewMode === "calendar" && (
              <Card className="p-3 sm:p-4 md:p-6 overflow-x-auto">
                <BookingCalendarView
                  bookings={unifiedBookingsData?.items || []}
                  onBookingClick={(booking) => {
                    setSelectedBooking(booking);
                  }}
                />
              </Card>
            )}

            {viewMode === "list" && (
              <Card className="p-3 sm:p-4 md:p-6 overflow-x-auto">
                <BookingListView
                  bookings={unifiedBookingsData?.items || []}
                  onBookingClick={(booking) => {
                    setSelectedBooking(booking);
                  }}
                  onEdit={(booking) => {
                    setSelectedBookingId(booking.id);
                    navigate("/dashboard/bookings/new");
                  }}
                  onDelete={() => {
                    // Handle delete
                  }}
                />
              </Card>
            )}

            {viewMode === "waitlist" && (
              <Card className="p-3 sm:p-4 md:p-6">
                <WaitlistManagement
                  bookings={unifiedBookingsData?.items || []}
                />
              </Card>
            )}

            {viewMode === "analytics" && (
              <Card className="p-3 sm:p-4 md:p-6 overflow-x-auto">
                <BookingAnalyticsDashboard
                  bookings={unifiedBookingsData?.items || []}
                />
              </Card>
            )}

            {viewMode === "search" && (
              <Card className="p-3 sm:p-4 md:p-6">
                <AdvancedSearchForm onSearch={() => {}} />
              </Card>
            )}

            {viewMode === "audit" && (
              <Card className="p-3 sm:p-4 md:p-6 overflow-x-auto">
                <AuditLogViewer entries={[]} />
              </Card>
            )}

            {viewMode === "bulk" && (
              <Card className="p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4">
                <BulkActionToolbar selectedCount={0} />
                <NoShowPolicyEnforcer
                  customerId=""
                  noShowCount={0}
                  onPolicyApply={async () => {}}
                />
              </Card>
            )}
          </>
        )}
      </Suspense>

      {/* Booking Details Modal */}
      {selectedBooking && (
        <BookingDetailsModal
          booking={selectedBooking}
          isOpen={!!selectedBooking}
          onClose={() => setSelectedBooking(null)}
          onEdit={() => {
            setSelectedBookingId(selectedBooking.id);
            setSelectedBooking(null);
            navigate("/dashboard/bookings/new");
          }}
          onDelete={() => {
            // Handle delete
            setSelectedBooking(null);
          }}
        />
      )}
    </div>
  );
}
