import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  StarIcon,
  AlertTriangleIcon,
  UserIcon,
  FilterIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import type { Review as ReviewType } from "@/lib/api/types";

interface Review extends ReviewType {
  _id: string;
}

interface RatingAggregation {
  average_rating: number;
  total_reviews: number;
  rating_distribution: {
    "1": number;
    "2": number;
    "3": number;
    "4": number;
    "5": number;
  };
}

interface StylistReviewsSectionProps {
  stylistId: string;
}

export function StylistReviewsSection({
  stylistId,
}: StylistReviewsSectionProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [aggregation, setAggregation] = useState<RatingAggregation | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterRating, setFilterRating] = useState<number | null>(null);

  useEffect(() => {
    loadReviews();
    loadAggregation();
  }, [stylistId, filterRating]);

  const loadReviews = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = {
        stylist_id: stylistId,
        status: "approved",
        limit: 10,
      };

      const response = await apiClient.get("/api/reviews", { params });
      let reviewsList = response.data.reviews || response.data || [];

      // Ensure it's an array
      if (!Array.isArray(reviewsList)) {
        reviewsList = [];
      }

      // Filter by rating if selected
      if (filterRating) {
        reviewsList = reviewsList.filter(
          (r: Review) => r.rating === filterRating,
        );
      }

      setReviews(reviewsList);
    } catch (err) {
      console.error("Error loading reviews:", err);
      // Don't show error for 404 - just means no reviews yet
      if ((err as any)?.response?.status !== 404) {
        setError("Failed to load reviews");
      }
      setReviews([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadAggregation = async () => {
    try {
      const response = await apiClient.get("/api/reviews/aggregation", {
        params: { stylist_id: stylistId },
      });
      setAggregation(response.data);
    } catch (err) {
      console.error("Error loading rating aggregation:", err);
      // Don't show error for 404 - just means no reviews yet
      setAggregation(null);
    }
  };

  const renderStars = (rating: number, size: number = 16) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <StarIcon
            key={star}
            size={size}
            className={
              star <= rating
                ? "text-yellow-500 fill-yellow-500"
                : "text-gray-300"
            }
          />
        ))}
      </div>
    );
  };

  const getRatingPercentage = (rating: number): number => {
    if (!aggregation || aggregation.total_reviews === 0) return 0;
    const count =
      aggregation.rating_distribution[
        rating.toString() as keyof typeof aggregation.rating_distribution
      ];
    return (count / aggregation.total_reviews) * 100;
  };

  if (isLoading && !aggregation) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
          <StarIcon size={20} className="text-yellow-500" />
          Customer Reviews
        </h3>
        <p className="text-sm text-muted-foreground mt-1">
          See what customers are saying about this stylist
        </p>
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      )}

      {/* Rating Summary */}
      {aggregation && (
        <Card className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Average Rating */}
            <div className="flex flex-col items-center justify-center">
              <div className="text-5xl font-bold text-foreground mb-2">
                {aggregation.average_rating.toFixed(1)}
              </div>
              {renderStars(Math.round(aggregation.average_rating), 24)}
              <p className="text-sm text-muted-foreground mt-2">
                Based on {aggregation.total_reviews} review
                {aggregation.total_reviews !== 1 ? "s" : ""}
              </p>
            </div>

            {/* Rating Distribution */}
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((rating) => (
                <div key={rating} className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      setFilterRating(filterRating === rating ? null : rating)
                    }
                    className={`flex items-center gap-1 text-sm cursor-pointer transition-all duration-200 ${
                      filterRating === rating
                        ? "text-primary font-semibold"
                        : "text-foreground hover:text-primary"
                    }`}
                  >
                    {rating}
                    <StarIcon size={14} className="text-yellow-500" />
                  </button>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-yellow-500 transition-all duration-300"
                      style={{ width: `${getRatingPercentage(rating)}%` }}
                    />
                  </div>
                  <span className="text-sm text-muted-foreground w-12 text-right">
                    {
                      aggregation.rating_distribution[
                        rating.toString() as keyof typeof aggregation.rating_distribution
                      ]
                    }
                  </span>
                </div>
              ))}
            </div>
          </div>

          {filterRating && (
            <div className="mt-4 pt-4 border-t border-border">
              <Badge
                variant="secondary"
                className="cursor-pointer"
                onClick={() => setFilterRating(null)}
              >
                <FilterIcon size={14} />
                Showing {filterRating}-star reviews • Click to clear
              </Badge>
            </div>
          )}
        </Card>
      )}

      {/* Reviews List */}
      {reviews.length === 0 ? (
        <Card className="p-12 text-center">
          <StarIcon size={48} className="mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">
            No Reviews Yet
          </h3>
          <p className="text-sm text-muted-foreground">
            {filterRating
              ? `No ${filterRating}-star reviews found. Try a different filter.`
              : "Be the first to review this stylist!"}
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <Card key={review._id} className="p-6">
              <div className="flex items-start gap-4">
                {/* Avatar */}
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <UserIcon size={24} className="text-primary" />
                </div>

                {/* Review Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-foreground">
                        {review.client_name}
                      </h4>
                      <p className="text-xs text-muted-foreground">
                        {new Date(review.created_at).toLocaleDateString(
                          "en-US",
                          {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          },
                        )}
                      </p>
                    </div>
                    {renderStars(review.rating)}
                  </div>

                  {review.comment && (
                    <p className="text-sm text-foreground mt-2">
                      {review.comment}
                    </p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Info Card */}
      {aggregation && aggregation.total_reviews > 0 && (
        <Card className="p-4 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <div className="flex gap-3">
            <StarIcon
              size={20}
              className="text-blue-600 flex-shrink-0 mt-0.5"
            />
            <div>
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                About Reviews
              </h4>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                All reviews are from verified customers who have completed
                services with this stylist. Reviews are moderated to ensure
                quality and authenticity.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
