import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMultiLocation } from "@/lib/api/hooks/useMultiLocation";

interface LocationDistributionReportProps {
  selectedLocationId?: string;
}

const MapPinIcon = () => (
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
      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
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

export const LocationDistributionReport: React.FC<
  LocationDistributionReportProps
> = ({ selectedLocationId }) => {
  const { distribution, loading, fetchDistribution } = useMultiLocation("");
  const [totalStaff, setTotalStaff] = useState(0);

  useEffect(() => {
    fetchDistribution(selectedLocationId);
  }, [selectedLocationId, fetchDistribution]);

  useEffect(() => {
    const total = distribution.reduce((sum, loc) => sum + loc.staff_count, 0);
    setTotalStaff(total);
  }, [distribution]);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-slate-500">Loading distribution...</p>
        </CardContent>
      </Card>
    );
  }

  if (distribution.length === 0) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-slate-500">
            No location data available
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPinIcon />
            Staff Distribution by Location
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {distribution.map((location) => {
              const percentage =
                totalStaff > 0 ? (location.staff_count / totalStaff) * 100 : 0;
              return (
                <div key={location.location_id} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <UsersIcon />
                      <span className="font-medium text-sm">
                        {location.location_name}
                      </span>
                    </div>
                    <span className="text-sm font-semibold">
                      {location.staff_count} staff
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-blue-500 h-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-600">
                    {percentage.toFixed(1)}% of total staff
                  </p>
                </div>
              );
            })}
          </div>

          <div className="mt-6 pt-4 border-t">
            <div className="flex justify-between items-center">
              <span className="font-medium">Total Staff</span>
              <span className="text-lg font-bold">{totalStaff}</span>
            </div>
            <div className="flex justify-between items-center mt-2">
              <span className="font-medium">Locations</span>
              <span className="text-lg font-bold">{distribution.length}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
