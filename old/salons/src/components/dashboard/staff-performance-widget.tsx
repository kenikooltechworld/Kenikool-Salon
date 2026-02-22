import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Badge } from "@/components/ui/badge";
import { UserIcon, StarIcon } from "@/components/icons";

interface StaffMember {
  id: string;
  name: string;
  revenue: number;
  booking_count: number;
  rating: number;
  utilization: number;
}

interface StaffPerformanceWidgetProps {
  staff: StaffMember[];
  loading?: boolean;
  onStaffClick?: (staffId: string) => void;
}

export function StaffPerformanceWidget({
  staff,
  loading = false,
  onStaffClick,
}: StaffPerformanceWidgetProps) {
  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-right-4 duration-500"
      role="region"
      aria-label="Staff Performance Widget"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Staff Performance
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => (window.location.href = "/dashboard/staff")}
          className="transition-all duration-200 ease-out hover:scale-105"
          aria-label="View all staff members"
        >
          View All
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : staff.length === 0 ? (
        <div className="text-center py-8 animate-in fade-in-0 zoom-in-95 duration-300">
          <UserIcon size={48} className="mx-auto text-muted-foreground mb-2" />
          <p className="text-muted-foreground">No staff data available</p>
        </div>
      ) : (
        <div
          className="space-y-3"
          role="list"
          aria-label="Top performing staff members"
        >
          {staff.slice(0, 3).map((member, index) => (
            <div
              key={member.id}
              role="listitem"
              tabIndex={0}
              className="p-4 bg-[var(--muted)]/50 rounded-lg hover:bg-[var(--muted)] transition-all duration-300 ease-out hover:scale-[1.02] hover:shadow-sm transform will-change-transform cursor-pointer animate-in fade-in-0 slide-in-from-right-2 focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
              style={{ animationDelay: `${index * 50}ms` }}
              onClick={() => onStaffClick?.(member.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onStaffClick?.(member.id);
                }
              }}
              aria-label={`${member.name}, rating ${member.rating.toFixed(
                1
              )} stars, ${member.utilization.toFixed(
                0
              )}% utilized, ₦${member.revenue.toLocaleString()} revenue, ${
                member.booking_count
              } bookings`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className="p-2 bg-[var(--primary)]/10 rounded-lg transition-all duration-300 ease-out hover:bg-[var(--primary)]/20 hover:scale-110 transform will-change-transform"
                    aria-hidden="true"
                  >
                    <UserIcon size={20} className="text-[var(--primary)]" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{member.name}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <StarIcon
                        size={14}
                        className="text-[var(--warning)] -current"
                        aria-hidden="true"
                      />
                      <span className="text-sm text-muted-foreground">
                        {member.rating.toFixed(1)}
                        <span className="sr-only"> stars out of 5</span>
                      </span>
                    </div>
                  </div>
                </div>
                <Badge
                  variant="default"
                  aria-label={`${member.utilization.toFixed(
                    0
                  )} percent utilized`}
                >
                  {member.utilization.toFixed(0)}% utilized
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2 bg-background rounded">
                  <p className="text-xs text-muted-foreground">Revenue</p>
                  <p className="text-sm font-semibold text-foreground">
                    ₦{member.revenue.toLocaleString()}
                  </p>
                </div>
                <div className="p-2 bg-background rounded">
                  <p className="text-xs text-muted-foreground">Bookings</p>
                  <p className="text-sm font-semibold text-foreground">
                    {member.booking_count}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
