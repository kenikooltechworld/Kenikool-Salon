'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Star, ChevronLeft, ChevronRight } from 'lucide-react';
import { ReviewCard } from '@/components/reviews/review-card';

interface Review {
  _id: string;
  client_name: string;
  rating: number;
  comment: string;
  created_at: string;
  booking_id?: string;
  service_name: string;
  stylist_name: string;
}

interface RatingAggregation {
  average_rating: number;
  total_reviews: number;
  rating_distribution: Record<string, number>;
}

interface PageProps {
  params: {
    id: string;
  };
}

const RATING_COLORS = {
  '1': '#ef4444',
  '2': '#f97316',
  '3': '#eab308',
  '4': '#84cc16',
  '5': '#22c55e'
};

export default function PublicReviewsPage({ params }: PageProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [aggregation, setAggregation] = useState<RatingAggregation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalReviews, setTotalReviews] = useState(0);
  const [sortBy, setSortBy] = useState<'created_at' | 'rating'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const pageSize = 10;
  const tenantId = params.id;

  useEffect(() => {
    fetchReviews();
    fetchAggregation();
  }, [currentPage, sortBy, sortOrder, tenantId]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const skip = currentPage * pageSize;
      const response = await fetch(
        `/api/reviews/public/${tenantId}?skip=${skip}&limit=${pageSize}&sort_by=${sortBy}&sort_order=${sortOrder}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch reviews');
      }

      const data = await response.json();
      setReviews(data.reviews || []);
      setTotalReviews(data.total || 0);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reviews');
      setReviews([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAggregation = async () => {
    try {
      const response = await fetch(`/api/reviews/public/${tenantId}/aggregation`);

      if (!response.ok) {
        throw new Error('Failed to fetch aggregation');
      }

      const data = await response.json();
      setAggregation(data);
    } catch (err) {
      console.error('Failed to fetch aggregation:', err);
    }
  };

  const ratingDistributionData = aggregation
    ? [
        { rating: '5 Stars', count: aggregation.rating_distribution['5'] || 0 },
        { rating: '4 Stars', count: aggregation.rating_distribution['4'] || 0 },
        { rating: '3 Stars', count: aggregation.rating_distribution['3'] || 0 },
        { rating: '2 Stars', count: aggregation.rating_distribution['2'] || 0 },
        { rating: '1 Star', count: aggregation.rating_distribution['1'] || 0 }
      ]
    : [];

  const totalPages = Math.ceil(totalReviews / pageSize);

  const handlePreviousPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handleSortChange = (newSortBy: 'created_at' | 'rating') => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('desc');
    }
    setCurrentPage(0);
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
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Customer Reviews</h1>
          <p className="text-gray-600">See what our clients say about us</p>
        </div>

        {/* Rating Summary */}
        {aggregation && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Rating Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Average Rating */}
                <div className="flex flex-col items-center justify-center">
                  <div className="text-5xl font-bold text-gray-900 mb-2">
                    {aggregation.average_rating.toFixed(1)}
                  </div>
                  <div className="mb-2">{renderStars(Math.round(aggregation.average_rating))}</div>
                  <p className="text-sm text-gray-600">
                    Based on {aggregation.total_reviews} review{aggregation.total_reviews !== 1 ? 's' : ''}
                  </p>
                </div>

                {/* Rating Distribution Chart */}
                <div className="md:col-span-2">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={ratingDistributionData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="rating" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]}>
                        {ratingDistributionData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={RATING_COLORS[entry.rating.split(' ')[0] as keyof typeof RATING_COLORS]}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Sort Controls */}
        <div className="mb-6 flex gap-2">
          <Button
            variant={sortBy === 'created_at' ? 'default' : 'outline'}
            onClick={() => handleSortChange('created_at')}
            className="text-sm"
          >
            Newest {sortBy === 'created_at' && (sortOrder === 'desc' ? '↓' : '↑')}
          </Button>
          <Button
            variant={sortBy === 'rating' ? 'default' : 'outline'}
            onClick={() => handleSortChange('rating')}
            className="text-sm"
          >
            Highest Rated {sortBy === 'rating' && (sortOrder === 'desc' ? '↓' : '↑')}
          </Button>
        </div>

        {/* Reviews List */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading reviews...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
          </div>
        ) : reviews.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No reviews yet. Be the first to leave a review!</p>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-8">
              {reviews.map((review) => (
                <ReviewCard key={review._id} review={review} showVerifiedBadge={true} />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between">
                <Button
                  variant="outline"
                  onClick={handlePreviousPage}
                  disabled={currentPage === 0}
                  className="flex items-center gap-2"
                >
                  <ChevronLeft size={16} />
                  Previous
                </Button>

                <div className="text-sm text-gray-600">
                  Page {currentPage + 1} of {totalPages}
                </div>

                <Button
                  variant="outline"
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages - 1}
                  className="flex items-center gap-2"
                >
                  Next
                  <ChevronRight size={16} />
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
