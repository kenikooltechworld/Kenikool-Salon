import { StarIcon, CheckIcon, XIcon, MessageSquareIcon, EditIcon, TrashIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { useState, useEffect } from "react";

interface Review {
  _id: string;
  client_name: string;
  rating: number;
  comment: string;
  status: "pending" | "approved" | "rejected";
  created_at: string;
  booking_id?: string;
  response?: {
    text: string;
    responder_name: string;
    responded_at: string;
  };
}

interface ReviewModerationListProps {
  reviews: Review[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onRespond?: (review: Review) => void;
  onEditResponse?: (review: Review) => void;
  onDeleteResponse?: (id: string) => void;
  onSelectionChange?: (selectedIds: Set<string>) => void;
}

export function ReviewModerationList({
  reviews,
  onApprove,
  onReject,
  onRespond,
  onEditResponse,
  onDeleteResponse,
  onSelectionChange,
}: ReviewModerationListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(false);

  // Notify parent of selection changes
  useEffect(() => {
    onSelectionChange?.(selectedIds);
  }, [selectedIds, onSelectionChange]);

  const handleSelectAll = (checked: boolean) => {
    setSelectAll(checked);
    if (checked) {
      setSelectedIds(new Set(reviews.map((r) => r._id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectReview = (reviewId: string, checked: boolean) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(reviewId);
    } else {
      newSelected.delete(reviewId);
    }
    setSelectedIds(newSelected);
    setSelectAll(newSelected.size === reviews.length && reviews.length > 0);
  };

  if (reviews.length === 0) {
    return (
      <div className="text-center py-12">
        <StarIcon
          size={48}
          className="mx-auto text-[var(--muted-foreground)] mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No reviews to moderate</h3>
        <p className="text-[var(--muted-foreground)]">
          All reviews have been processed
        </p>
      </div>
    );
  }

  const getBadgeVariant = (
    status: "pending" | "approved" | "rejected"
  ): "default" | "secondary" | "destructive" | "outline" | "accent" => {
    switch (status) {
      case "approved":
        return "secondary";
      case "rejected":
        return "destructive";
      case "pending":
      default:
        return "outline";
    }
  };

  return (
    <div className="space-y-3">
      {/* Select All Header */}
      <div className="flex items-center gap-3 px-4 py-2 bg-[var(--muted)] rounded-lg">
        <Checkbox
          checked={selectAll}
          onCheckedChange={handleSelectAll}
          aria-label="Select all reviews"
        />
        <span className="text-sm font-medium text-[var(--foreground)]">
          {selectedIds.size > 0
            ? `${selectedIds.size} selected`
            : "Select all reviews"}
        </span>
      </div>

      {reviews.map((review) => (
        <Card
          key={review._id}
          className={`p-4 hover:shadow-md transition-shadow ${
            selectedIds.has(review._id) ? "ring-2 ring-blue-500 bg-blue-50" : ""
          }`}
        >
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                <Checkbox
                  checked={selectedIds.has(review._id)}
                  onCheckedChange={(checked) =>
                    handleSelectReview(review._id, checked as boolean)
                  }
                  aria-label={`Select review from ${review.client_name}`}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <p className="font-semibold">{review.client_name}</p>
                    <Badge variant={getBadgeVariant(review.status)}>
                      {review.status}
                    </Badge>
                    {review.booking_id && (
                      <Badge
                        variant="outline"
                        className="text-xs"
                        title="This review is from a verified purchase"
                      >
                        ✓ Verified
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1 mb-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <StarIcon
                        key={star}
                        size={16}
                        className={
                          star <= review.rating
                            ? "text-[var(--warning)] fill-[var(--warning)]"
                            : "text-[var(--muted-foreground)]"
                        }
                      />
                    ))}
                    <span className="text-sm text-[var(--muted-foreground)] ml-2">
                      {review.rating}/5
                    </span>
                  </div>
                  <p className="text-sm text-[var(--foreground)]">
                    {review.comment}
                  </p>
                  <p className="text-xs text-[var(--muted-foreground)] mt-2">
                    {new Date(review.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Response Display */}
            {review.response && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium text-blue-900 flex items-center gap-1">
                    <MessageSquareIcon size={14} />
                    Response from {review.response.responder_name}
                  </p>
                  {onEditResponse || onDeleteResponse ? (
                    <div className="flex gap-1">
                      {onEditResponse && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onEditResponse(review)}
                          className="h-6 w-6 p-0"
                        >
                          <EditIcon size={14} />
                        </Button>
                      )}
                      {onDeleteResponse && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDeleteResponse(review._id)}
                          className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                        >
                          <TrashIcon size={14} />
                        </Button>
                      )}
                    </div>
                  ) : null}
                </div>
                <p className="text-sm text-blue-900">{review.response.text}</p>
                <p className="text-xs text-blue-700">
                  {new Date(review.response.responded_at).toLocaleString()}
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2 pt-3 border-t border-[var(--border)] flex-wrap">
              {review.status === "pending" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onApprove(review._id)}
                  >
                    <CheckIcon size={16} className="mr-1" />
                    Approve
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onReject(review._id)}
                  >
                    <XIcon size={16} className="mr-1" />
                    Reject
                  </Button>
                </>
              )}
              
              {review.status === "approved" && onRespond && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRespond(review)}
                  className="flex items-center gap-1"
                >
                  <MessageSquareIcon size={16} />
                  {review.response ? "Edit Response" : "Add Response"}
                </Button>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
