import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/format";
import { StarIcon } from "@/components/icons";

export interface StaffReview {
  id: string;
  customerId: string;
  customerName: string;
  appointmentId: string;
  serviceName: string;
  rating: number; // 0-5
  feedback: string;
  appointmentDate: string;
  createdAt: string;
}

interface StaffReviewCardProps {
  review: StaffReview;
}

const ratingColors: Record<number, string> = {
  1: "text-destructive",
  2: "text-destructive/80",
  3: "text-warning",
  4: "text-warning",
  5: "text-success",
};

const ratingLabels: Record<number, string> = {
  1: "Poor",
  2: "Fair",
  3: "Good",
  4: "Very Good",
  5: "Excellent",
};

export function StaffReviewCard({ review }: StaffReviewCardProps) {
  const appointmentDate = new Date(review.appointmentDate);
  const createdDate = new Date(review.createdAt);

  return (
    <Card hover>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base">{review.customerName}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {review.serviceName}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <StarIcon
                  key={star}
                  size={16}
                  className={
                    star <= review.rating
                      ? ratingColors[review.rating]
                      : "text-muted-foreground"
                  }
                  fill={star <= review.rating ? "currentColor" : "none"}
                />
              ))}
            </div>
            <Badge variant="outline" className="text-xs">
              {ratingLabels[review.rating] || "No rating"}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {review.feedback && (
          <div>
            <p className="text-sm text-muted-foreground mb-1">Feedback</p>
            <p className="text-sm text-foreground">{review.feedback}</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p className="text-muted-foreground">Appointment Date</p>
            <p className="font-medium">{formatDate(appointmentDate)}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Submitted</p>
            <p className="font-medium">{formatDate(createdDate)}</p>
          </div>
        </div>

        <div className="pt-2 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Review ID: {review.id.slice(0, 8)}...
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
