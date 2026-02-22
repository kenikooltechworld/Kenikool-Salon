import { Card } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  TrophyIcon,
  DollarIcon,
  UsersIcon,
  StarIcon,
} from "@/components/icons";

interface StaffPerformance {
  stylist_id: string;
  stylist_name: string;
  stylist_photo?: string;
  total_bookings: number;
  total_revenue: number;
  average_rating?: number;
  clients_served?: number;
}

interface StaffLeaderboardProps {
  staff: StaffPerformance[];
}

export function StaffLeaderboard({ staff }: StaffLeaderboardProps) {
  // Sort staff by revenue
  const sortedStaff = [...staff].sort(
    (a, b) => b.total_revenue - a.total_revenue
  );

  const getMedalColor = (index: number) => {
    switch (index) {
      case 0:
        return "text-yellow-500";
      case 1:
        return "text-gray-400";
      case 2:
        return "text-orange-600";
      default:
        return "text-muted-foreground";
    }
  };

  return (
    <Card className="p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Staff Leaderboard
        </h2>
        <p className="text-sm text-muted-foreground">
          Top performers by revenue
        </p>
      </div>

      {sortedStaff.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          No staff data available
        </div>
      ) : (
        <div className="space-y-4">
          {sortedStaff.slice(0, 5).map((member, index) => (
            <div
              key={member.stylist_id}
              className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors"
            >
              {/* Rank */}
              <div className="flex items-center justify-center w-8">
                {index < 3 ? (
                  <TrophyIcon size={20} className={getMedalColor(index)} />
                ) : (
                  <span className="text-sm font-semibold text-muted-foreground">
                    {index + 1}
                  </span>
                )}
              </div>

              {/* Avatar */}
              <Avatar
                src={member.stylist_photo}
                alt={member.stylist_name}
                size="md"
              />

              {/* Info */}
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-foreground truncate">
                  {member.stylist_name}
                </h3>
                <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <DollarIcon size={14} />
                    <span>₦{member.total_revenue.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <UsersIcon size={14} />
                    <span>{member.total_bookings} bookings</span>
                  </div>
                  {member.average_rating && member.average_rating > 0 && (
                    <div className="flex items-center gap-1">
                      <StarIcon
                        size={14}
                        className="fill-yellow-500 text-yellow-500"
                      />
                      <span>{member.average_rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Badge for top 3 */}
              {index === 0 && (
                <Badge variant="primary" className="bg-yellow-500 text-white">
                  Top Performer
                </Badge>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
