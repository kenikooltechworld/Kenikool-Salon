import React, { useState } from 'react';

interface Goal {
  id: string;
  name: string;
  target: number;
  current: number;
  unit: string;
  status: 'on_track' | 'at_risk' | 'achieved';
  type: 'individual' | 'team';
  owner?: string;
  teamMembers?: string[];
  historicalAchievement?: number;
}

interface GoalTrackerProps {
  goals?: Goal[];
}

export const GoalTracker: React.FC<GoalTrackerProps> = ({
  goals = [
    { id: '1', name: 'Monthly Revenue', target: 50000, current: 42000, unit: '$', status: 'on_track', type: 'team', teamMembers: ['Alice', 'Bob', 'Charlie'], historicalAchievement: 92 },
    { id: '2', name: 'Bookings', target: 500, current: 480, unit: '', status: 'on_track', type: 'team', teamMembers: ['Alice', 'Bob', 'Charlie'], historicalAchievement: 88 },
    { id: '3', name: 'New Clients', target: 100, current: 85, unit: '', status: 'at_risk', type: 'individual', owner: 'Alice', historicalAchievement: 75 },
    { id: '4', name: 'Client Retention', target: 95, current: 92, unit: '%', status: 'on_track', type: 'team', teamMembers: ['Alice', 'Bob', 'Charlie'], historicalAchievement: 90 },
  ],
}) => {
  const [viewMode, setViewMode] = useState<'all' | 'team' | 'individual'>('all');
  const [expandedGoal, setExpandedGoal] = useState<string | null>(null);

  const filteredGoals = goals.filter((goal) => {
    if (viewMode === 'all') return true;
    return goal.type === viewMode;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'achieved':
        return 'bg-green-100 text-green-800';
      case 'on_track':
        return 'bg-blue-100 text-blue-800';
      case 'at_risk':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 80) return 'bg-blue-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setViewMode('all')}
          className={`px-3 py-1 text-sm rounded ${viewMode === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          All Goals
        </button>
        <button
          onClick={() => setViewMode('team')}
          className={`px-3 py-1 text-sm rounded ${viewMode === 'team' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          Team Goals
        </button>
        <button
          onClick={() => setViewMode('individual')}
          className={`px-3 py-1 text-sm rounded ${viewMode === 'individual' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
        >
          Individual Goals
        </button>
      </div>

      {filteredGoals.map((goal) => {
        const percentage = Math.min((goal.current / goal.target) * 100, 100);
        const isExpanded = expandedGoal === goal.id;
        return (
          <div key={goal.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-gray-900">{goal.name}</h3>
                  <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-700">
                    {goal.type === 'team' ? '👥 Team' : '👤 Individual'}
                  </span>
                </div>
                {goal.owner && <p className="text-xs text-gray-500 mt-1">Owner: {goal.owner}</p>}
              </div>
              <span className={`text-xs font-semibold px-2 py-1 rounded ${getStatusColor(goal.status)}`}>
                {goal.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>
                {goal.unit}
                {goal.current.toLocaleString()} / {goal.unit}
                {goal.target.toLocaleString()}
              </span>
              <span>{percentage.toFixed(0)}%</span>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
              <div
                className={`h-2 rounded-full transition-all ${getProgressColor(percentage)}`}
                style={{ width: `${percentage}%` }}
              />
            </div>

            {goal.historicalAchievement && (
              <div className="text-xs text-gray-600 mb-2">
                Historical Achievement Rate: {goal.historicalAchievement}%
              </div>
            )}

            {goal.type === 'team' && goal.teamMembers && (
              <div>
                <button
                  onClick={() => setExpandedGoal(isExpanded ? null : goal.id)}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  {isExpanded ? '▼' : '▶'} Team Members ({goal.teamMembers.length})
                </button>
                {isExpanded && (
                  <div className="mt-2 pl-4 border-l-2 border-gray-200 space-y-1">
                    {goal.teamMembers.map((member) => (
                      <div key={member} className="text-xs text-gray-600">
                        • {member}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
