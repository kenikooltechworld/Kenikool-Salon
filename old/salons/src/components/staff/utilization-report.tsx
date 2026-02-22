import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useUtilizationReports } from "@/lib/api/hooks/useUtilizationReports";

interface UtilizationReportProps {
  staffId?: string;
}

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

const CheckIcon = () => (
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
      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

export const UtilizationReport: React.FC<UtilizationReportProps> = ({
  staffId,
}) => {
  const {
    loading,
    getStaffUtilization,
    getUnderutilizedStaff,
    getOverutilizedStaff,
    getAverageUtilization,
    getLocationComparison,
    getUtilizationTrends,
  } = useUtilizationReports();

  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0],
  );

  const [staffUtil, setStaffUtil] = useState<any>(null);
  const [underutilized, setUnderutilized] = useState<any[]>([]);
  const [overutilized, setOverutilized] = useState<any[]>([]);
  const [average, setAverage] = useState<any>(null);
  const [locations, setLocations] = useState<any[]>([]);
  const [trends, setTrends] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, [startDate, endDate]);

  const loadData = async () => {
    if (staffId) {
      const util = await getStaffUtilization(staffId, startDate, endDate);
      setStaffUtil(util);

      const trendData = await getUtilizationTrends(staffId, startDate, endDate);
      setTrends(trendData);
    } else {
      const [under, over, avg, locs] = await Promise.all([
        getUnderutilizedStaff(startDate, endDate),
        getOverutilizedStaff(startDate, endDate),
        getAverageUtilization(startDate, endDate),
        getLocationComparison(startDate, endDate),
      ]);

      setUnderutilized(under);
      setOverutilized(over);
      setAverage(avg);
      setLocations(locs);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-slate-500">
            Loading utilization data...
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Date Range Selector */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-2 gap-4">
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

      {/* Staff Utilization */}
      {staffUtil && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUpIcon />
              Staff Utilization
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Utilization Rate</p>
                <p className="text-3xl font-bold">
                  {staffUtil.utilization_rate.toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Bookings</p>
                <p className="text-3xl font-bold">{staffUtil.booking_count}</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Booked Hours</span>
                <span className="font-semibold">
                  {staffUtil.total_booked_hours.toFixed(1)}h
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-500 h-full"
                  style={{
                    width: `${Math.min(staffUtil.utilization_rate, 100)}%`,
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-600">
                <span>
                  Scheduled: {staffUtil.total_scheduled_hours.toFixed(1)}h
                </span>
                <span>Idle: {staffUtil.idle_hours.toFixed(1)}h</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trends */}
      {trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Utilization Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {trends.map((trend, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                >
                  <div>
                    <p className="text-sm font-medium">
                      {trend.period_start} to {trend.period_end}
                    </p>
                    <p className="text-xs text-slate-600">
                      {trend.booked_hours.toFixed(1)}h /{" "}
                      {trend.scheduled_hours.toFixed(1)}h
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">
                      {trend.utilization_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Average Utilization */}
      {average && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckIcon />
              Average Utilization
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-slate-600">Average Rate</p>
                <p className="text-3xl font-bold text-green-600">
                  {average.average_utilization.toFixed(1)}%
                </p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Staff Count</p>
                <p className="text-3xl font-bold">{average.staff_count}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Underutilized Staff */}
      {underutilized.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertIcon />
              Underutilized Staff ({underutilized.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {underutilized.map((staff, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{staff.staff_name}</p>
                    <p className="text-xs text-slate-600">
                      {staff.booked_hours.toFixed(1)}h /{" "}
                      {staff.scheduled_hours.toFixed(1)}h
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-orange-600">
                      {staff.utilization_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overutilized Staff */}
      {overutilized.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUpIcon />
              Overutilized Staff ({overutilized.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {overutilized.map((staff, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{staff.staff_name}</p>
                    <p className="text-xs text-slate-600">
                      {staff.booked_hours.toFixed(1)}h booked
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-red-600">
                      {staff.utilization_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Location Comparison */}
      {locations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Utilization by Location</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {locations.map((loc, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">
                      {loc.location_name}
                    </span>
                    <span className="text-sm font-semibold">
                      {loc.average_utilization.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-blue-500 h-full"
                      style={{
                        width: `${Math.min(loc.average_utilization, 100)}%`,
                      }}
                    />
                  </div>
                  <p className="text-xs text-slate-600">
                    {loc.staff_count} staff
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
