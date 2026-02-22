'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, ThumbsUp } from 'lucide-react';

interface ReviewCardProps {
  review: {
    _id: string;
    client_name: string;
    rating: number;
    comment?: string;
    created_at: string;
    booking_id?: string;
    service_name?: string;
    stylist_name?: string;
    helpful_votes?: string[];
  };
  showVerifiedBadge?: boolean;
  currentUserId?: string;
  onHelpfulVote?: (reviewId: string, isVoting: boolean) => Promise<void>;
}

export function ReviewCard({
  review,
  showVerifiedBadge = true,
  currentUserId,
  onHelpfulVote
}: ReviewCardProps) {
  const [isVoting, setIsVoting] = useState(false);
  const [helpfulVotes, setHelpfulVotes] = useState(review.helpful_votes || []);
  const [error, setError] = useState<string | null>(null);

  const isUserVoted = currentUserId && helpfulVotes.includes(currentUserId);
  const voteCount = helpfulVotes.length;

  const handleHelpfulVote = async () => {
    if (!currentUserId) {
      setError('Please log in to vote');
      return;
    }

    try {
      setIsVoting(true);
      setError(null);

      if (isUserVoted) {
        // Remove vote
        const response = await fetch(`/api/reviews/${review._id}/helpful`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          throw new Error('Failed to remove vote');
        }

        setHelpfulVotes(helpfulVotes.filter(id => id !== currentUserId));
      } else {
        // Add vote
        const response = await fetch(`/api/reviews/${review._id}/helpful`, {
          method: 'POST'
        });

        if (!response.ok) {
          throw new Error('Failed to vote');
        }

        setHelpfulVotes([...helpfulVotes, currentUserId]);
      }

      if (onHelpfulVote) {
        await onHelpfulVote(review._id, !isUserVoted);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to vote');
    } finally {
      setIsVoting(false);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            size={16}
            className={
              i < rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300'
            }
          />
        ))}
      </div>
    );
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="flex items-center gap-2 mb-2">
              {renderStars(review.rating)}
              {showVerifiedBadge && review.booking_id && (
                <Badge
                  variant="outline"
                  className="text-xs"
                  title="This review is from a verified purchase"
                >
                  ✓ Verified Purchase
                </Badge>
              )}
            </div>
            <p className="font-semibold text-gray-900">{review.client_name}</p>
            {review.service_name && review.stylist_name && (
              <p className="text-sm text-gray-600">
                {review.service_name} • {review.stylist_name}
              </p>
            )}
          </div>
          <p className="text-sm text-gray-500">
            {new Date(review.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </p>
        </div>
        {review.comment && (
          <p className="text-gray-700 text-sm leading-relaxed mb-4">{review.comment}</p>
        )}

        {/* Helpful Vote Section */}
        <div className="flex items-center gap-2 pt-3 border-t border-gray-200">
          <Button
            size="sm"
            variant={isUserVoted ? 'default' : 'outline'}
            onClick={handleHelpfulVote}
            disabled={isVoting}
            className="gap-2"
          >
            <ThumbsUp size={16} />
            {isVoting ? 'Voting...' : 'Helpful'}
          </Button>
          {voteCount > 0 && (
            <span className="text-xs text-gray-600">
              {voteCount} {voteCount === 1 ? 'person' : 'people'} found this helpful
            </span>
          )}
          {error && (
            <span className="text-xs text-red-600">{error}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
