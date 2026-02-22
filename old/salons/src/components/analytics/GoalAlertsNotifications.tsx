import React, { useState, useEffect, useMemo } from 'react';
import { AlertCircle, Bell, Lightbulb, TrendingDown, Clock, X, CheckCircle } from 'lucide-react';

interface Alert {
  id: string;
  goalId: string;
  goalName: string;
  type: 'at_risk' | 'missed' | 'off_track' | 'critical';
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  read: boolean;
  actionRequired: boolean;
}

interface Recommendation {
  id: string;
  goalId: string;
  goalName: string;
  title: string;
  description: string;
  action: string;
  impact: 'high' | 'medium' | 'low';
  basedOn: string;
  createdAt: string;
}

interface GoalAlertsNotificationsProps {
  alerts?: Alert[];
  recommendations?: Recommendation[];
  onAlertDismiss?: (alertId: string) => void;
  onAlertRead?: (alertId: string) => void;
  onRecommendationApply?: (recommendationId: string) => void;
  onRecommendationDismiss?: (recommendationId: string) => void;
}

export const GoalAlertsNotifications: React.FC<GoalAlertsNotificationsProps> = ({
  alerts = [],
  recommendations = [],
  onAlertDismiss,
  onAlertRead,
  onRecommendationApply,
  onRecommendationDismiss,
}) => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'recommendations'>('alerts');
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());
  const [dismissedRecommendations, setDismissedRecommendations] = useState<Set<string>>(new Set());

  const visibleAlerts = useMemo(
    () => alerts.filter((alert) => !dismissedAlerts.has(alert.id)),
    [alerts, dismissedAlerts]
  );

  const visibleRecommendations = useMemo(
    () => recommendations.filter((rec) => !dismissedRecommendations.has(rec.id)),
    [recommendations, dismissedRecommendations]
  );

  const unreadAlerts = useMemo(() => visibleAlerts.filter((a) => !a.read).length, [visibleAlerts]);

  const criticalAlerts = useMemo(
    () => visibleAlerts.filter((a) => a.severity === 'critical' || a.type === 'critical'),
    [visibleAlerts]
  );

  const handleDismissAlert = (alertId: string) => {
    setDismissedAlerts((prev) => new Set([...prev, alertId]));
    onAlertDismiss?.(alertId);
  };

  const handleReadAlert = (alertId: string) => {
    onAlertRead?.(alertId);
  };

  const handleDismissRecommendation = (recId: string) => {
    setDismissedRecommendations((prev) => new Set([...prev, recId]));
    onRecommendationDismiss?.(recId);
  };

  const handleApplyRecommendation = (recId: string) => {
    setDismissedRecommendations((prev) => new Set([...prev, recId]));
    onRecommendationApply?.(recId);
  };

  const getSeverityColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-800';
      case 'high':
        return 'bg-orange-100 border-orange-300 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'low':
        return 'bg-blue-100 border-blue-300 text-blue-800';
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const getSeverityIcon = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'high':
        return <AlertCircle className="w-5 h-5 text-orange-600" />;
      case 'medium':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'low':
        return <Bell className="w-5 h-5 text-blue-600" />;
      default:
        return null;
    }
  };

  const getImpactColor = (impact: Recommendation['impact']) => {
    switch (impact) {
      case 'high':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'medium':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const renderAlert = (alert: Alert) => (
    <div
      key={alert.id}
      className={`rounded-lg border-l-4 p-4 mb-3 transition ${getSeverityColor(alert.severity)} ${
        !alert.read ? 'border-l-4 font-medium' : ''
      }`}
    >
      <div className="flex justify-between items-start">
        <div className="flex gap-3 flex-1">
          {getSeverityIcon(alert.severity)}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold">{alert.goalName}</h4>
              {!alert.read && (
                <span className="inline-block w-2 h-2 bg-current rounded-full"></span>
              )}
            </div>
            <p className="text-sm">{alert.message}</p>
            <div className="text-xs opacity-75 mt-1">
              {new Date(alert.createdAt).toLocaleString()}
            </div>
          </div>
        </div>

        <div className="flex gap-2 ml-2">
          {!alert.read && (
            <button
              onClick={() => handleReadAlert(alert.id)}
              className="p-1 hover:bg-white hover:bg-opacity-50 rounded transition"
              title="Mark as read"
            >
              <CheckCircle className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => handleDismissAlert(alert.id)}
            className="p-1 hover:bg-white hover:bg-opacity-50 rounded transition"
            title="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {alert.actionRequired && (
        <div className="mt-3 pt-3 border-t border-current border-opacity-20">
          <button className="text-sm font-medium hover:underline">
            Take Action →
          </button>
        </div>
      )}
    </div>
  );

  const renderRecommendation = (rec: Recommendation) => (
    <div
      key={rec.id}
      className={`rounded-lg border-l-4 p-4 mb-3 transition ${getImpactColor(rec.impact)}`}
    >
      <div className="flex justify-between items-start">
        <div className="flex gap-3 flex-1">
          <Lightbulb className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold mb-1">{rec.title}</h4>
            <p className="text-sm mb-2">{rec.description}</p>
            <div className="text-xs opacity-75 mb-2">
              <span className="inline-block mr-3">Goal: {rec.goalName}</span>
              <span className="inline-block">Based on: {rec.basedOn}</span>
            </div>
            <div className="text-xs opacity-75">
              {new Date(rec.createdAt).toLocaleString()}
            </div>
          </div>
        </div>

        <div className="flex gap-2 ml-2">
          <button
            onClick={() => handleApplyRecommendation(rec.id)}
            className="px-3 py-1 text-sm font-medium bg-white bg-opacity-50 hover:bg-opacity-75 rounded transition"
          >
            Apply
          </button>
          <button
            onClick={() => handleDismissRecommendation(rec.id)}
            className="p-1 hover:bg-white hover:bg-opacity-50 rounded transition"
            title="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-current border-opacity-20">
        <p className="text-sm font-medium">{rec.action}</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Alerts & Recommendations</h2>
        {criticalAlerts.length > 0 && (
          <div className="flex items-center gap-2 bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
            <AlertCircle className="w-4 h-4" />
            {criticalAlerts.length} Critical Alert{criticalAlerts.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('alerts')}
          className={`px-4 py-2 font-medium border-b-2 transition ${
            activeTab === 'alerts'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4" />
            Alerts
            {unreadAlerts > 0 && (
              <span className="ml-1 inline-block w-5 h-5 bg-red-600 text-white text-xs rounded-full flex items-center justify-center">
                {unreadAlerts}
              </span>
            )}
          </div>
        </button>
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`px-4 py-2 font-medium border-b-2 transition ${
            activeTab === 'recommendations'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Recommendations
            {visibleRecommendations.length > 0 && (
              <span className="ml-1 inline-block w-5 h-5 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center">
                {visibleRecommendations.length}
              </span>
            )}
          </div>
        </button>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow p-6">
        {activeTab === 'alerts' ? (
          <div>
            {visibleAlerts.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
                <p className="text-gray-600">All goals are on track! No alerts at this time.</p>
              </div>
            ) : (
              <div>
                {/* Critical Alerts Section */}
                {criticalAlerts.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-red-800 mb-3 uppercase">
                      Critical Alerts ({criticalAlerts.length})
                    </h3>
                    {criticalAlerts.map(renderAlert)}
                  </div>
                )}

                {/* Other Alerts Section */}
                {visibleAlerts.filter((a) => a.severity !== 'critical').length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase">
                      Other Alerts (
                      {visibleAlerts.filter((a) => a.severity !== 'critical').length})
                    </h3>
                    {visibleAlerts
                      .filter((a) => a.severity !== 'critical')
                      .map(renderAlert)}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div>
            {visibleRecommendations.length === 0 ? (
              <div className="text-center py-8">
                <Lightbulb className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No recommendations at this time.</p>
              </div>
            ) : (
              <div>
                {/* High Impact Recommendations */}
                {visibleRecommendations.filter((r) => r.impact === 'high').length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-green-800 mb-3 uppercase">
                      High Impact ({visibleRecommendations.filter((r) => r.impact === 'high').length})
                    </h3>
                    {visibleRecommendations
                      .filter((r) => r.impact === 'high')
                      .map(renderRecommendation)}
                  </div>
                )}

                {/* Medium Impact Recommendations */}
                {visibleRecommendations.filter((r) => r.impact === 'medium').length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold text-blue-800 mb-3 uppercase">
                      Medium Impact ({visibleRecommendations.filter((r) => r.impact === 'medium').length})
                    </h3>
                    {visibleRecommendations
                      .filter((r) => r.impact === 'medium')
                      .map(renderRecommendation)}
                  </div>
                )}

                {/* Low Impact Recommendations */}
                {visibleRecommendations.filter((r) => r.impact === 'low').length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase">
                      Low Impact ({visibleRecommendations.filter((r) => r.impact === 'low').length})
                    </h3>
                    {visibleRecommendations
                      .filter((r) => r.impact === 'low')
                      .map(renderRecommendation)}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {(visibleAlerts.length > 0 || visibleRecommendations.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-red-600">{visibleAlerts.length}</div>
            <div className="text-sm text-gray-600">Active Alerts</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{visibleRecommendations.length}</div>
            <div className="text-sm text-gray-600">Recommendations</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {((visibleAlerts.filter((a) => a.read).length / Math.max(visibleAlerts.length, 1)) * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-600">Alerts Reviewed</div>
          </div>
        </div>
      )}
    </div>
  );
};
