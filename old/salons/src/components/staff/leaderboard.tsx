import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Trophy, TrendingUp } from "lucide-react";

interface LeaderboardEntry {
  rank: number;
  staff_id: string;
  staff_name: string;
  value: number;
  bookings?: number;
  revenue?: number;
  reviews?: number;
  rebookings?: number;
  total_bookings?: number;
}

interface LeaderboardProps {
  userRole: string;
}

export const Leaderboard: React.FC<LeaderboardProps> = ({ userRole }) => {
  const [category, setCategory] = useState("revenue");
  const [period, setPeriod] = useState("month");
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [category, period]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/staff/leaderboard?category=${category}&period=${period}`,
      );
      const data = await response.json();
      setLeaderboard(data.leaderboard || []);
    } catch (error) {
      console.error("Failed to fetch leaderboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const getMedalIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return "🥇";
      case 2:
        return "🥈";
      case 3:
        return "🥉";
      default:
        return null;
    }
  };

  const getValueLabel = () => {
    switch (category) {
      case "revenue":
        return "Revenue";
      case "bookings":
        return "Bookings";
      case "ratings":
        return "Avg Rating";
      case "rebookings":
        return "Rebooking %";
      default:
        return "Value";
    }
  };

  const formatValue = (value: number) => {
    switch (category) {
      case "revenue":
        return `$${value.toFixed(2)}`;
      case "bookings":
        return value.toString();
      case "ratings":
        return value.toFixed(2);
      case "rebookings":
        return `${value.toFixed(1)}%`;
      default:
        return value.toString();
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-5 h-5" />
            Staff Leaderboard
          </CardTitle>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Category</label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="revenue">Revenue</SelectItem>
                <SelectItem value="bookings">Bookings</SelectItem>
                <SelectItem value="ratings">Ratings</SelectItem>
                <SelectItem value="rebookings">Rebookings</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Period</label>
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
                <SelectItem value="quarter">This Quarter</SelectItem>
                <SelectItem value="year">This Year</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {loading ? (
          <p className="text-center text-slate-500 py-8">
            Loading leaderboard...
          </p>
        ) : leaderboard.length === 0 ? (
          <p className="text-center text-slate-500 py-8">No data available</p>
        ) : (
          <div className="space-y-2">
            {leaderboard.map((entry) => (
              <div
                key={entry.staff_id}
                className={`flex items-center justify-between p-3 rounded-lg transition ${
                  entry.rank <= 3
                    ? "bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200"
                    : "bg-slate-50 hover:bg-slate-100"
                }`}
              >
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-8 text-center">
                    {getMedalIcon(entry.rank) ? (
                      <span className="text-xl">
                        {getMedalIcon(entry.rank)}
                      </span>
                    ) : (
                      <span className="text-sm font-semibold text-slate-600">
                        #{entry.rank}
                      </span>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{entry.staff_name}</p>
                    <p className="text-xs text-slate-500">
                      {entry.bookings && `${entry.bookings} bookings`}
                      {entry.reviews && `${entry.reviews} reviews`}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="font-semibold text-sm">
                    {formatValue(entry.value)}
                  </p>
                  <p className="text-xs text-slate-500">{getValueLabel()}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {leaderboard.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-900">
            <p className="font-medium mb-1">Top Performers</p>
            <p className="text-xs">
              {leaderboard
                .slice(0, 3)
                .map((e) => e.staff_name)
                .join(", ")}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
