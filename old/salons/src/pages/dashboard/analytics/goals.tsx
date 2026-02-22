import React, { useState } from 'react';
import { GoalManagement } from '@/components/analytics/GoalManagement';
import { KPIDashboard } from '@/components/analytics/KPIDashboard';
import { GoalAlertsNotifications } from '@/components/analytics/GoalAlertsNotifications';
import { TeamIndividualGoalTracking } from '@/components/analytics/TeamIndividualGoalTracking';

interface Goal {
  id: string;
  name: string;
  goalType: 'revenue' | 'bookings' | 'clients' | 'custom';
  targetValue: number;
  currentValue: number;
  unit: string;
  status: 'on_track' | 'at_risk' | 'achieved' | 'missed';
  progressPercentage: number;
  description: string;
  assignedTo: string[];
  startDate: string;
  endDate: string;
  createdAt: string;
  updatedAt: string;
}

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

export default function GoalsPage() {
  const [activeTab, setActiveTab] = useState<'goals' | 'kpis' | 'alerts' | 'team'>('goals');
  const [goals, setGoals] = useState<Goal[]>([
    {
      id: '1',
      name: 'Monthly Revenue',
      goalType: 'revenue',
      targetValue: 50000,
      currentValue: 42000,
      unit: '$',
      status: 'on_track',
      progressPercentage: 84,
      description: 'Q1 revenue target',
      assignedTo: ['Alice', 'Bob', 'Charlie'],
      startDate: '2024-01-01',
      endDate: '2024-03-31',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-15T00:00:00Z',
    },
    {
      id: '2',
      name: 'Bookings Target',
      goalType: 'bookings',
      targetValue: 500,
      currentValue: 480,
      unit: 'bookings',
      status: 'on_track',
      progressPercentage: 96,
      description: 'Monthly booking target',
      assignedTo: ['Alice', 'Bob', 'Charlie'],
      startDate: '2024-01-01',
      endDate: '2024-01-31',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-15T00:00:00Z',
    },
    {
      id: '3',
      name: 'New Clients',
      goalType: 'clients',
      targetValue: 100,
      currentValue: 85,
      unit: 'clients',
      status: 'at_risk',
      progressPercentage: 85,
      description: 'New client acquisition',
      assignedTo: ['Alice'],
      startDate: '2024-01-01',
      endDate: '2024-01-31',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-15T00:00:00Z',
    },
  ]);

  const [kpis] = useState<KPIMetric[]>([
    {
      id: 'kpi_1',
      name: 'Revenue per Booking',
      currentValue: 87.5,
      targetValue: 100,
      unit: '$',
      status: 'on_track',
      trend: 'up',
      trendPercentage: 5,
      lastUpdated: new Date().toISOString(),
      historicalData: [75, 78, 80, 85, 87.5],
      description: 'Average revenue per booking',
    },
    {
      id: 'kpi_2',
      name: 'Client Retention Rate',
      currentValue: 92,
      targetValue: 95,
      unit: '%',
      status: 'on_track',
      trend: 'stable',
      trendPercentage: 0,
      lastUpdated: new Date().toISOString(),
      historicalData: [88, 89, 90, 91, 92],
      description: 'Percentage of returning clients',
    },
    {
      id: 'kpi_3',
      name: 'Average Booking Value',
      currentValue: 125,
      targetValue: 150,
      unit: '$',
      status: 'at_risk',
      trend: 'down',
      trendPercentage: -3,
      lastUpdated: new Date().toISOString(),
      historicalData: [145, 140, 135, 130, 125],
      description: 'Average value per booking',
    },
  ]);

  const [alerts] = useState([
    {
      id: 'alert_1',
      goalId: '3',
      goalName: 'New Clients',
      type: 'at_risk' as const,
      message: 'Goal is at risk. Current progress: 85%. Need 15 more clients by end of month.',
      severity: 'high' as const,
      createdAt: new Date().toISOString(),
      read: false,
      actionRequired: true,
    },
    {
      id: 'alert_2',
      goalId: 'kpi_3',
      goalName: 'Average Booking Value',
      type: 'off_track' as const,
      message: 'KPI is declining. Average booking value down 3% from last period.',
      severity: 'medium' as const,
      createdAt: new Date().toISOString(),
      read: false,
      actionRequired: false,
    },
  ]);

  const [recommendations] = useState([
    {
      id: 'rec_1',
      goalId: '3',
      goalName: 'New Clients',
      title: 'Increase Marketing Efforts',
      description: 'To reach the new client target, consider increasing marketing spend or referral incentives.',
      action: 'Launch a referral program offering 10% discount for new client referrals',
      impact: 'high' as const,
      basedOn: 'Current progress vs time remaining',
      createdAt: new Date().toISOString(),
    },
    {
      id: 'rec_2',
      goalId: 'kpi_3',
      goalName: 'Average Booking Value',
      title: 'Promote Premium Services',
      description: 'Increase average booking value by promoting premium service packages.',
      action: 'Create bundled service packages at premium pricing',
      impact: 'high' as const,
      basedOn: 'Declining booking value trend',
      createdAt: new Date().toISOString(),
    },
  ]);

  const handleGoalCreate = (goalData: any) => {
    const newGoal: Goal = {
      id: `goal_${Date.now()}`,
      ...goalData,
      status: 'on_track',
      progressPercentage: (goalData.currentValue / goalData.targetValue) * 100,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setGoals([...goals, newGoal]);
  };

  const handleGoalUpdate = (goalId: string, goalData: any) => {
    setGoals(
      goals.map((g) =>
        g.id === goalId
          ? {
              ...g,
              ...goalData,
              progressPercentage: (goalData.currentValue / goalData.targetValue) * 100,
              updatedAt: new Date().toISOString(),
            }
          : g
      )
    );
  };

  const handleGoalDelete = (goalId: string) => {
    setGoals(goals.filter((g) => g.id !== goalId));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Goals & KPIs</h1>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 border-b border-gray-200 overflow-x-auto">
          {[
            { id: 'goals', label: 'Goals', icon: '🎯' },
            { id: 'kpis', label: 'KPI Dashboard', icon: '📊' },
            { id: 'alerts', label: 'Alerts & Recommendations', icon: '🔔' },
            { id: 'team', label: 'Team Comparison', icon: '👥' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 font-medium border-b-2 transition whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'goals' && (
            <GoalManagement
              existingGoals={goals}
              onGoalCreate={handleGoalCreate}
              onGoalUpdate={handleGoalUpdate}
              onGoalDelete={handleGoalDelete}
            />
          )}

          {activeTab === 'kpis' && (
            <KPIDashboard
              kpis={kpis}
              showTrends={true}
              layout="grid"
            />
          )}

          {activeTab === 'alerts' && (
            <GoalAlertsNotifications
              alerts={alerts}
              recommendations={recommendations}
            />
          )}

          {activeTab === 'team' && (
            <TeamIndividualGoalTracking
              goals={[
                {
                  goalId: '1',
                  goalName: 'Monthly Revenue',
                  goalType: 'revenue',
                  teamTarget: 50000,
                  teamCurrent: 42000,
                  teamProgress: 84,
                  teamMembers: [
                    {
                      memberId: 'member_1',
                      memberName: 'Alice',
                      currentValue: 15000,
                      targetValue: 16667,
                      achievementRate: 90,
                      historicalAchievementRates: [75, 80, 85, 88, 90],
                      trend: 'up',
                      lastUpdated: new Date().toISOString(),
                    },
                    {
                      memberId: 'member_2',
                      memberName: 'Bob',
                      currentValue: 14000,
                      targetValue: 16667,
                      achievementRate: 84,
                      historicalAchievementRates: [70, 75, 80, 82, 84],
                      trend: 'up',
                      lastUpdated: new Date().toISOString(),
                    },
                    {
                      memberId: 'member_3',
                      memberName: 'Charlie',
                      currentValue: 13000,
                      targetValue: 16666,
                      achievementRate: 78,
                      historicalAchievementRates: [65, 70, 74, 76, 78],
                      trend: 'up',
                      lastUpdated: new Date().toISOString(),
                    },
                  ],
                  historicalTeamAchievement: [70, 75, 80, 82, 84],
                  historicalIndividualAchievements: {
                    member_1: [75, 80, 85, 88, 90],
                    member_2: [70, 75, 80, 82, 84],
                    member_3: [65, 70, 74, 76, 78],
                  },
                },
              ]}
            />
          )}
        </div>
      </div>
    </div>
  );
}
