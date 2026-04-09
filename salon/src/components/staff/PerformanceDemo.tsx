import { useState } from "react";
import { StaffPerformanceMetrics } from "./StaffPerformanceMetrics";
import { StaffReviewsList } from "./StaffReviewsList";
import {
  usePerformanceMetrics,
  usePerformanceReviews,
} from "@/hooks/usePerformanceMetrics";
import type { StaffReview } from "./StaffReviewCard";

export function PerformanceDemo() {
  const [sortBy, setSortBy] = useState<"date" | "rating">("date");

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

  const handleViewDetails = () => {
    console.log("View detailed report clicked");
    // In a real app, this would navigate to a detailed report page
  };

  const handleSortChange = (newSortBy: "date" | "rating") => {
    setSortBy(newSortBy);
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">Performance & Ratings Demo</h1>
        <p className="text-muted-foreground">
          This demo shows the performance metrics and reviews components working
          together.
        </p>
      </div>

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
            onViewDetails={handleViewDetails}
          />
        </div>

        {/* Reviews List */}
        <div className="lg:col-span-2">
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-2">Customer Reviews</h2>
              <p className="text-sm text-muted-foreground">
                Feedback from your customers
              </p>
            </div>

            <StaffReviewsList
              reviews={(reviews as StaffReview[]) || []}
              isLoading={reviewsLoading}
              error={reviewsError?.message}
              onRetry={refetchReviews}
              sortBy={sortBy}
              onSortChange={handleSortChange}
              emptyMessage="No reviews yet. Your reviews will appear here once customers provide feedback."
            />
          </div>
        </div>
      </div>

      <div className="pt-6 border-t border-border">
        <h3 className="text-lg font-medium mb-3">Component Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <h4 className="font-medium">StaffPerformanceMetrics</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Displays average rating with stars</li>
              <li>• Shows appointments completed</li>
              <li>• Customer satisfaction percentage</li>
              <li>• Loading and error states</li>
              <li>• Auto-refresh capability</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">StaffReviewsList</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Sort by date or rating</li>
              <li>• Loading skeletons</li>
              <li>• Error handling with retry</li>
              <li>• Empty state message</li>
              <li>• Responsive design</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">StaffReviewCard</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Star rating display</li>
              <li>• Customer and service info</li>
              <li>• Feedback text</li>
              <li>• Date information</li>
              <li>• Hover effects</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
