'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Trash2, CheckCircle } from 'lucide-react';
import { ReviewCard } from '@/components/reviews/review-card';

interface Flag {
  reason: string;
  details?: string;
  flagged_by: string;
  flagged_at: string;
}

interface FlaggedReview {
  _id: string;
  client_name: string;
  rating: number;
  comment?: string;
  created_at: string;
  service_name?: string;
  stylist_name?: string;
  flags: Flag[];
  status: string;
}

export default function FlaggedReviewsPage() {
  const [reviews, setReviews] = useState<FlaggedReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [unflaggingId, setUnflaggingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    fetchFlaggedReviews();
  }, []);

  const fetchFlaggedReviews = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/reviews?is_flagged=true&limit=100');
      
      if (!response.ok) {
        throw new Error('Failed to fetch flagged reviews');
      }

      const data = await response.json();
      setReviews(data.reviews || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reviews');
    } finally {
      setLoading(false);
    }
  };

  const handleUnflag = async (reviewId: string) => {
    try {
      setUnflaggingId(reviewId);
      const response = await fetch(`/api/reviews/${reviewId}/flag`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to unflag review');
      }

      // Remove from list
      setReviews(reviews.filter(r => r._id !== reviewId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unflag review');
    } finally {
      setUnflaggingId(null);
    }
  };

  const handleDelete = async (reviewId: string) => {
    if (!confirm('Are you sure you want to delete this review?')) {
      return;
    }

    try {
      setDeletingId(reviewId);
      const response = await fetch(`/api/reviews/${reviewId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'deleted' })
      });

      if (!response.ok) {
        throw new Error('Failed to delete review');
      }

      // Remove from list
      setReviews(reviews.filter(r => r._id !== reviewId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete review');
    } finally {
      setDeletingId(null);
    }
  };

  const getFlagReasonLabel = (reason: string) => {
    const labels: Record<string, string> = {
      spam: 'Spam',
      offensive: 'Offensive',
      fake: 'Fake Review',
      other: 'Other'
    };
    return labels[reason] || reason;
  };

  const getFlagReasonColor = (reason: string) => {
    const colors: Record<string, string> = {
      spam: 'bg-blue-100 text-blue-800',
      offensive: 'bg-red-100 text-red-800',
      fake: 'bg-yellow-100 text-yellow-800',
      other: 'bg-gray-100 text-gray-800'
    };
    return colors[reason] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Flagged Reviews</h1>
          <p className="text-gray-600 mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Flagged Reviews</h1>
        <p className="text-gray-600 mt-2">
          Manage reviews that have been flagged by users or moderators
        </p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {reviews.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900">No flagged reviews</p>
            <p className="text-sm text-gray-600 mt-1">
              All reviews are in good standing
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
                {reviews.length} Flagged Review{reviews.length !== 1 ? 's' : ''}
              </CardTitle>
              <CardDescription>
                Review and take action on flagged content
              </CardDescription>
            </CardHeader>
          </Card>

          {reviews.map(review => (
            <Card key={review._id} className="border-amber-200">
              <CardContent className="pt-6 space-y-4">
                {/* Review Content */}
                <ReviewCard review={review} showVerifiedBadge={false} />

                {/* Flags Section */}
                <div className="bg-amber-50 rounded-lg p-4 space-y-3">
                  <h4 className="font-semibold text-sm text-amber-900">
                    Flags ({review.flags.length})
                  </h4>

                  <div className="space-y-2">
                    {review.flags.map((flag, index) => (
                      <div key={index} className="bg-white rounded p-3 border border-amber-200">
                        <div className="flex items-start justify-between mb-2">
                          <Badge className={getFlagReasonColor(flag.reason)}>
                            {getFlagReasonLabel(flag.reason)}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {new Date(flag.flagged_at).toLocaleDateString()}
                          </span>
                        </div>

                        {flag.details && (
                          <p className="text-sm text-gray-700 mb-2">
                            {flag.details}
                          </p>
                        )}

                        <p className="text-xs text-gray-500">
                          Flagged by: {flag.flagged_by}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 justify-end pt-4 border-t">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleUnflag(review._id)}
                    disabled={unflaggingId === review._id}
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {unflaggingId === review._id ? 'Unflagging...' : 'Unflag'}
                  </Button>

                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDelete(review._id)}
                    disabled={deletingId === review._id}
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    {deletingId === review._id ? 'Deleting...' : 'Delete'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
