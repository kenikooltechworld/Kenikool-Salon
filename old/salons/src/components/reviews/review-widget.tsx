"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Star, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Review {
  _id: string;
  client_name: string;
  rating: number;
  comment?: string;
  created_at: string;
  service_name?: string;
}

interface WidgetConfig {
  colors?: {
    primary?: string;
    background?: string;
    text?: string;
  };
  layout?: "grid" | "list";
  maxReviews?: number;
}

interface ReviewWidgetProps {
  tenantId: string;
  config?: WidgetConfig;
  apiBaseUrl?: string;
}

export function ReviewWidget({
  tenantId,
  config = {},
  apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000",
}: ReviewWidgetProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [stats, setStats] = useState({ average_rating: 0, total_reviews: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    colors = {
      primary: "#3b82f6",
      background: "#ffffff",
      text: "#1f2937",
    },
    layout = "grid",
    maxReviews = 5,
  } = config;

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `${apiBaseUrl}/api/reviews/widget/${tenantId}?limit=${maxReviews}`,
        );

        if (!response.ok) {
          throw new Error("Failed to fetch reviews");
        }

        const data = await response.json();
        setReviews(data.reviews || []);
        setStats(data.stats || { average_rating: 0, total_reviews: 0 });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load reviews");
        console.error("Error fetching widget reviews:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, [tenantId, maxReviews, apiBaseUrl]);

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            size={14}
            className={
              i < rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
            }
          />
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div
        className="p-4 rounded-lg"
        style={{ backgroundColor: colors.background }}
      >
        <div className="text-center text-sm" style={{ color: colors.text }}>
          Loading reviews...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="p-4 rounded-lg border border-red-200"
        style={{ backgroundColor: colors.background }}
      >
        <div className="text-sm text-red-600">Error: {error}</div>
      </div>
    );
  }

  return (
    <div
      className="w-full rounded-lg overflow-hidden"
      style={{ backgroundColor: colors.background }}
    >
      {/* Header with stats */}
      <div
        className="p-4 border-b"
        style={{
          borderColor: colors.primary,
          backgroundColor: `${colors.primary}10`,
        }}
      >
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-sm" style={{ color: colors.text }}>
            Customer Reviews
          </h3>
          <div className="flex items-center gap-2">
            {renderStars(Math.round(stats.average_rating))}
            <span
              className="text-sm font-medium"
              style={{ color: colors.text }}
            >
              {stats.average_rating.toFixed(1)}
            </span>
          </div>
        </div>
        <p className="text-xs" style={{ color: colors.text, opacity: 0.7 }}>
          Based on {stats.total_reviews} review
          {stats.total_reviews !== 1 ? "s" : ""}
        </p>
      </div>

      {/* Reviews list */}
      <div
        className={`p-4 ${
          layout === "grid" ? "grid grid-cols-1 gap-3" : "space-y-3"
        }`}
      >
        {reviews.length > 0 ? (
          reviews.map((review) => (
            <div
              key={review._id}
              className="p-3 rounded border"
              style={{
                borderColor: `${colors.primary}30`,
                backgroundColor: `${colors.primary}05`,
              }}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {renderStars(review.rating)}
                  </div>
                  <p
                    className="font-medium text-sm"
                    style={{ color: colors.text }}
                  >
                    {review.client_name}
                  </p>
                </div>
              </div>
              {review.comment && (
                <p
                  className="text-xs leading-relaxed mb-2"
                  style={{ color: colors.text, opacity: 0.8 }}
                >
                  {review.comment.length > 100
                    ? `${review.comment.substring(0, 100)}...`
                    : review.comment}
                </p>
              )}
              {review.service_name && (
                <p
                  className="text-xs"
                  style={{ color: colors.text, opacity: 0.6 }}
                >
                  {review.service_name}
                </p>
              )}
            </div>
          ))
        ) : (
          <p
            className="text-sm text-center py-4"
            style={{ color: colors.text, opacity: 0.6 }}
          >
            No reviews yet
          </p>
        )}
      </div>

      {/* Footer with link */}
      <div
        className="p-3 border-t text-center"
        style={{ borderColor: colors.primary }}
      >
        <a
          href={`/salons/${tenantId}/reviews`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs font-medium hover:opacity-80 transition-opacity"
          style={{ color: colors.primary }}
        >
          View all reviews
          <ExternalLink size={12} />
        </a>
      </div>
    </div>
  );
}
