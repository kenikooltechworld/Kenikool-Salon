import { Card } from "@/components/ui/card";
import { TableRowSkeleton } from "@/components/ui/skeleton";
import { UserIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useState } from "react";

interface StylistPerformance {
  stylist_id: string;
  stylist_name: string;
  total_bookings: number;
  total_revenue: number;
  percentage_contribution: number;
}

interface StylistPerformanceWidgetProps {
  serviceId: string;
}

export function StylistPerformanceWidget({
  serviceId,
}: StylistPerformanceWidgetProps) {
  const [sortBy, setSortBy] = useState<"revenue" | "bookings">("revenue");

  const { data, isLoading } = useQuery({
    queryKey: ["service-stylist-performance", serviceId],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/services/${serviceId}/stylist-performance`
      );
      return response.data;
    },
  });

  const stylists: StylistPerformance[] = data?.stylists || [];

  // Sort stylists
  const sortedStylists = [...stylists].sort((a, b) => {
    if (sortBy === "revenue") {
      return b.total_revenue - a.total_revenue;
    }
    return b.total_bookings - a.total_bookings;
  });

  if (isLoading) {
    return (
      <Card className="p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
          Stylist Performance
        </h2>
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <TableRowSkeleton key={i} />
          ))}
        </div>
      </Card>
    );
  }

  if (stylists.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          Stylist Performance
        </h2>
        <div className="text-center py-8">
          <UserIcon size={48} className="mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No stylist data available</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-foreground">
          Stylist Performance
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setSortBy("revenue")}
            className={`px-3 py-1 text-sm rounded-lg transition-all duration-200 cursor-pointer ${
              sortBy === "revenue"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-muted text-muted-foreground hover:bg-muted/80 hover:shadow-sm"
            }`}
          >
            By Revenue
          </button>
          <button
            onClick={() => setSortBy("bookings")}
            className={`px-3 py-1 text-sm rounded-lg transition-all duration-200 cursor-pointer ${
              sortBy === "bookings"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-muted text-muted-foreground hover:bg-muted/80 hover:shadow-sm"
            }`}
          >
            By Bookings
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {sortedStylists.map((stylist, index) => (
          <div key={stylist.stylist_id} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                  #{index + 1}
                </div>
                <div>
                  <p className="font-medium text-foreground">
                    {stylist.stylist_name}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {stylist.total_bookings} booking
                    {stylist.total_bookings !== 1 ? "s" : ""}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-foreground">
                  ₦{stylist.total_revenue.toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">
                  {(stylist.percentage_contribution || 0).toFixed(1)}% of total
                </p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary h-full transition-all duration-500 ease-out"
                style={{ width: `${stylist.percentage_contribution || 0}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-border">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Total Stylists</span>
          <span className="font-medium text-foreground">{stylists.length}</span>
        </div>
      </div>
    </Card>
  );
}
