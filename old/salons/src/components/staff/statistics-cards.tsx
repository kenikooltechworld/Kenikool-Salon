import { Card } from "@/components/ui/card";
import { DollarIcon, CalendarIcon, StarIcon } from "@/components/icons";

interface StylistStatistics {
  totalBookings: number;
  completedBookings: number;
  cancelledBookings: number;
  totalRevenue: number;
  averageRating?: number;
}

interface StatisticsCardsProps {
  statistics: StylistStatistics | null;
}

export function StatisticsCards({ statistics }: StatisticsCardsProps) {
  if (!statistics) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      <Card className="p-4 sm:p-6 hover:shadow-lg transition-all duration-300">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs sm:text-sm text-muted-foreground mb-1">
              Total Revenue
            </p>
            <p className="text-2xl sm:text-3xl font-bold text-foreground">
              ₦{(statistics.totalRevenue || 0).toLocaleString()}
            </p>
          </div>
          <div className="p-2 sm:p-3 bg-primary/10 rounded-lg">
            <DollarIcon size={20} className="sm:w-6 sm:h-6 text-primary" />
          </div>
        </div>
      </Card>

      <Card className="p-4 sm:p-6 hover:shadow-lg transition-all duration-300">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs sm:text-sm text-muted-foreground mb-1">
              Total Bookings
            </p>
            <p className="text-2xl sm:text-3xl font-bold text-foreground">
              {statistics.totalBookings || 0}
            </p>
          </div>
          <div className="p-2 sm:p-3 bg-primary/10 rounded-lg">
            <CalendarIcon size={20} className="sm:w-6 sm:h-6 text-primary" />
          </div>
        </div>
      </Card>

      <Card className="p-4 sm:p-6 hover:shadow-lg transition-all duration-300">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs sm:text-sm text-muted-foreground mb-1">
              Completed
            </p>
            <p className="text-2xl sm:text-3xl font-bold text-foreground">
              {statistics.completedBookings || 0}
            </p>
          </div>
          <div className="p-2 sm:p-3 bg-green-100 rounded-lg">
            <CalendarIcon size={20} className="sm:w-6 sm:h-6 text-green-600" />
          </div>
        </div>
      </Card>

      <Card className="p-4 sm:p-6 hover:shadow-lg transition-all duration-300">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs sm:text-sm text-muted-foreground mb-1">
              Avg Rating
            </p>
            <p className="text-2xl sm:text-3xl font-bold text-foreground">
              {statistics.averageRating
                ? statistics.averageRating.toFixed(1)
                : "N/A"}
            </p>
          </div>
          <div className="p-2 sm:p-3 bg-yellow-100 rounded-lg">
            <StarIcon size={20} className="sm:w-6 sm:h-6 text-yellow-600" />
          </div>
        </div>
      </Card>
    </div>
  );
}
