import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface Suggestion {
  id: string;
  recommendation: string;
  impact: 'high' | 'medium' | 'low';
  category: string;
  confidence: number;
}

interface Insight {
  id: string;
  description: string;
  type: 'performance' | 'opportunity' | 'risk';
  value?: number;
}

interface Alert {
  id: string;
  message: string;
  severity: 'critical' | 'warning' | 'info';
  timestamp: string;
}

export const AISuggestionsComponent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'suggestions' | 'insights' | 'alerts'>('suggestions');
  const [userId] = useState(localStorage.getItem('user_id') || '');

  // Fetch suggestions
  const { data: suggestionsData, isLoading: suggestionsLoading } = useQuery({
    queryKey: ['ai-suggestions', userId],
    queryFn: async () => {
      const response = await fetch(`/api/voice/ai/suggestions?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch suggestions');
      return response.json();
    },
    refetchInterval: 60000, // Refetch every minute
  });

  // Fetch insights
  const { data: insightsData, isLoading: insightsLoading } = useQuery({
    queryKey: ['ai-insights', userId],
    queryFn: async () => {
      const response = await fetch(`/api/voice/ai/insights?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch insights');
      return response.json();
    },
    refetchInterval: 60000,
  });

  // Fetch alerts
  const { data: alertsData, isLoading: alertsLoading } = useQuery({
    queryKey: ['ai-alerts', userId],
    queryFn: async () => {
      const response = await fetch(`/api/voice/ai/alerts?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch alerts');
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Submit feedback mutation
  const feedbackMutation = useMutation({
    mutationFn: async ({ suggestionId, accepted }: { suggestionId: string; accepted: boolean }) => {
      const response = await fetch(`/api/voice/ai/suggestions/${suggestionId}/feedback?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accepted }),
      });
      if (!response.ok) throw new Error('Failed to submit feedback');
      return response.json();
    },
  });

  // Acknowledge alert mutation
  const acknowledgeMutation = useMutation({
    mutationFn: async (alertId: string) => {
      const response = await fetch(`/api/voice/ai/alerts/${alertId}/acknowledge?user_id=${userId}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to acknowledge alert');
      return response.json();
    },
  });

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'info':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Tab Navigation */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('suggestions')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'suggestions'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          💡 Suggestions
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'insights'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          📈 Insights
        </button>
        <button
          onClick={() => setActiveTab('alerts')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'alerts'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          ⚠️ Alerts
        </button>
      </div>

      {/* Suggestions Tab */}
      {activeTab === 'suggestions' && (
        <div className="space-y-3">
          {suggestionsLoading ? (
            <div className="text-center py-8 text-gray-500">Loading suggestions...</div>
          ) : suggestionsData?.suggestions?.length > 0 ? (
            suggestionsData.suggestions.map((suggestion: Suggestion) => (
              <Card key={suggestion.id}>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{suggestion.recommendation}</p>
                      <div className="flex gap-2 mt-2">
                        <Badge className={getImpactColor(suggestion.impact)}>
                          {suggestion.impact} impact
                        </Badge>
                        <Badge variant="outline">{suggestion.category}</Badge>
                        <span className="text-sm text-gray-600">
                          {Math.round(suggestion.confidence * 100)}% confidence
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          feedbackMutation.mutate({
                            suggestionId: suggestion.id,
                            accepted: true,
                          })
                        }
                      >
                        ✓ Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          feedbackMutation.mutate({
                            suggestionId: suggestion.id,
                            accepted: false,
                          })
                        }
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">No suggestions available</div>
          )}
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-3">
          {insightsLoading ? (
            <div className="text-center py-8 text-gray-500">Loading insights...</div>
          ) : insightsData?.insights?.length > 0 ? (
            insightsData.insights.map((insight: Insight) => (
              <Card key={insight.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <span className="text-xl mt-1 flex-shrink-0">📈</span>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{insight.description}</p>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="outline">{insight.type}</Badge>
                        {insight.value !== undefined && (
                          <span className="text-sm text-gray-600">Value: {insight.value}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">No insights available</div>
          )}
        </div>
      )}

      {/* Alerts Tab */}
      {activeTab === 'alerts' && (
        <div className="space-y-3">
          {alertsLoading ? (
            <div className="text-center py-8 text-gray-500">Loading alerts...</div>
          ) : alertsData?.alerts?.length > 0 ? (
            alertsData.alerts.map((alert: Alert) => (
              <Card key={alert.id} className={getSeverityColor(alert.severity)}>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <p className="font-medium">{alert.message}</p>
                      <p className="text-sm opacity-75 mt-1">
                        {new Date(alert.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => acknowledgeMutation.mutate(alert.id)}
                    >
                      Acknowledge
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">No alerts</div>
          )}
        </div>
      )}
    </div>
  );
};

export default AISuggestionsComponent;
