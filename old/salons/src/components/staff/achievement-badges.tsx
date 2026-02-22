import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Award, Lock } from "lucide-react";

interface Achievement {
  _id: string;
  achievement_type: string;
  title: string;
  description: string;
  icon_url?: string;
  earned_at: string;
}

interface AchievementBadgesProps {
  staffId: string;
  staffName: string;
}

export const AchievementBadges: React.FC<AchievementBadgesProps> = ({
  staffId,
  staffName,
}) => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAchievements();
  }, [staffId]);

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/staff/leaderboard/achievements/${staffId}`,
      );
      const data = await response.json();
      setAchievements(data.achievements || []);
    } catch (error) {
      console.error("Failed to fetch achievements:", error);
    } finally {
      setLoading(false);
    }
  };

  const getAchievementIcon = (type: string) => {
    const icons: Record<string, string> = {
      "10_bookings": "🎯",
      "50_bookings": "⭐",
      "100_bookings": "🏆",
      "250_bookings": "👑",
      "500_bookings": "💎",
      perfect_rating: "⭐⭐⭐⭐⭐",
      excellent_rating: "⭐⭐⭐⭐",
    };
    return icons[type] || "🏅";
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Award className="w-5 h-5" />
          Achievements
        </CardTitle>
        <p className="text-sm text-slate-500 mt-1">{staffName}</p>
      </CardHeader>

      <CardContent>
        {loading ? (
          <p className="text-center text-slate-500 py-8">
            Loading achievements...
          </p>
        ) : achievements.length === 0 ? (
          <div className="text-center py-8">
            <Lock className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="text-slate-500">No achievements earned yet</p>
            <p className="text-xs text-slate-400 mt-1">
              Keep working to unlock achievements!
            </p>
          </div>
        ) : (
          <ScrollArea className="h-96">
            <div className="grid grid-cols-2 gap-3 pr-4">
              {achievements.map((achievement) => (
                <div
                  key={achievement._id}
                  className="border rounded-lg p-3 hover:bg-slate-50 transition text-center"
                >
                  <div className="text-3xl mb-2">
                    {getAchievementIcon(achievement.achievement_type)}
                  </div>
                  <h3 className="font-semibold text-sm">{achievement.title}</h3>
                  <p className="text-xs text-slate-600 mt-1">
                    {achievement.description}
                  </p>
                  <p className="text-xs text-slate-400 mt-2">
                    {new Date(achievement.earned_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
};
