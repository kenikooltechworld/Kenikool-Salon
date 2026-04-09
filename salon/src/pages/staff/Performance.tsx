import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  StarIcon,
  UsersIcon,
  CalendarIcon,
  TrendingUpIcon,
  RefreshCwIcon,
  AlertCircleIcon,
  FilterIcon,
  InfoIcon,
} from "@/components/icons";
import { StaffPerformanceMetrics } from "@/components/staff/StaffPerformanceMetrics";
import { StaffReviewsList } from "@/components/staff/StaffReviewsList";
import {
  usePerformanceMetrics,
  usePerformanceReviews,
} from "@/hooks/usePerformanceMetrics";

/**
 * Performance & Ratings page for staff members
 * Displays customer ratings, reviews, and performance metrics
 *
 * Features:
 * - Average rating score display
 * - Individual customer reviews with ratings
 * - Performance metrics (appointments completed, customer satisfaction)
 * - Default sort by date descending
 * - "No ratings" message when no data exists
 * - Responsive design for mobile devices
 * - Proper error handling and loading states
 *
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */
export default function Performance() {
  const [sortBy, setSortBy] = useState<"date" | "rating">("date");

  // Fetch performance data
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics,
  } = usePerformanceMetrics();

  const {
    data: reviews,
    isLoading: reviewsLoading,
    error: reviewsError,
    refetch: refetchReviews,
  } = usePerformanceReviews();

  const handleRefresh = () => {
    refetchMetrics();
    refetchReviews();
  };

  const handleSortChange = (newSortBy: "date" | "rating") => {
    setSortBy(newSortBy);
  };

  const isLoading = metricsLoading || reviewsLoading;
  const hasReviews = reviews && reviews.length > 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <StarIcon size={28} className="text-primary" />
            Performance & Ratings
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your performance metrics and customer feedback
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            disabled={isLoading}
            className="self-start sm:self-auto"
          >
            <RefreshCwIcon size={16} className="mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Performance Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Average Rating */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <StarIcon size={16} />
              Average Rating
            </CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : metricsError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {metrics?.averageRating?.toFixed(1) || "0.0"}
                  <span className="text-lg text-muted-foreground">/5</span>
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Based on {metrics?.totalReviews || 0} review
                  {metrics?.totalReviews !== 1 ? "s" : ""}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Total Reviews */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <UsersIcon size={16} />
              Total Reviews
            </CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : metricsError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {metrics?.totalReviews || 0}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Customer feedback received
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Appointments Completed */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CalendarIcon size={16} />
              Appointments Completed
            </CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : metricsError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {metrics?.appointmentsCompleted || 0}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Total completed appointments
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Customer Satisfaction */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUpIcon size={16} />
              Customer Satisfaction
            </CardTitle>
          </CardHeader>
          <CardContent>
            {metricsLoading ? (
              <div className="flex items-center gap-2">
                <Spinner size="sm" />
                <span className="text-sm text-muted-foreground">
                  Loading...
                </span>
              </div>
            ) : metricsError ? (
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={16} className="text-destructive" />
                <p className="text-sm text-destructive">Failed to load</p>
              </div>
            ) : (
              <div>
                <p className="text-2xl font-bold text-foreground">
                  {metrics?.customerSatisfaction || 0}%
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Satisfied customers
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics Component */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Metrics Card */}
        <div className="lg:col-span-1">
          <StaffPerformanceMetrics
            metrics={
              metrics || {
                averageRating: 0,
                totalReviews: 0,
                appointmentsCompleted: 0,
                customerSatisfaction: 0,
              }
            }
            isLoading={metricsLoading}
            error={metricsError?.message}
            onRetry={refetchMetrics}
          />
        </div>

        {/* Reviews List */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FilterIcon size={20} />
                Customer Reviews
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Feedback from your customers, sorted by{" "}
                {sortBy === "date" ? "newest first" : "highest rated"}
              </p>
            </CardHeader>
            <CardContent>
              <StaffReviewsList
                reviews={reviews || []}
                isLoading={reviewsLoading}
                error={reviewsError?.message}
                onRetry={refetchReviews}
                sortBy={sortBy}
                onSortChange={handleSortChange}
                emptyMessage="No ratings yet. Your reviews will appear here once customers provide feedback."
              />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Additional Performance Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <InfoIcon size={20} />
            Performance Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-foreground">
                Rating Distribution
              </h4>
              {metrics?.ratingDistribution ? (
                <div className="space-y-2">
                  {Object.entries(metrics.ratingDistribution)
                    .sort(([a], [b]) => parseInt(b) - parseInt(a))
                    .map(([rating, count]) => (
                      <div key={rating} className="flex items-center gap-3">
                        <div className="flex items-center gap-1 w-16">
                          <span className="text-sm font-medium">{rating}</span>
                          <StarIcon size={14} className="text-yellow-500" />
                        </div>
                        <div className="flex-1">
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary"
                              style={{
                                width: `${(count / metrics.totalReviews) * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                        <span className="text-sm text-muted-foreground w-8 text-right">
                          {count}
                        </span>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Rating distribution data not available
                </p>
              )}
            </div>
            <div className="space-y-3">
              <h4 className="font-medium text-foreground">Performance Tips</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-start gap-2 p-3 bg-muted/50 rounded-lg">
                  <StarIcon
                    size={16}
                    className="text-primary mt-0.5 flex-shrink-0"
                  />
                  <p className="text-muted-foreground">
                    Maintain consistent service quality to improve your average
                    rating
                  </p>
                </div>
                <div className="flex items-start gap-2 p-3 bg-muted/50 rounded-lg">
                  <UsersIcon
                    size={16}
                    className="text-primary mt-0.5 flex-shrink-0"
                  />
                  <p className="text-muted-foreground">
                    Encourage satisfied customers to leave reviews to build your
                    reputation
                  </p>
                </div>
                <div className="flex items-start gap-2 p-3 bg-muted/50 rounded-lg">
                  <TrendingUpIcon
                    size={16}
                    className="text-primary mt-0.5 flex-shrink-0"
                  />
                  <p className="text-muted-foreground">
                    Focus on customer satisfaction to increase repeat business
                    and referrals
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
