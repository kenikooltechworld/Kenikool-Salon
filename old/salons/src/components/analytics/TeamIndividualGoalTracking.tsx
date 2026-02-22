import React, { useState, useMemo } from 'react';
import { Users, User, TrendingUp, Award, BarChart3, Calendar } from 'lucide-react';

interface TeamMemberPerformance {
  memberId: string;
  memberName: string;
  currentValue: number;
  targetValue: number;
  achievementRate: number;
  historicalAchievementRates: number[];
  trend: 'up' | 'down' | 'stable';
  lastUpdated: string;
}

interface GoalComparison {
  goalId: string;
  goalName: string;
  goalType: string;
  teamTarget: number;
  teamCurrent: number;
  teamProgress: number;
  teamMembers: TeamMemberPerformance[];
  historicalTeamAchievement: number[];
  historicalIndividualAchievements: Record<string, number[]>;
}

interface TeamIndividualGoalTrackingProps {
  goals?: GoalComparison[];
  onMemberClick?: (memberId: string) => void;
  onGoalClick?: (goalId: string) => void;
}

export const TeamIndividualGoalTracking: React.FC<TeamIndividualGoalTrackingProps> = ({
  goals = [],
  onMemberClick,
  onGoalClick,
}) => {
  const [selectedGoalId, setSelectedGoalId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'comparison' | 'history'>('comparison');
  const [selectedMemberId, setSelectedMemberId] = useState<string | null>(null);

  const selectedGoal = useMemo(
    () => goals.find((g) => g.goalId === selectedGoalId) || goals[0],
    [goals, selectedGoalId]
  );

  const teamStats = useMemo(() => {
    if (!selectedGoal) return null;

    const avgAchievement =
      selectedGoal.teamMembers.reduce((sum, m) => sum + m.achievementRate, 0) /
      selectedGoal.teamMembers.length;

    const topPerformer = [...selectedGoal.teamMembers].sort(
      (a, b) => b.achievementRate - a.achievementRate
    )[0];

    const bottomPerformer = [...selectedGoal.teamMembers].sort(
      (a, b) => a.achievementRate - b.achievementRate
    )[0];

    return {
      avgAchievement,
      topPerformer,
      bottomPerformer,
      totalMembers: selectedGoal.teamMembers.length,
    };
  }, [selectedGoal]);

  const getPerformanceColor = (achievement: number) => {
    if (achievement >= 100) return 'text-green-600 bg-green-50';
    if (achievement >= 80) return 'text-blue-600 bg-blue-50';
    if (achievement >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 80) return 'bg-blue-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return '📈';
      case 'down':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '';
    }
  };

  if (!selectedGoal) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <p className="text-gray-600">No goals available for comparison.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Team vs Individual Goal Tracking</h2>
      </div>

      {/* Goal Selection */}
      {goals.length > 1 && (
        <div className="bg-white rounded-lg shadow p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Goal</label>
          <select
            value={selectedGoalId || goals[0].goalId}
            onChange={(e) => setSelectedGoalId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {goals.map((goal) => (
              <option key={goal.goalId} value={goal.goalId}>
                {goal.goalName} ({goal.goalType})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* View Mode Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setViewMode('comparison')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            viewMode === 'comparison'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Comparison View
          </div>
        </button>
        <button
          onClick={() => setViewMode('history')}
          className={`px-4 py-2 rounded-lg font-medium transition ${
            viewMode === 'history'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Historical Trends
          </div>
        </button>
      </div>

      {viewMode === 'comparison' ? (
        <>
          {/* Team Overview */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <Users className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Team Performance</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Team Progress */}
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">Team Progress</div>
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {selectedGoal.teamProgress.toFixed(0)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                  <div
                    className={`h-3 rounded-full transition-all ${getProgressColor(
                      selectedGoal.teamProgress
                    )}`}
                    style={{ width: `${Math.min(selectedGoal.teamProgress, 100)}%` }}
                  />
                </div>
                <div className="text-sm text-gray-600">
                  {selectedGoal.teamCurrent.toLocaleString()} / {selectedGoal.teamTarget.toLocaleString()}
                </div>
              </div>

              {/* Team Stats */}
              <div className="space-y-3">
                {teamStats && (
                  <>
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium text-gray-700">Average Achievement</span>
                      <span className="text-lg font-bold text-gray-900">
                        {teamStats.avgAchievement.toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                      <span className="text-sm font-medium text-gray-700">Top Performer</span>
                      <span className="text-lg font-bold text-green-600">
                        {teamStats.topPerformer?.memberName}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-orange-50 rounded">
                      <span className="text-sm font-medium text-gray-700">Needs Support</span>
                      <span className="text-lg font-bold text-orange-600">
                        {teamStats.bottomPerformer?.memberName}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Individual Member Comparison */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <User className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">Individual Performance</h3>
            </div>

            <div className="space-y-3">
              {selectedGoal.teamMembers.map((member) => {
                const isSelected = selectedMemberId === member.memberId;
                const progressPercentage = (member.currentValue / member.targetValue) * 100;

                return (
                  <div
                    key={member.memberId}
                    onClick={() => {
                      setSelectedMemberId(isSelected ? null : member.memberId);
                      onMemberClick?.(member.memberId);
                    }}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">{member.memberName}</h4>
                        <div className="text-xs text-gray-500 mt-1">
                          Updated: {new Date(member.lastUpdated).toLocaleDateString()}
                        </div>
                      </div>
                      <div className={`text-right px-3 py-1 rounded font-bold ${getPerformanceColor(member.achievementRate)}`}>
                        {member.achievementRate.toFixed(0)}%
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mb-2">
                      <div className="flex justify-between text-xs text-gray-600 mb-1">
                        <span>
                          {member.currentValue.toLocaleString()} / {member.targetValue.toLocaleString()}
                        </span>
                        <span>{progressPercentage.toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${getProgressColor(progressPercentage)}`}
                          style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                        />
                      </div>
                    </div>

                    {/* Trend */}
                    <div className="flex items-center gap-1 text-sm">
                      <span>{getTrendIcon(member.trend)}</span>
                      <span className="text-gray-600">
                        {member.trend === 'up' && 'Improving'}
                        {member.trend === 'down' && 'Declining'}
                        {member.trend === 'stable' && 'Stable'}
                      </span>
                    </div>

                    {/* Expanded Details */}
                    {isSelected && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="text-xs font-medium text-gray-700 mb-2">Achievement History</div>
                        <div className="flex items-end gap-1 h-12">
                          {member.historicalAchievementRates.map((rate, idx) => {
                            const maxRate = Math.max(...member.historicalAchievementRates);
                            const height = (rate / maxRate) * 100;
                            return (
                              <div
                                key={idx}
                                className="flex-1 bg-purple-300 rounded-t opacity-70 hover:opacity-100 transition"
                                style={{ height: `${height}%` }}
                                title={`${rate.toFixed(0)}%`}
                              />
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Leaderboard */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-2 mb-4">
              <Award className="w-5 h-5 text-yellow-600" />
              <h3 className="text-lg font-semibold text-gray-900">Leaderboard</h3>
            </div>

            <div className="space-y-2">
              {[...selectedGoal.teamMembers]
                .sort((a, b) => b.achievementRate - a.achievementRate)
                .map((member, idx) => (
                  <div key={member.memberId} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                    <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{member.memberName}</div>
                      <div className="text-xs text-gray-600">
                        {member.currentValue.toLocaleString()} / {member.targetValue.toLocaleString()}
                      </div>
                    </div>
                    <div className={`text-lg font-bold ${getPerformanceColor(member.achievementRate)}`}>
                      {member.achievementRate.toFixed(0)}%
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Historical Achievement Rates */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Historical Achievement Rates</h3>

            <div className="space-y-6">
              {/* Team Historical Trend */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Team Average</h4>
                <div className="flex items-end gap-1 h-32">
                  {selectedGoal.historicalTeamAchievement.map((rate, idx) => {
                    const maxRate = Math.max(...selectedGoal.historicalTeamAchievement);
                    const height = (rate / maxRate) * 100;
                    return (
                      <div
                        key={idx}
                        className="flex-1 bg-blue-400 rounded-t opacity-70 hover:opacity-100 transition group relative"
                        style={{ height: `${height}%` }}
                      >
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                          {rate.toFixed(0)}%
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Individual Member Trends */}
              <div className="space-y-4">
                {selectedGoal.teamMembers.map((member) => (
                  <div key={member.memberId}>
                    <h4 className="font-medium text-gray-900 mb-2">{member.memberName}</h4>
                    <div className="flex items-end gap-1 h-20">
                      {(selectedGoal.historicalIndividualAchievements[member.memberId] || []).map(
                        (rate, idx) => {
                          const maxRate = Math.max(
                            ...(selectedGoal.historicalIndividualAchievements[member.memberId] || [])
                          );
                          const height = (rate / maxRate) * 100;
                          return (
                            <div
                              key={idx}
                              className="flex-1 bg-purple-400 rounded-t opacity-70 hover:opacity-100 transition group relative"
                              style={{ height: `${height}%` }}
                            >
                              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                                {rate.toFixed(0)}%
                              </div>
                            </div>
                          );
                        }
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Trend Analysis */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Trend Analysis</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {selectedGoal.teamMembers.map((member) => {
                const rates = selectedGoal.historicalIndividualAchievements[member.memberId] || [];
                const trend =
                  rates.length >= 2
                    ? rates[rates.length - 1] > rates[rates.length - 2]
                      ? 'improving'
                      : 'declining'
                    : 'stable';

                return (
                  <div key={member.memberId} className="p-4 bg-gray-50 rounded-lg">
                    <div className="font-medium text-gray-900 mb-2">{member.memberName}</div>
                    <div className="text-sm text-gray-600 mb-2">
                      {trend === 'improving' && '📈 Improving trend'}
                      {trend === 'declining' && '📉 Declining trend'}
                      {trend === 'stable' && '➡️ Stable performance'}
                    </div>
                    {rates.length >= 2 && (
                      <div className="text-xs text-gray-600">
                        {Math.abs(rates[rates.length - 1] - rates[rates.length - 2]).toFixed(1)}% change
                        from last period
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
