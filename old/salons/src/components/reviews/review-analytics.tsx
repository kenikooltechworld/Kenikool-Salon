import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, TrendingUp, Users, MessageSquare, Star } from 'lucide-react';
import { format, subDays } from 'date-fns';

interface AnalyticsData {
  period: {
    start_date: string;
    end_date: string;
  };
  overall_metrics: {
    average_rating: number;
    total_reviews: number;
    rating_distribution: Record<string, number>;
    response_rate: number;
    responded_count: number;
  };
  rating_trend: Array<{
    date: string;
    average_rating: number;
    total_reviews: number;
  }>;
  service_ratings: Array<{
    service_id: string;
    service_name: string;
    average_rating: number;
    total_reviews: number;
  }>;
  stylist_ratings: Array<{
    stylist_id: string;
    stylist_name: string;
    average_rating: number;
    total_reviews: number;
  }>;
  response_rate: {
    response_rate: number;
    responded_count: number;
    total_reviews: number;
  };
  review_volume: Array<{
    date: string;
    total_reviews: number;
    approved: number;
    pending: number;
    rejected: number;
  }>;
  monthly_aggregation: Array<{
    month: string;
    average_rating: number;
    total_reviews: number;
    rating_distribution: Record<string, number>;
  }>;
}

interface ReviewAnalyticsProps {
  tenantId: string;
  onDateRangeChange?: (range: { start_date: Date; end_date: Date }) => void;
}

const COLORS = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e'];
const RATING_COLORS = {
  '1': '#ef4444',
  '2': '#f97316',
  '3': '#eab308',
  '4': '#84cc16',
  '5': '#22c55e'
};

export function ReviewAnalytics({ tenantId, onDateRangeChange }: ReviewAnalyticsProps) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    start_date: subDays(new Date(), 30),
    end_date: new Date()
  });

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        start_date: dateRange.start_date.toISOString(),
        end_date: dateRange.end_date.toISOString()
      });

      const response = await fetch(`/api/reviews/analytics?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeChange = (days: number) => {
    const newEndDate = new Date();
    const newStartDate = subDays(newEndDate, days);
    setDateRange({
      start_date: newStartDate,
      end_date: newEndDate
    });
    onDateRangeChange?.({
      start_date: newStartDate,
      end_date: newEndDate
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <Button onClick={fetchAnalytics} className="mt-2">
          Retry
        </Button>
      </div>
    );
  }

  if (!analytics) {
    return <div className="text-center py-8">No analytics data available</div>;
  }

  const ratingDistributionData = Object.entries(analytics.overall_metrics.rating_distribution).map(
    ([rating, count]) => ({
      name: `${rating} Star${parseInt(rating) !== 1 ? 's' : ''}`,
      value: count,
      fill: RATING_COLORS[rating as keyof typeof RATING_COLORS]
    })
  );

  return (
    <div className="space-y-6">
      {/* Date Range Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Date Range
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 flex-wrap">
            <Button
              variant="outline"
              onClick={() => handleDateRangeChange(7)}
              size="sm"
            >
              Last 7 Days
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDateRangeChange(30)}
              size="sm"
            >
              Last 30 Days
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDateRangeChange(90)}
              size="sm"
            >
              Last 90 Days
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDateRangeChange(365)}
              size="sm"
            >
              Last Year
            </Button>
          </div>
          <p className="text-sm text-gray-600 mt-3">
            {format(dateRange.start_date, 'MMM d, yyyy')} - {format(dateRange.end_date, 'MMM d, yyyy')}
          </p>
        </CardContent>
      </Card>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Star className="w-4 h-4" />
              Average Rating
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {analytics.overall_metrics.average_rating.toFixed(2)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              out of 5.0
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Total Reviews
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {analytics.overall_metrics.total_reviews}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              in selected period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Response Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {analytics.response_rate.response_rate.toFixed(1)}%
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {analytics.response_rate.responded_count} of {analytics.response_rate.total_reviews}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Responded
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {analytics.response_rate.responded_count}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              reviews with responses
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Rating Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Rating Trend Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          {analytics.rating_trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.rating_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis domain={[0, 5]} />
                <Tooltip
                  formatter={(value) => value.toFixed(2)}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="average_rating"
                  stroke="#3b82f6"
                  dot={{ fill: '#3b82f6', r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Average Rating"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-gray-500 py-8">No data available</p>
          )}
        </CardContent>
      </Card>

      {/* Service Ratings Chart */}
      {analytics.service_ratings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Service Ratings</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.service_ratings}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="service_name"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis domain={[0, 5]} />
                <Tooltip
                  formatter={(value) => value.toFixed(2)}
                  labelFormatter={(label) => `Service: ${label}`}
                />
                <Legend />
                <Bar
                  dataKey="average_rating"
                  fill="#10b981"
                  name="Average Rating"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Stylist Ratings Chart */}
      {analytics.stylist_ratings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Stylist Ratings</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.stylist_ratings}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="stylist_name"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis domain={[0, 5]} />
                <Tooltip
                  formatter={(value) => value.toFixed(2)}
                  labelFormatter={(label) => `Stylist: ${label}`}
                />
                <Legend />
                <Bar
                  dataKey="average_rating"
                  fill="#f59e0b"
                  name="Average Rating"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Rating Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Rating Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          {ratingDistributionData.some(item => item.value > 0) ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={ratingDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {ratingDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-center text-gray-500 py-8">No rating data available</p>
          )}
        </CardContent>
      </Card>

      {/* Review Volume Chart */}
      {analytics.review_volume.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Review Volume by Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.review_volume}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="approved" fill="#22c55e" name="Approved" />
                <Bar dataKey="pending" fill="#eab308" name="Pending" />
                <Bar dataKey="rejected" fill="#ef4444" name="Rejected" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
