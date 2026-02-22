"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface StaffComparison {
  staff_id: string;
  staff_name: string;
  metrics: Record<string, any>;
  rankings?: Record<string, number>;
}

interface PerformanceComparisonProps {
  staffIds: string[];
  startDate?: Date;
  endDate?: Date;
}

export function PerformanceComparison({
  staffIds,
  startDate,
  endDate,
}: PerformanceComparisonProps) {
  const [selectedMetric, setSelectedMetric] = useState("revenue");

  const { data: comparison, isLoading } = useQuery({
    queryKey: ["performance-comparison", staffIds, startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate.toISOString());
      if (endDate) params.append("end_date", endDate.toISOString());
      staffIds.forEach((id) => params.append("staff_ids", id));

      const res = await fetch(`/api/staff/performance/compare?${params}`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Failed to fetch comparison");
      return res.json();
    },
  });

  const staffComparisons: StaffComparison[] =
    comparison?.data?.staff_comparison || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!staffComparisons || staffComparisons.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No comparison data available
          </p>
        </CardContent>
      </Card>
    );
  }

  const metrics = comparison?.data?.metrics || [
    "revenue",
    "bookings",
    "rating",
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance Comparison</CardTitle>
        <div className="flex gap-2 mt-4 flex-wrap">
          {metrics.map((metric: string) => (
            <Button
              key={metric}
              variant={selectedMetric === metric ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedMetric(metric)}
              className="capitalize"
            >
              {metric}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Staff Member</TableHead>
                <TableHead className="text-right">Rank</TableHead>
                <TableHead className="text-right">Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {staffComparisons.map((staff) => {
                const metricData = staff.metrics[selectedMetric];
                const rank = staff.rankings?.[selectedMetric] || "-";

                let displayValue = "-";
                if (metricData) {
                  if (selectedMetric === "revenue") {
                    displayValue = `$${metricData.total?.toFixed(2) || 0}`;
                  } else if (selectedMetric === "bookings") {
                    displayValue = metricData.total?.toString() || "0";
                  } else if (selectedMetric === "rating") {
                    displayValue = metricData.average?.toFixed(2) || "0";
                  } else if (selectedMetric === "utilization") {
                    displayValue = `${metricData.percentage?.toFixed(1) || 0}%`;
                  }
                }

                return (
                  <TableRow key={staff.staff_id}>
                    <TableCell className="font-medium">
                      {staff.staff_name}
                    </TableCell>
                    <TableCell className="text-right">
                      <Badge variant={rank === 1 ? "default" : "secondary"}>
                        #{rank}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      {displayValue}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
