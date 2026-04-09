import { StaffReviewCard, type StaffReview } from "./StaffReviewCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RefreshCwIcon } from "@/components/icons";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

interface StaffReviewsListProps {
  reviews: StaffReview[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  emptyMessage?: string;
  sortBy?: "date" | "rating";
  onSortChange?: (sortBy: "date" | "rating") => void;
}

export function StaffReviewsList({
  reviews,
  isLoading = false,
  error,
  onRetry,
  emptyMessage = "No reviews available",
  sortBy = "date",
  onSortChange,
}: StaffReviewsListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 border border-destructive/50 rounded-lg bg-destructive/5">
        <p className="text-destructive font-medium mb-2">
          Unable to load reviews
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          {error || "Network error. Please try again."}
        </p>
        {onRetry && (
          <Button variant="outline" size="sm" onClick={onRetry}>
            <RefreshCwIcon size={14} className="mr-2" />
            Retry
          </Button>
        )}
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div className="text-center py-8 border border-border rounded-lg">
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  // Sort reviews based on current sortBy
  const sortedReviews = [...reviews].sort((a, b) => {
    if (sortBy === "date") {
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    } else {
      return b.rating - a.rating;
    }
  });

  return (
    <div className="space-y-4">
      {onSortChange && (
        <div className="flex justify-end">
          <div className="inline-flex rounded-md border border-input bg-background p-1">
            <Button
              variant={sortBy === "date" ? "default" : "ghost"}
              size="sm"
              onClick={() => onSortChange("date")}
              className="px-3"
            >
              Newest First
            </Button>
            <Button
              variant={sortBy === "rating" ? "default" : "ghost"}
              size="sm"
              onClick={() => onSortChange("rating")}
              className="px-3"
            >
              Highest Rated
            </Button>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {sortedReviews.map((review) => (
          <StaffReviewCard key={review.id} review={review} />
        ))}
      </div>

      <div className="text-center text-sm text-muted-foreground">
        Showing {sortedReviews.length} review
        {sortedReviews.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}

function CardSkeleton() {
  return (
    <Card className="border-border">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Skeleton className="h-5 w-32 mb-2" />
            <Skeleton className="h-4 w-24" />
          </div>
          <Skeleton className="h-6 w-16" />
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <div className="grid grid-cols-2 gap-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
        </div>
      </CardContent>
    </Card>
  );
}
