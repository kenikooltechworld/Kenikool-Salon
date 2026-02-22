import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCapacityPlanning } from "@/lib/api/hooks/useCapacityPlanning";

interface CapacityPlannerProps {
  locationId?: string;
}

const AlertIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v2m0 4v2m0 4v2M7.08 6.06A9 9 0 1020.94 19.94M7.08 6.06l-2.83-2.83m13.86 13.86l2.83 2.83"
    />
  </svg>
);

const TrendingUpIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
    />
  </svg>
);

const UsersIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 4.354a4 4 0 110 8.048M12 4.354L8.646 7.708m6.708 0L15.354 7.708M9 20h6a2 2 0 002-2v-1a6 6 0 00-12 0v1a2 2 0 002 2z"
    />
  </svg>
);

export const CapacityPlanner: React.FC<CapacityPlannerProps> = ({
  locationId,
}) => {
  const {
    loading,
    getDailyCapacity,
    getUtilization,
    getLowStaffingDays,
    getBusyPeriods,
    getShiftSuggestions,
  } = useCapacityPlanning();

  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0],
  );
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0],
  );

  const [capacity, setCapacity] = useState<any>(null);
  const [utilization, setUtilization] = useState<any>(null);
  const [lowStaffing, setLowStaffing] = useState<any[]>([]);
  const [busyPeriods, setBusyPeriods] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, [selectedDate, startDate, endDate]);

  const loadData = async () => {
    const [cap, util, low, busy, sug] = await Promise.all([
      getDailyCapacity(selectedDate, locationId),
      getUtilization(selectedDate, locationId),
      getLowStaffingDays(startDate, endDate, undefined, locationId),
      getBusyPeriods(startDate, endDate, locationId),
      getShiftSuggestions(startDate, endDate, locationId),
    ]);

    setCapacity(cap);
    setUtilization(util);
    setLowStaffing(low);
    setBusyPeriods(busy);
    setSuggestions(sug);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-slate-500">Loading capacity data...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Date Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Capacity Planning</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Selected Date
              </label>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Start Date
              </label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date</label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Daily Utilization */}
      {utilization && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUpIcon />
              Daily Utilization - {selectedDate}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Utilization Rate</p>
                <p className="text-3xl font-bold">
                  {utilization.utilization_rate.toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Staff Count</p>
                <p className="text-3xl font-bold">{utilization.staff_count}</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Booked Hours</span>
                <span className="font-semibold">
                  {utilization.booked_hours.toFixed(1)}h
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-500 h-full"
                  style={{
                    width: `${Math.min(
                      (utilization.booked_hours /
                        utilization.total_capacity_hours) *
                        100,
                      100,
                    )}%`,
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-600">
                <span>
                  {utilization.booked_slots} / {utilization.available_slots}{" "}
                  slots
                </span>
                <span>{utilization.available_hours.toFixed(1)}h available</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Low Staffing Days */}
      {lowStaffing.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertIcon />
              Low Staffing Days ({lowStaffing.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {lowStaffing.map((day, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{day.date}</p>
                    <p className="text-xs text-slate-600">
                      {day.staff_count} staff (need {day.required_staff})
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-red-600">
                      -{day.shortage} staff
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Busy Periods */}
      {busyPeriods.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUpIcon />
              Busy Periods ({busyPeriods.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {busyPeriods.map((period, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{period.date}</p>
                    <p className="text-xs text-slate-600">
                      {period.booked_hours.toFixed(1)}h booked
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-orange-600">
                      {period.utilization_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Shift Suggestions */}
      {suggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UsersIcon />
              Shift Suggestions ({suggestions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {suggestions.map((sug, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{sug.date}</p>
                    <p className="text-xs text-slate-600">{sug.reason}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-green-600">
                      +{sug.suggested_shifts} shift
                      {sug.suggested_shifts > 1 ? "s" : ""}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
