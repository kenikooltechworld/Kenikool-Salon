import { useState } from "react";
import { Card, Button, Label } from "@/components/ui";
import { StarIcon } from "@/components/icons";

interface ReviewFormProps {
  bookingId: string;
  onSubmit?: () => void;
}

export default function ReviewForm({ bookingId, onSubmit }: ReviewFormProps) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [feedback, setFeedback] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) {
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(
        `/api/public/bookings/reviews`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            booking_id: bookingId,
            rating,
            feedback: feedback || "",
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to submit review");
      }

      setSubmitted(true);
      onSubmit?.();
    } catch (error) {
      console.error("Error submitting review:", error);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <Card className="p-6 text-center">
        <h3 className="text-xl font-semibold mb-2">Thank You!</h3>
        <p className="text-muted-foreground">
          Your review has been submitted successfully.
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-xl font-semibold mb-4">Leave a Review</h3>
      <p className="text-sm text-muted-foreground mb-4">
        How was your experience? We&apos;d love to hear your feedback.
      </p>

      <div className="space-y-4">
        <div>
          <Label>Rating</Label>
          <div className="flex gap-1 mt-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                className="p-1"
              >
                <StarIcon
                  size={28}
                  className={
                    star <= (hoverRating || rating)
                      ? "text-yellow-400 fill-yellow-400"
                      : "text-gray-300"
                  }
                />
              </button>
            ))}
          </div>
        </div>

        <div>
          <Label>Your Feedback</Label>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Tell us about your experience..."
            className="flex min-h-[80px] w-full rounded-md border border-[var(--input)] bg-[var(--background)] px-3 py-2 text-sm ring-offset-[var(--background)] placeholder:text-[var(--muted-foreground)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            maxLength={1000}
          />
        </div>

        <Button
          onClick={handleSubmit}
          disabled={rating === 0 || submitting}
          className="w-full"
        >
          {submitting ? "Submitting..." : "Submit Review"}
        </Button>
      </div>
    </Card>
  );
}
