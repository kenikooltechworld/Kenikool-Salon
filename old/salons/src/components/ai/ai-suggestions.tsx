import React, { useState, useEffect } from "react";
import { Card } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Spinner } from "../ui/spinner";
import {
  LightbulbIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  ThumbsUpIcon,
  ThumbsDownIcon,
  ClockIcon,
  UsersIcon,
  PackageIcon,
  DollarSignIcon,
  CalendarIcon,
} from "../icons";

// Types matching backend models
export enum SuggestionType {
  BOOKING_TIME = "booking_time",
  STYLIST_ASSIGNMENT = "stylist_assignment",
  INVENTORY_REORDER = "inventory_reorder",
  CLIENT_RETENTION = "client_retention",
  UPSELL_SERVICE = "upsell_service",
  STAFFING_OPTIMIZATION = "staffing_optimization",
  PRICING_ADJUSTMENT = "pricing_adjustment",
}

export enum InsightType {
  PERFORMANCE = "performance",
  OPPORTUNITY = "opportunity",
  RISK = "risk",
  TREND = "trend",
}

export enum AlertType {
  INVENTORY_SHORTAGE = "inventory_shortage",
  CLIENT_CHURN_RISK = "client_churn_risk",
  UNDERUTILIZED_SLOTS = "underutilized_slots",
  PERFORMANCE_DECLINE = "performance_decline",
  OPPORTUNITY_DETECTED = "opportunity_detected",
}

export interface Suggestion {
  id: string;
  type: SuggestionType;
  title: string;
  description: string;
  confidence: number;
  reasoning: string;
  action_data: Record<string, any>;
  created_at: string;
  expires_at?: string;
  was_accepted?: boolean;
  user_feedback?: string;
}

export interface Insight {
  id: string;
  type: InsightType;
  title: string;
  description: string;
  impact_level: "high" | "medium" | "low";
  data_points: Record<string, any>;
  recommendations: string[];
  created_at: string;
}

export interface Alert {
  id: string;
  type: AlertType;
  severity: "high" | "medium" | "low";
  title: string;
  message: string;
  action_required: boolean;
  suggested_actions: string[];
  data: Record<string, unknown>;
  created_at: string;
  acknowledged: boolean;
}

interface AISuggestionsProps {
  salonId: string;
  onAcceptSuggestion?: (suggestionId: string) => void;
  onRejectSuggestion?: (suggestionId: string, feedback?: string) => void;
  onAcknowledgeAlert?: (alertId: string) => void;
}

