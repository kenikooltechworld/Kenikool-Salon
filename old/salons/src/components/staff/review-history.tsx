import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp } from "lucide-react";

interface Review {
  _id: string;
  review_date: string;
  ratings: Record<string, number>;
  strengths: string;
  areas_for_improvement: string;
  goals: Array<{ goal: string; target_date: string }>;
  follow_up_date?: string;
}

interface ReviewHistoryProps {
  staffId: string;
  staffName: string;
}

export const ReviewHistory: React.FC<ReviewHistoryProps> = ({
  staffId,
  staffName,
}) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);

  useEffect(() => {
    fetchReviews();
    fetchTrends();
  }, [staffId]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/staff/reviews/${staffId}`);
      const data = await response.json();
      setReviews(data.reviews || []);
      if (data.reviews && data.reviews.length > 0) {
        setSelectedReview(data.reviews[0]);
      }
    } catch (error) {
      console.error("Failed to fetch reviews:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch(`/api/staff/reviews/${staffId}/trends`);
      const data = await response.json();
      setTrends(data);
    } catch (error) {
      console.error("Failed to fetch trends:", error);
    }
  };

  const getAverageRating = (ratings: Record<string, number>) => {
    const values = Object.values(ratings);
    return values.length > 0
      ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
      : "N/A";
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Review History
          </CardTitle>
          <p className="text-sm text-slate-500 mt-1">{staffName}</p>
        </CardHeader>

        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-center text-slate-500 py-8">
              Loading reviews...
            </p>
          ) : reviews.length === 0 ? (
            <p className="text-center text-slate-500 py-8">No reviews yet</p>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-1">
                <h3 className="font-semibold text-sm mb-2">Reviews</h3>
                <ScrollArea className="h-96">
                  <div className="space-y-2 pr-4">
                    {reviews.map((review) => (
                      <button
                        key={review._id}
                        onClick={() => setSelectedReview(review)}
                        className={`w-full text-left p-2 rounded-lg transition ${
                          selectedReview?._id === review._id
                            ? "bg-blue-100 border border-blue-300"
                            : "hover:bg-slate-100 border border-slate-200"
                        }`}
                      >
                        <p className="text-sm font-medium">
                          {new Date(review.review_date).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-slate-600">
                          Avg: {getAverageRating(review.ratings)}
                        </p>
                      </button>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              <div className="lg:col-span-2">
                {selectedReview && (
                  <div className="space-y-4">
                    <div className="bg-slate-50 rounded-lg p-3">
                      <p className="text-sm text-slate-600 mb-2">
                        Review Date:{" "}
                        {new Date(
                          selectedReview.review_date,
                        ).toLocaleDateString()}
                      </p>
                      <div className="grid grid-cols-2 gap-2 mb-3">
                        {Object.entries(selectedReview.ratings).map(
                          ([key, value]) => (
                            <div key={key} className="text-xs">
                              <span className="capitalize text-slate-600">
                                {key}:
                              </span>
                              <span className="font-semibold ml-1">
                                {value}/5
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-sm mb-1">Strengths</h4>
                      <p className="text-sm text-slate-700">
                        {selectedReview.strengths}
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-sm mb-1">
                        Areas for Improvement
                      </h4>
                      <p className="text-sm text-slate-700">
                        {selectedReview.areas_for_improvement}
                      </p>
                    </div>

                    {selectedReview.goals &&
                      selectedReview.goals.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-sm mb-2">Goals</h4>
                          <div className="space-y-1">
                            {selectedReview.goals.map((goal, idx) => (
                              <div key={idx} className="text-sm">
                                <p className="text-slate-700">• {goal.goal}</p>
                                {goal.target_date && (
                                  <p className="text-xs text-slate-500 ml-4">
                                    Target:{" "}
                                    {new Date(
                                      goal.target_date,
                                    ).toLocaleDateString()}
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                    {selectedReview.follow_up_date && (
                      <Badge variant="outline">
                        Follow-up:{" "}
                        {new Date(
                          selectedReview.follow_up_date,
                        ).toLocaleDateString()}
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {trends && trends.trends && trends.trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Rating Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends.trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <YAxis domain={[0, 5]} />
                <Tooltip
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <Legend />
                {Object.keys(trends.average_ratings || {}).map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={`ratings.${key}`}
                    name={key}
                    stroke={`hsl(${Math.random() * 360}, 70%, 50%)`}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
