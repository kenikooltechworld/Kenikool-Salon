import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StarIcon } from "@/components/icons";
import { useState } from "react";

interface StylistReviewsDisplayProps {
  stylistId: string;
  stylistName: string;
}

interface Review {
  _id: string;
  rating: number;
  comment: string;
  clientName: string;
  createdAt: string;
}

export function StylistReviewsDisplay({
  stylistId,
  stylistName,
}: StylistReviewsDisplayProps) {
  const [filterRating, setFilterRating] = useState<number | null>(null);

  const { data: reviewsData, isLoading } = useQuery({
    queryKey: ["stylist-reviews", stylistId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/reviews/stylist/${stylistId}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const reviews = reviewsData?.reviews || [];
  const averageRating = reviewsData?.average_rating || 0;
  const totalReviews = reviewsData?.total_reviews || 0;

  const filteredReviews = filterRating
    ? reviews.filter((r: Review) => r.rating === filterRating)
    : reviews;

  const ratingDistribution = [5, 4, 3, 2, 1].map((rating) => ({
    rating,
    count: reviews.filter((r: Review) => r.rating === rating).length,
  }));

  if (isLoading) {
    return <div className="text-[var(--muted-foreground)]">Loading reviews...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Rating Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Customer Reviews</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Average Rating */}
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-[var(--foreground)]">
                {averageRating.toFixed(1)}
              </div>
              <div className="flex gap-1 justify-center mt-2">
                {[...Array(5)].map((_, i) => (
                  <StarIcon
                    key={i}
                    size={16}
                    className={
                      i < Math.round(averageRating)
                        ? "text-[var(--warning)] fill-[var(--warning)]"
                        : "text-[var(--muted)]"
                    }
                  />
                ))}
              </div>
              <p className="text-sm text-[var(--muted-foreground)] mt-2">
                Based on {totalReviews} review{totalReviews !== 1 ? "s" : ""}
              </p>
            </div>

            {/* Rating Distribution */}
            <div className="flex-1 space-y-2">
              {ratingDistribution.map(({ rating, count }) => (
                <div key={rating} className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      setFilterRating(filterRating === rating ? null : rating)
                    }
                    className="flex items-center gap-2 flex-1 hover:opacity-70 transition-opacity"
                  >
                    <span className="text-sm text-[var(--muted-foreground)] w-8">
                      {rating}★
                    </span>
                    <div className="flex-1 h-2 bg-[var(--muted)] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[var(--warning)]"
                        style={{
                          width: `${
                            totalReviews > 0
                              ? (count / totalReviews) * 100
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                    <span className="text-sm text-[var(--muted-foreground)] w-8 text-right">
                      {count}
                    </span>
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Filter Info */}
          {filterRating && (
            <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
              <p className="text-sm text-[var(--muted-foreground)]">
                Showing {filterRating}-star reviews
              </p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setFilterRating(null)}
              >
                Clear Filter
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Reviews List */}
      {filteredReviews.length > 0 ? (
        <div className="space-y-4">
          <h3 className="font-semibold text-[var(--foreground)]">
            Reviews ({filteredReviews.length})
          </h3>
          {filteredReviews.map((review: Review) => (
            <Card key={review._id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex gap-1 mb-1">
                      {[...Array(5)].map((_, i) => (
                        <StarIcon
                          key={i}
                          size={14}
                          className={
                            i < review.rating
                              ? "text-[var(--warning)] fill-[var(--warning)]"
                              : "text-[var(--muted)]"
                          }
                        />
                      ))}
                    </div>
                    <p className="font-medium text-[var(--foreground)]">
                      {review.clientName}
                    </p>
                  </div>
                  <Badge variant="secondary">
                    {review.rating} out of 5
                  </Badge>
                </div>
                <p className="text-sm text-[var(--foreground)] mb-3">
                  {review.comment}
                </p>
                <p className="text-xs text-[var(--muted-foreground)]">
                  {new Date(review.createdAt).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-[var(--muted-foreground)]">
            {filterRating
              ? `No ${filterRating}-star reviews yet`
              : "No reviews yet"}
          </p>
        </div>
      )}
    </div>
  );
}