export function AISuggestionsComponent({
  salonId,
  onAcceptSuggestion,
  onRejectSuggestion,
  onAcknowledgeAlert,
}: AISuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<
    "suggestions" | "insights" | "alerts"
  >("suggestions");
  const [feedbackText, setFeedbackText] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchAIData();
    // Poll for updates every 5 minutes
    const interval = setInterval(fetchAIData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [salonId]);

  const fetchAIData = async () => {
    try {
      setLoading(true);
      const [suggestionsRes, insightsRes, alertsRes] = await Promise.all([
        fetch(`/api/ai/suggestions?salon_id=${salonId}`),
        fetch(`/api/ai/insights?salon_id=${salonId}`),
        fetch(`/api/ai/alerts?salon_id=${salonId}`),
      ]);

      if (suggestionsRes.ok) {
        const data = await suggestionsRes.json();
        setSuggestions(data.suggestions || []);
      }

      if (insightsRes.ok) {
        const data = await insightsRes.json();
        setInsights(data.insights || []);
      }

      if (alertsRes.ok) {
        const data = await alertsRes.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error("Failed to fetch AI data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptSuggestion = async (suggestionId: string) => {
    try {
      const response = await fetch(
        `/api/ai/suggestions/${suggestionId}/feedback`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ accepted: true }),
        }
      );

      if (response.ok) {
        setSuggestions((prev) =>
          prev.map((s) =>
            s.id === suggestionId ? { ...s, was_accepted: true } : s
          )
        );
        onAcceptSuggestion?.(suggestionId);
      }
    } catch (error) {
      console.error("Failed to accept suggestion:", error);
    }
  };

  const handleRejectSuggestion = async (suggestionId: string) => {
    try {
      const feedback = feedbackText[suggestionId] || "";
      const response = await fetch(
        `/api/ai/suggestions/${suggestionId}/feedback`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ accepted: false, feedback }),
        }
      );

      if (response.ok) {
        setSuggestions((prev) =>
          prev.map((s) =>
            s.id === suggestionId
              ? { ...s, was_accepted: false, user_feedback: feedback }
              : s
          )
        );
        onRejectSuggestion?.(suggestionId, feedback);
        setFeedbackText((prev) => {
          const newState = { ...prev };
          delete newState[suggestionId];
          return newState;
        });
      }
    } catch (error) {
      console.error("Failed to reject suggestion:", error);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/ai/alerts/${alertId}/acknowledge`, {
        method: "POST",
      });

      if (response.ok) {
        setAlerts((prev) =>
          prev.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a))
        );
        onAcknowledgeAlert?.(alertId);
      }
    } catch (error) {
      console.error("Failed to acknowledge alert:", error);
    }
  };

  const getSuggestionIcon = (type: SuggestionType) => {
    switch (type) {
      case SuggestionType.BOOKING_TIME:
        return <CalendarIcon className="h-5 w-5" />;
      case SuggestionType.STYLIST_ASSIGNMENT:
        return <UsersIcon className="h-5 w-5" />;
      case SuggestionType.INVENTORY_REORDER:
        return <PackageIcon className="h-5 w-5" />;
      case SuggestionType.CLIENT_RETENTION:
        return <UsersIcon className="h-5 w-5" />;
      case SuggestionType.UPSELL_SERVICE:
        return <DollarSignIcon className="h-5 w-5" />;
      case SuggestionType.STAFFING_OPTIMIZATION:
        return <UsersIcon className="h-5 w-5" />;
      case SuggestionType.PRICING_ADJUSTMENT:
        return <DollarSignIcon className="h-5 w-5" />;
      default:
        return <LightbulbIcon className="h-5 w-5" />;
    }
  };

  const getInsightIcon = (type: InsightType) => {
    switch (type) {
      case InsightType.PERFORMANCE:
        return <TrendingUpIcon className="h-5 w-5 text-blue-500" />;
      case InsightType.OPPORTUNITY:
        return <LightbulbIcon className="h-5 w-5 text-green-500" />;
      case InsightType.RISK:
        return <AlertTriangleIcon className="h-5 w-5 text-red-500" />;
      case InsightType.TREND:
        return <TrendingUpIcon className="h-5 w-5 text-purple-500" />;
      default:
        return <LightbulbIcon className="h-5 w-5" />;
    }
  };

  const getAlertIcon = (type: AlertType) => {
    switch (type) {
      case AlertType.INVENTORY_SHORTAGE:
        return <PackageIcon className="h-5 w-5 text-orange-500" />;
      case AlertType.CLIENT_CHURN_RISK:
        return <UsersIcon className="h-5 w-5 text-red-500" />;
      case AlertType.UNDERUTILIZED_SLOTS:
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case AlertType.PERFORMANCE_DECLINE:
        return <TrendingUpIcon className="h-5 w-5 text-red-500" />;
      case AlertType.OPPORTUNITY_DETECTED:
        return <LightbulbIcon className="h-5 w-5 text-green-500" />;
      default:
        return <AlertTriangleIcon className="h-5 w-5" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">AI Suggestions & Insights</h2>
          <p className="text-gray-600">
            Intelligent recommendations powered by your salon data
          </p>
        </div>
        <Button onClick={fetchAIData} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b">
        <button
          onClick={() => setActiveTab("suggestions")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "suggestions"
              ? "border-b-2 border-blue-500 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Suggestions (
          {suggestions.filter((s) => s.was_accepted === undefined).length})
        </button>
        <button
          onClick={() => setActiveTab("insights")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "insights"
              ? "border-b-2 border-blue-500 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Insights ({insights.length})
        </button>
        <button
          onClick={() => setActiveTab("alerts")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "alerts"
              ? "border-b-2 border-blue-500 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Alerts ({alerts.filter((a) => !a.acknowledged).length})
        </button>
      </div>

      {/* Content */}
      <div className="space-y-4">
        {activeTab === "suggestions" && (
          <>
            {suggestions.filter((s) => s.was_accepted === undefined).length ===
            0 ? (
              <Card className="p-8 text-center">
                <LightbulbIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">
                  No active suggestions at the moment
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  The AI will analyze your salon data and provide suggestions
                  soon
                </p>
              </Card>
            ) : (
              suggestions
                .filter((s) => s.was_accepted === undefined)
                .map((suggestion) => (
                  <Card key={suggestion.id} className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="p-3 bg-blue-50 rounded-lg">
                          {getSuggestionIcon(suggestion.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-lg font-semibold">
                              {suggestion.title}
                            </h3>
                            <Badge
                              variant="outline"
                              className={getConfidenceColor(
                                suggestion.confidence
                              )}
                            >
                              {Math.round(suggestion.confidence * 100)}%
                              confidence
                            </Badge>
                          </div>
                          <p className="text-gray-700 mb-3">
                            {suggestion.description}
                          </p>
                          <details className="text-sm text-gray-600">
                            <summary className="cursor-pointer hover:text-gray-900">
                              Why this suggestion?
                            </summary>
                            <p className="mt-2 pl-4 border-l-2 border-gray-200">
                              {suggestion.reasoning}
                            </p>
                          </details>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center space-x-3">
                      <Button
                        onClick={() => handleAcceptSuggestion(suggestion.id)}
                        size="sm"
                        className="flex items-center space-x-2"
                      >
                        <ThumbsUpIcon className="h-4 w-4" />
                        <span>Accept</span>
                      </Button>
                      <Button
                        onClick={() => handleRejectSuggestion(suggestion.id)}
                        variant="outline"
                        size="sm"
                        className="flex items-center space-x-2"
                      >
                        <ThumbsDownIcon className="h-4 w-4" />
                        <span>Reject</span>
                      </Button>
                      <input
                        type="text"
                        placeholder="Optional feedback..."
                        value={feedbackText[suggestion.id] || ""}
                        onChange={(e) =>
                          setFeedbackText((prev) => ({
                            ...prev,
                            [suggestion.id]: e.target.value,
                          }))
                        }
                        className="flex-1 px-3 py-1 text-sm border rounded-md"
                      />
                    </div>
                  </Card>
                ))
            )}
          </>
        )}

        {activeTab === "insights" && (
          <>
            {insights.length === 0 ? (
              <Card className="p-8 text-center">
                <TrendingUpIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">No insights available yet</p>
                <p className="text-sm text-gray-500 mt-2">
                  The AI needs more data to generate meaningful insights
                </p>
              </Card>
            ) : (
              insights.map((insight) => (
                <Card key={insight.id} className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      {getInsightIcon(insight.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold">
                          {insight.title}
                        </h3>
                        <Badge
                          className={getSeverityColor(insight.impact_level)}
                        >
                          {insight.impact_level} impact
                        </Badge>
                      </div>
                      <p className="text-gray-700 mb-4">
                        {insight.description}
                      </p>

                      {insight.recommendations.length > 0 && (
                        <div className="bg-blue-50 rounded-lg p-4">
                          <h4 className="font-medium text-sm mb-2">
                            Recommendations:
                          </h4>
                          <ul className="space-y-1">
                            {insight.recommendations.map((rec, idx) => (
                              <li
                                key={idx}
                                className="text-sm text-gray-700 flex items-start"
                              >
                                <span className="mr-2">•</span>
                                <span>{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              ))
            )}
          </>
        )}

        {activeTab === "alerts" && (
          <>
            {alerts.filter((a) => !a.acknowledged).length === 0 ? (
              <Card className="p-8 text-center">
                <CheckCircleIcon className="h-12 w-12 mx-auto mb-4 text-green-500" />
                <p className="text-gray-600">No active alerts</p>
                <p className="text-sm text-gray-500 mt-2">
                  Everything looks good!
                </p>
              </Card>
            ) : (
              alerts
                .filter((a) => !a.acknowledged)
                .map((alert) => (
                  <Card
                    key={alert.id}
                    className={`p-6 border-l-4 ${getSeverityColor(
                      alert.severity
                    )}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="p-3 bg-white rounded-lg">
                          {getAlertIcon(alert.type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-lg font-semibold">
                              {alert.title}
                            </h3>
                            <Badge className={getSeverityColor(alert.severity)}>
                              {alert.severity}
                            </Badge>
                            {alert.action_required && (
                              <Badge
                                variant="outline"
                                className="bg-red-50 text-red-700 border-red-200"
                              >
                                Action Required
                              </Badge>
                            )}
                          </div>
                          <p className="text-gray-700 mb-4">{alert.message}</p>

                          {alert.suggested_actions.length > 0 && (
                            <div className="bg-yellow-50 rounded-lg p-4">
                              <h4 className="font-medium text-sm mb-2">
                                Suggested Actions:
                              </h4>
                              <ul className="space-y-1">
                                {alert.suggested_actions.map((action, idx) => (
                                  <li
                                    key={idx}
                                    className="text-sm text-gray-700 flex items-start"
                                  >
                                    <span className="mr-2">•</span>
                                    <span>{action}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="mt-4">
                      <Button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        size="sm"
                        variant="outline"
                        className="flex items-center space-x-2"
                      >
                        <CheckCircleIcon className="h-4 w-4" />
                        <span>Acknowledge</span>
                      </Button>
                    </div>
                  </Card>
                ))
            )}
          </>
        )}
      </div>
    </div>
  );
}
