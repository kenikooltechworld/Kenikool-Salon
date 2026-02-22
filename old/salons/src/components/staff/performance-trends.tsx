"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface TrendDataPoint {
  date?: string;
  week?: number;
  month?: string;
  value: number;
}

interface PerformanceTrendsProps {
  staffId: string;
  staffName: string;
  metric?: string;
  days?: number;
}

export function PerformanceTrends({
  staffId,
  staffName,
  metric = "revenue",
  days = 30,
}: PerformanceTrendsProps) {
  const [period, setPeriod] = useState("daily");

  const { data: trends, isLoading } = useQuery({
    queryKey: ["performance-trends", staffId, metric, period, days],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append("metric", metric);
      params.append("period", period);
      params.append("days", days.toString());

      const res = await fetch(
        `/api/staff/performance/trends/${staffId}?${params}`,
      );
      if (!res.ok) throw new Error("Failed to fetch trends");
      return res.json();
    },
  });

  const dataPoints: TrendDataPoint[] = trends?.data?.data_points || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!dataPoints || dataPoints.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No trend data available
          </p>
        </CardContent>
      </Card>
    );
  }

  // Find max value for scaling
  const maxValue = Math.max(...dataPoints.map((d) => d.value), 1);
  const minValue = Math.min(...dataPoints.map((d) => d.value), 0);
  const range = maxValue - minValue || 1;

  // Get label for each data point
  const getLabel = (point: TrendDataPoint) => {
    if (point.date) {
      return new Date(point.date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      });
    } else if (point.week) {
      return `W${point.week}`;
    } else if (point.month) {
      return point.month;
    }
    return "";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="capitalize">{metric} Trends</CardTitle>
          <div className="flex gap-2">
            {["daily", "weekly", "monthly"].map((p) => (
              <Button
                key={p}
                variant={period === p ? "default" : "outline"}
                size="sm"
                onClick={() => setPeriod(p)}
                className="capitalize"
              >
                {p}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Simple bar chart */}
          <div className="flex items-end gap-1 h-48">
            {dataPoints.map((point, idx) => {
              const height = ((point.value - minValue) / range) * 100;
              return (
                <div
                  key={idx}
                  className="flex-1 flex flex-col items-center gap-1 group"
                >
                  <div
                    className="w-full bg-primary rounded-t transition-all hover:bg-primary/80"
                    style={{ height: `${Math.max(height, 5)}%` }}
                    title={`${point.value}`}
                  />
                  <span className="text-xs text-muted-foreground text-center truncate w-full">
                    {getLabel(point)}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t">
            <div>
              <p className="text-xs text-muted-foreground">Average</p>
              <p className="text-lg font-semibold">
                {(
                  dataPoints.reduce((sum, p) => sum + p.value, 0) /
                  dataPoints.length
                ).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Highest</p>
              <p className="text-lg font-semibold">
                {Math.max(...dataPoints.map((p) => p.value)).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Lowest</p>
              <p className="text-lg font-semibold">
                {Math.min(...dataPoints.map((p) => p.value)).toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
