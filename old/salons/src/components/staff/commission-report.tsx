"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

interface CommissionReportProps {
  staffId?: string;
  startDate?: Date;
  endDate?: Date;
}

export function CommissionReport({
  staffId,
  startDate,
  endDate,
}: CommissionReportProps) {
  const { data: response, isLoading } = useQuery({
    queryKey: ["commission-report", staffId, startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate.toISOString());
      if (endDate) params.append("end_date", endDate.toISOString());
      if (staffId) params.append("staff_id", staffId);

      const res = await fetch(`/api/staff/commissions/reports?${params}`);
      if (!res.ok) throw new Error("Failed to fetch report");
      return res.json();
    },
  });

  const report = response?.data;

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  if (!report) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground text-center">
            No commission data available
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Total Commission
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${report.total_commission?.toFixed(2) || "0.00"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {report.commission_count || 0} commissions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              ${report.pending_commission?.toFixed(2) || "0.00"}
            </div>
            <Badge className="mt-2 bg-yellow-100 text-yellow-800">
              Pending
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Paid</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${report.paid_commission?.toFixed(2) || "0.00"}
            </div>
            <Badge className="mt-2 bg-green-100 text-green-800">Paid</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Disputed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ${report.disputed_commission?.toFixed(2) || "0.00"}
            </div>
            <Badge className="mt-2 bg-red-100 text-red-800">Disputed</Badge>
          </CardContent>
        </Card>
      </div>

      {/* By Staff Breakdown */}
      {report.by_staff && Object.keys(report.by_staff).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Commission by Staff</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(report.by_staff).map(
                ([id, staff]: [string, any]) => (
                  <div key={id} className="border rounded p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{staff.staff_name}</h4>
                      <span className="text-lg font-bold">
                        ${staff.total?.toFixed(2) || "0.00"}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Pending</p>
                        <p className="font-semibold">
                          ${staff.pending?.toFixed(2) || "0.00"}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Paid</p>
                        <p className="font-semibold">
                          ${staff.paid?.toFixed(2) || "0.00"}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Count</p>
                        <p className="font-semibold">{staff.count || 0}</p>
                      </div>
                    </div>
                  </div>
                ),
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
