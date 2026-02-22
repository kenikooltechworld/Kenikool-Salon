import { StarIcon, ThumbsUpIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";

interface RatingAggregation {
  average_rating: number;
  total_reviews: number;
  rating_distribution: {
    [key: string]: number;
  };
}

interface ReviewStatsProps {
  aggregation: RatingAggregation | null;
}

export function ReviewStats({ aggregation }: ReviewStatsProps) {
  if (!aggregation || aggregation.total_reviews === 0) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <ThumbsUpIcon
            size={48}
            className="mx-auto text-[var(--muted-foreground)] mb-4"
          />
          <h3 className="text-lg font-semibold mb-2">No reviews yet</h3>
          <p className="text-[var(--muted-foreground)]">
            Reviews will appear here once clients start rating your services
          </p>
        </div>
      </Card>
    );
  }

  const maxCount = Math.max(
    ...Object.values(aggregation.rating_distribution),
    1
  );

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <StarIcon
              size={32}
              className="text-[var(--warning)] -[var(--warning)]"
            />
            <span className="text-4xl font-bold">
              {aggregation.average_rating.toFixed(1)}
            </span>
          </div>
          <p className="text-[var(--muted-foreground)]">
            Based on {aggregation.total_reviews} review
            {aggregation.total_reviews !== 1 ? "s" : ""}
          </p>
        </div>

        <div className="space-y-3">
          {[5, 4, 3, 2, 1].map((rating) => {
            const count = aggregation.rating_distribution[rating] || 0;
            const percentage = (count / maxCount) * 100;

            return (
              <div key={rating} className="flex items-center gap-3">
                <div className="flex items-center gap-1 w-16">
                  <span className="text-sm font-medium">{rating}</span>
                  <StarIcon
                    size={14}
                    className="text-[var(--warning)] -[var(--warning)]"
                  />
                </div>
                <div className="flex-1 bg-[var(--muted)] rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-[var(--warning)] h-full rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="text-sm text-[var(--muted-foreground)] w-12 text-right">
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
