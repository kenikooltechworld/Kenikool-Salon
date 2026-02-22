'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, Trash2, RotateCcw } from 'lucide-react';
import { Star } from 'lucide-react';

interface DeletedReview {
  _id: string;
  client_name: string;
  rating: number;
  comment?: string;
  service_name?: string;
  stylist_name?: string;
  deleted_at: string;
  deleted_by: string;
  deletion_reason: string;
  created_at: string;
}

export default function DeletedReviewsPage() {
  const [reviews, setReviews] = useState<DeletedReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [restoring, setRestoring] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    fetchDeletedReviews();
  }, [skip]);

  const fetchDeletedReviews = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `/api/reviews/deleted?skip=${skip}&limit=${limit}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch deleted reviews');
      }

      const data = await response.json();
      setReviews(data.reviews);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reviews');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (reviewId: string) => {
    try {
      setRestoring(reviewId);
      setError(null);

      const response = await fetch(`/api/reviews/${reviewId}/restore`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('Failed to restore review');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      fetchDeletedReviews();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to restore review');
    } finally {
      setRestoring(null);
    }
  };

  const handlePermanentDelete = async (reviewId: string) => {
    if (!confirm('Are you sure you want to permanently delete this review? This action cannot be undone.')) {
      return;
    }

    try {
      setDeleting(reviewId);
      setError(null);

      const response = await fetch(`/api/reviews/${reviewId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to delete review');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      fetchDeletedReviews();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete review');
    } finally {
      setDeleting(null);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            size={14}
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Deleted Reviews</h1>
          <p className="text-gray-600 mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Deleted Reviews</h1>
        <p className="text-gray-600 mt-2">
          View and manage soft-deleted reviews. You can restore or permanently delete them.
        </p>
      </div>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {success && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-green-700">Action completed successfully</p>
          </CardContent>
        </Card>
      )}

      {reviews.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <p className="text-gray-600">No deleted reviews found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <Card key={review._id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {renderStars(review.rating)}
                      <span className="text-sm font-semibold text-gray-900">
                        {review.client_name}
                      </span>
                    </div>
                    {review.service_name && review.stylist_name && (
                      <p className="text-sm text-gray-600 mb-2">
                        {review.service_name} • {review.stylist_name}
                      </p>
                    )}
                    {review.comment && (
                      <p className="text-gray-700 text-sm mb-3">{review.comment}</p>
                    )}
                    <div className="space-y-1 text-xs text-gray-600">
                      <p>
                        <strong>Deleted:</strong>{' '}
                        {new Date(review.deleted_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                      <p>
                        <strong>Reason:</strong> {review.deletion_reason}
                      </p>
                      <p>
                        <strong>Deleted by:</strong> {review.deleted_by}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRestore(review._id)}
                      disabled={restoring === review._id}
                      className="gap-2"
                    >
                      <RotateCcw size={16} />
                      {restoring === review._id ? 'Restoring...' : 'Restore'}
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handlePermanentDelete(review._id)}
                      disabled={deleting === review._id}
                      className="gap-2"
                    >
                      <Trash2 size={16} />
                      {deleting === review._id ? 'Deleting...' : 'Delete'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <p className="text-sm text-gray-600">
              Showing {skip + 1} to {Math.min(skip + limit, total)} of {total} reviews
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setSkip(Math.max(0, skip - limit))}
                disabled={skip === 0}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                onClick={() => setSkip(skip + limit)}
                disabled={skip + limit >= total}
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
