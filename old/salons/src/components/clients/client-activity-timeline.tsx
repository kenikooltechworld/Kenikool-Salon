import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Calendar,
  MessageSquare,
  Star,
  Clock,
  Activity,
} from "@/components/icons";
import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";

interface ClientActivity {
  id: string;
  type: "booking" | "communication" | "review";
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface ClientActivityTimelineProps {
  clientId: string;
}

const activityIcons: Record<string, any> = {
  booking: Calendar,
  communication: MessageSquare,
  review: Star,
  default: Activity,
};

const activityColors: Record<string, string> = {
  booking: "bg-blue-500",
  communication: "bg-purple-500",
  review: "bg-pink-500",
  default: "bg-gray-500",
};

export function ClientActivityTimeline({
  clientId,
}: ClientActivityTimelineProps) {
  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ["client-activity", clientId],
      queryFn: async ({ pageParam = 0 }) => {
        const response = await apiClient.get(
          `/api/clients/${clientId}/activity`,
          {
            params: {
              offset: pageParam,
              limit: 20,
            },
          },
        );
        return response.data;
      },
      getNextPageParam: (lastPage, pages) => {
        if (lastPage.has_more) {
          return pages.length * 20;
        }
        return undefined;
      },
      initialPageParam: 0,
    });

  const activities = data?.pages.flatMap((page) => page.activities) || [];

  const getActivityIcon = (type: string) => {
    const Icon = activityIcons[type] || activityIcons.default;
    return Icon;
  };

  const getActivityColor = (type: string) => {
    return activityColors[type] || activityColors.default;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Activity Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">
            Loading timeline...
          </div>
        ) : activities.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No activities yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

              {/* Activities */}
              <div className="space-y-6">
                {activities.map((activity: ClientActivity) => {
                  const Icon = getActivityIcon(activity.type);
                  const color = getActivityColor(activity.type);

                  return (
                    <div key={activity.id} className="relative pl-12">
                      {/* Icon */}
                      <div
                        className={`absolute left-0 w-8 h-8 rounded-full ${color} flex items-center justify-center`}
                      >
                        <Icon className="h-4 w-4 text-white" />
                      </div>

                      {/* Content */}
                      <div className="bg-card border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-medium">{activity.title}</p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {format(new Date(activity.timestamp), "PPp")}
                            </p>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {activity.type}
                          </Badge>
                        </div>

                        {activity.description && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {activity.description}
                          </p>
                        )}

                        {/* Metadata */}
                        {activity.metadata &&
                          Object.keys(activity.metadata).length > 0 && (
                            <div className="mt-3 pt-3 border-t">
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                {Object.entries(activity.metadata).map(
                                  ([key, value]) => (
                                    <div key={key}>
                                      <span className="text-muted-foreground">
                                        {key}:{" "}
                                      </span>
                                      <span className="font-medium">
                                        {String(value)}
                                      </span>
                                    </div>
                                  ),
                                )}
                              </div>
                            </div>
                          )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Load More */}
            {hasNextPage && (
              <div className="text-center pt-4">
                <Button
                  variant="outline"
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                >
                  {isFetchingNextPage ? "Loading..." : "Load More"}
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
