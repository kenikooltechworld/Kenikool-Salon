import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  StarIcon,
  AlertTriangleIcon,
  MessageSquareIcon,
} from "@/components/icons";
import {
  useGetClientReviews,
  useGetClientReviewsStats,
  useRequestReview,
} from "@/lib/api/hooks/useClients";
import { useState } from "react";
import { ReviewRequestModal } from "./review-request-modal";

interface ClientReviewsSectionProps {
  clientId: string;
}

export function ClientReviewsSection({ clientId }: ClientReviewsSectionProps) {
  const {
    data: reviews,
    isLoading: reviewsLoading,
    error: reviewsError,
  } = useGetClientReviews(clientId);
  const { data: stats, isLoading: statsLoading } =
    useGetClientReviewsStats(clientId);
  const [showRequestModal, setShowRequestModal] = useState(false);

  if (reviewsLoading || statsLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  if (reviewsError || !reviews) {
    return (
      <Card className="p-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading reviews</h3>
            <p className="text-sm">
              {reviewsError?.message || "Reviews not available"}
            </p>
          </div>
        </Alert>
      </Card>
    );
  }

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <StarIcon
            key={star}
            size={16}
            className={
              star <= rating
                ? "fill-yellow-400 text-yellow-400"
                : "text-muted-foreground"
            }
          />
        ))}
      </div>
    );
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-foreground">
          Client Reviews
        </h2>
        <Button
          onClick={() => setShowRequestModal(true)}
          variant="outline"
          size="sm"
        >
          Request Review
        </Button>
      </div>

      {/* Review Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Average Rating */}
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-2">Average Rating</p>
            <div className="flex items-center gap-2">
              <p className="text-2xl font-bold text-foreground">
                {stats.average_rating.toFixed(1)}
              </p>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <StarIcon
                    key={star}
                    size={16}
                    className={
                      star <= Math.round(stats.average_rating)
                        ? "fill-yellow-400 text-yellow-400"
                        : "text-muted-foreground"
                    }
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Total Reviews */}
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-2">Total Reviews</p>
            <p className="text-2xl font-bold text-foreground">
              {stats.total_reviews}
            </p>
          </div>

          {/* Submission Rate */}
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-2">
              Submission Rate
            </p>
            <p className="text-2xl font-bold text-foreground">
              {(stats.submission_rate * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      )}

      {/* Reviews List */}
      {reviews.reviews && reviews.reviews.length > 0 ? (
        <div className="space-y-4">
          {reviews.reviews.map((review) => (
            <div
              key={review.id}
              className={`p-4 border rounded-lg ${
                review.is_flagged
                  ? "border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950"
                  : "border-border bg-muted/30"
              }`}
            >
              {/* Review Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {renderStars(review.rating)}
                    {review.is_flagged && (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded">
                        Flagged
                      </span>
                    )}
                  </div>
                  {review.service_name && (
                    <p className="text-sm text-muted-foreground">
                      Service: {review.service_name}
                    </p>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  {new Date(review.date).toLocaleDateString()}
                </p>
              </div>

              {/* Review Text */}
              <p className="text-sm text-foreground mb-3">{review.text}</p>

              {/* Response */}
              {review.response && (
                <div className="mt-3 p-3 bg-background rounded border border-border">
                  <div className="flex items-center gap-2 mb-1">
                    <MessageSquareIcon size={16} className="text-primary" />
                    <p className="text-xs font-semibold text-foreground">
                      Salon Response
                    </p>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {review.response}
                  </p>
                  {review.response_date && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(review.response_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <MessageSquareIcon
            size={32}
            className="mx-auto text-muted-foreground mb-2"
          />
          <p className="text-muted-foreground">No reviews yet</p>
          <p className="text-sm text-muted-foreground">
            Request a review to get feedback from this client
          </p>
        </div>
      )}

      {/* Review Request Modal */}
      {showRequestModal && (
        <ReviewRequestModal
          isOpen={showRequestModal}
          clientId={clientId}
          onClose={() => setShowRequestModal(false)}
        />
      )}
    </Card>
  );
}
