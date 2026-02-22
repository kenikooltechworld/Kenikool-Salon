import React, { useState, useMemo } from 'react';
import { TrendingUp, TrendingDown, Target, AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface KPIMetric {
  id: string;
  name: string;
  currentValue: number;
  targetValue: number;
  unit: string;
  status: 'on_track' | 'at_risk' | 'achieved' | 'missed';
  trend: 'up' | 'down' | 'stable';
  trendPercentage: number;
  lastUpdated: string;
  historicalData?: number[];
  description?: string;
}

interface KPIDashboardProps {
  kpis?: KPIMetric[];
  onKPIClick?: (kpiId: string) => void;
  showTrends?: boolean;
  layout?: 'grid' | 'list';
}

export const KPIDashboard: React.FC<KPIDashboardProps> = ({
  kpis = [],
  onKPIClick,
  showTrends = true,
  layout = 'grid',
}) => {
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'on_track' | 'at_risk' | 'achieved' | 'missed'>('all');

  const filteredKPIs = useMemo(() => {
    if (filterStatus === 'all') return kpis;
    return kpis.filter((kpi) => kpi.status === filterStatus);
  }, [kpis, filterStatus]);

  const stats = useMemo(() => {
    return {
      total: kpis.length,
      onTrack: kpis.filter((k) => k.status === 'on_track').length,
      atRisk: kpis.filter((k) => k.status === 'at_risk').length,
      achieved: kpis.filter((k) => k.status === 'achieved').length,
      missed: kpis.filter((k) => k.status === 'missed').length,
    };
  }, [kpis]);

  const getStatusIcon = (status: KPIMetric['status']) => {
    switch (status) {
      case 'achieved':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'on_track':
        return <Clock className="w-5 h-5 text-blue-600" />;
      case 'at_risk':
        return <AlertCircle className="w-5 h-5 text-orange-600" />;
      case 'missed':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: KPIMetric['status']) => {
    switch (status) {
      case 'achieved':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'on_track':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'at_risk':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'missed':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 80) return 'bg-blue-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getTrendIcon = (trend: KPIMetric['trend']) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-600" />;
      case 'stable':
        return <div className="w-4 h-4 text-gray-600">—</div>;
      default:
        return null;
    }
  };

  const getTrendColor = (trend: KPIMetric['trend']) => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      case 'stable':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  const renderKPICard = (kpi: KPIMetric) => {
    const progressPercentage = (kpi.currentValue / kpi.targetValue) * 100;
    const isSelected = selectedKPI === kpi.id;

    return (
      <div
        key={kpi.id}
        onClick={() => {
          setSelectedKPI(isSelected ? null : kpi.id);
          onKPIClick?.(kpi.id);
        }}
        className={`bg-white rounded-lg shadow-md p-5 cursor-pointer transition-all hover:shadow-lg border-l-4 ${getStatusColor(
          kpi.status
        )} ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900">{kpi.name}</h3>
              {getStatusIcon(kpi.status)}
            </div>
            {kpi.description && (
              <p className="text-xs text-gray-600">{kpi.description}</p>
            )}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">
              {kpi.unit}
              {kpi.currentValue.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">
              of {kpi.unit}
              {kpi.targetValue.toLocaleString()}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span className="font-medium">{Math.min(progressPercentage, 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${getProgressColor(progressPercentage)}`}
              style={{ width: `${Math.min(progressPercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Trend and Status */}
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-1">
            {getTrendIcon(kpi.trend)}
            <span className={`text-xs font-medium ${getTrendColor(kpi.trend)}`}>
              {kpi.trend === 'up' && '+'}
              {kpi.trend === 'down' && '-'}
              {kpi.trendPercentage}%
            </span>
          </div>
          <span className="text-xs text-gray-500">
            {new Date(kpi.lastUpdated).toLocaleDateString()}
          </span>
        </div>

        {/* Status Badge */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <span className={`text-xs font-semibold px-2 py-1 rounded ${getStatusColor(kpi.status)}`}>
            {kpi.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>

        {/* Expanded Details */}
        {isSelected && kpi.historicalData && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-xs font-medium text-gray-700 mb-2">Historical Trend</div>
            <div className="flex items-end gap-1 h-12">
              {kpi.historicalData.map((value, idx) => {
                const maxValue = Math.max(...kpi.historicalData!);
                const height = (value / maxValue) * 100;
                return (
                  <div
                    key={idx}
                    className="flex-1 bg-blue-300 rounded-t opacity-70 hover:opacity-100 transition"
                    style={{ height: `${height}%` }}
                    title={`${value}`}
                  />
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">KPI Dashboard</h2>
        <div className="text-sm text-gray-600">
          {filteredKPIs.length} of {kpis.length} KPIs
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-xs text-gray-600">Total KPIs</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4 text-center border-l-4 border-blue-500">
          <div className="text-2xl font-bold text-blue-600">{stats.onTrack}</div>
          <div className="text-xs text-blue-700">On Track</div>
        </div>
        <div className="bg-orange-50 rounded-lg shadow p-4 text-center border-l-4 border-orange-500">
          <div className="text-2xl font-bold text-orange-600">{stats.atRisk}</div>
          <div className="text-xs text-orange-700">At Risk</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4 text-center border-l-4 border-green-500">
          <div className="text-2xl font-bold text-green-600">{stats.achieved}</div>
          <div className="text-xs text-green-700">Achieved</div>
        </div>
        <div className="bg-red-50 rounded-lg shadow p-4 text-center border-l-4 border-red-500">
          <div className="text-2xl font-bold text-red-600">{stats.missed}</div>
          <div className="text-xs text-red-700">Missed</div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 flex-wrap">
        {(['all', 'on_track', 'at_risk', 'achieved', 'missed'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`px-3 py-1 text-sm rounded-full transition ${
              filterStatus === status
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {status === 'all' ? 'All' : status.replace('_', ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {/* KPI Cards */}
      {filteredKPIs.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">No KPIs found. Create your first KPI to get started!</p>
        </div>
      ) : layout === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredKPIs.map(renderKPICard)}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredKPIs.map(renderKPICard)}
        </div>
      )}

      {/* Achievement Trends Summary */}
      {showTrends && filteredKPIs.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Goal Achievement Trends</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Average Progress */}
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2">Average Progress</div>
              <div className="text-3xl font-bold text-blue-600">
                {(
                  filteredKPIs.reduce((sum, kpi) => sum + (kpi.currentValue / kpi.targetValue) * 100, 0) /
                  filteredKPIs.length
                ).toFixed(0)}
                %
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Across all {filteredKPIs.length} KPI{filteredKPIs.length !== 1 ? 's' : ''}
              </p>
            </div>

            {/* Status Distribution */}
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2">Status Distribution</div>
              <div className="space-y-2">
                {[
                  { status: 'on_track', label: 'On Track', color: 'bg-blue-500', count: stats.onTrack },
                  { status: 'at_risk', label: 'At Risk', color: 'bg-orange-500', count: stats.atRisk },
                  { status: 'achieved', label: 'Achieved', color: 'bg-green-500', count: stats.achieved },
                  { status: 'missed', label: 'Missed', color: 'bg-red-500', count: stats.missed },
                ].map((item) => (
                  <div key={item.status} className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${item.color}`} />
                    <span className="text-sm text-gray-700">{item.label}</span>
                    <span className="text-sm font-medium text-gray-900 ml-auto">
                      {item.count} ({((item.count / stats.total) * 100).toFixed(0)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
