import { Modal } from "@/components/ui/modal";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DollarIcon,
  CalendarIcon,
  StarIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useStylistPerformance } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";

interface PerformanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  stylist: Stylist;
}

export function PerformanceModal({
  isOpen,
  onClose,
  stylist,
}: PerformanceModalProps) {
  const {
    data: performance,
    isLoading,
    error,
  } = useStylistPerformance(stylist.id);

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Performance - {stylist.name}
        </h2>
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : error ? (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Error loading performance data</h3>
              <p className="text-sm">{error.message}</p>
            </div>
          </Alert>
        ) : (
          <div className="space-y-4">
            {/* Overview Stats */}
            <div className="grid grid-cols-2 gap-4">
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    Total Revenue
                  </span>
                </div>
                <p className="text-2xl font-bold text-foreground">
                  ₦{(performance?.total_revenue || 0).toLocaleString()}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Commission: ₦
                  {(performance?.total_commission || 0).toLocaleString()}
                </p>
              </Card>

              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CalendarIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    Completed Services
                  </span>
                </div>
                <p className="text-2xl font-bold text-foreground">
                  {performance?.completed_services || 0}
                </p>
                <p className="text-xs text-muted-foreground mt-1">This month</p>
              </Card>
            </div>

            {/* Rating */}
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <StarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Average Rating
                </span>
              </div>
              <div className="flex items-center gap-2">
                <p className="text-2xl font-bold text-foreground">
                  {performance?.average_rating !== undefined &&
                  performance.average_rating > 0
                    ? performance.average_rating.toFixed(1)
                    : "0.0"}
                </p>
                {performance?.average_rating !== undefined &&
                  performance.average_rating > 0 && (
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <StarIcon
                          key={i}
                          size={16}
                          className={
                            i < Math.round(performance.average_rating)
                              ? "text-[var(--warning)] -[var(--warning)]"
                              : "text-muted-foreground"
                          }
                        />
                      ))}
                    </div>
                  )}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Based on {performance?.total_reviews || 0} reviews
              </p>
            </Card>

            {/* Rebooking Rate */}
            <div className="grid grid-cols-2 gap-4">
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUpIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    Rebooking Rate
                  </span>
                </div>
                <p className="text-2xl font-bold text-foreground">
                  {performance?.rebooking_rate !== undefined
                    ? `${performance.rebooking_rate.toFixed(0)}%`
                    : "N/A"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Clients who book again
                </p>
              </Card>

              {/* On-Time Completion Rate */}
              <Card className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CalendarIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    On-Time Completion
                  </span>
                </div>
                <p className="text-2xl font-bold text-foreground">
                  {performance?.on_time_completion_rate !== undefined
                    ? `${performance.on_time_completion_rate.toFixed(0)}%`
                    : "N/A"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Services completed on schedule
                </p>
              </Card>
            </div>

            {/* Top Services */}
            {performance?.top_services &&
              performance.top_services.length > 0 && (
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    Top Services
                  </h3>
                  <div className="space-y-2">
                    {performance.top_services
                      .slice(0, 5)
                      .map(
                        (service: {
                          id: string;
                          name: string;
                          count: number;
                        }) => (
                          <div
                            key={service.id}
                            className="flex items-center justify-between p-2 bg-[var(--muted)]/50 rounded-lg"
                          >
                            <span className="text-sm text-foreground">
                              {service.name}
                            </span>
                            <span className="text-sm font-medium text-foreground">
                              {service.count} bookings
                            </span>
                          </div>
                        )
                      )}
                  </div>
                </div>
              )}

            {/* Recent Activity */}
            {performance?.recent_bookings &&
              performance.recent_bookings.length > 0 && (
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    Recent Activity
                  </h3>
                  <div className="space-y-2">
                    {performance.recent_bookings
                      .slice(0, 5)
                      .map(
                        (booking: {
                          id: string;
                          client_name: string;
                          service_name: string;
                          booking_date: string;
                        }) => (
                          <div
                            key={booking.id}
                            className="flex items-center justify-between p-2 bg-[var(--muted)]/50 rounded-lg"
                          >
                            <div>
                              <p className="text-sm font-medium text-foreground">
                                {booking.client_name}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {booking.service_name}
                              </p>
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {new Date(
                                booking.booking_date
                              ).toLocaleDateString()}
                            </span>
                          </div>
                        )
                      )}
                  </div>
                </div>
              )}
          </div>
        )}
      </div>
    </Modal>
  );
}
