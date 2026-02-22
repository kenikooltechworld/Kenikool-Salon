import React, { useState } from 'react';
import { Plus, Edit2, Trash2, AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface GoalFormData {
  name: string;
  goalType: 'revenue' | 'bookings' | 'clients' | 'custom';
  targetValue: number;
  currentValue: number;
  unit: string;
  description: string;
  assignedTo: string[];
  startDate: string;
  endDate: string;
}

interface Goal extends GoalFormData {
  id: string;
  status: 'on_track' | 'at_risk' | 'achieved' | 'missed';
  progressPercentage: number;
  createdAt: string;
  updatedAt: string;
}

interface GoalManagementProps {
  onGoalCreate?: (goal: GoalFormData) => void;
  onGoalUpdate?: (goalId: string, goal: GoalFormData) => void;
  onGoalDelete?: (goalId: string) => void;
  existingGoals?: Goal[];
}

const GOAL_TYPES = [
  { value: 'revenue', label: 'Revenue', icon: '💰', description: 'Track revenue targets' },
  { value: 'bookings', label: 'Bookings', icon: '📅', description: 'Track booking targets' },
  { value: 'clients', label: 'Clients', icon: '👥', description: 'Track client acquisition' },
  { value: 'custom', label: 'Custom', icon: '⚙️', description: 'Create custom metrics' },
];

const GOAL_UNITS: Record<string, string[]> = {
  revenue: ['$', '€', '£', '¥'],
  bookings: ['bookings', 'appointments'],
  clients: ['clients', 'new clients'],
  custom: ['units', 'items', '%', 'count'],
};

export const GoalManagement: React.FC<GoalManagementProps> = ({
  onGoalCreate,
  onGoalUpdate,
  onGoalDelete,
  existingGoals = [],
}) => {
  const [showForm, setShowForm] = useState(false);
  const [editingGoalId, setEditingGoalId] = useState<string | null>(null);
  const [formData, setFormData] = useState<GoalFormData>({
    name: '',
    goalType: 'revenue',
    targetValue: 0,
    currentValue: 0,
    unit: '$',
    description: '',
    assignedTo: [],
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  });

  const handleGoalTypeChange = (goalType: GoalFormData['goalType']) => {
    setFormData({
      ...formData,
      goalType,
      unit: GOAL_UNITS[goalType]?.[0] || '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || formData.targetValue <= 0) {
      alert('Please fill in all required fields');
      return;
    }

    if (editingGoalId) {
      onGoalUpdate?.(editingGoalId, formData);
      setEditingGoalId(null);
    } else {
      onGoalCreate?.(formData);
    }

    setFormData({
      name: '',
      goalType: 'revenue',
      targetValue: 0,
      currentValue: 0,
      unit: '$',
      description: '',
      assignedTo: [],
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    });
    setShowForm(false);
  };

  const handleEditGoal = (goal: Goal) => {
    setFormData({
      name: goal.name,
      goalType: goal.goalType,
      targetValue: goal.targetValue,
      currentValue: goal.currentValue,
      unit: goal.unit,
      description: goal.description,
      assignedTo: goal.assignedTo,
      startDate: goal.startDate,
      endDate: goal.endDate,
    });
    setEditingGoalId(goal.id);
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingGoalId(null);
    setFormData({
      name: '',
      goalType: 'revenue',
      targetValue: 0,
      currentValue: 0,
      unit: '$',
      description: '',
      assignedTo: [],
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    });
  };

  const getStatusIcon = (status: Goal['status']) => {
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

  const getStatusColor = (status: Goal['status']) => {
    switch (status) {
      case 'achieved':
        return 'bg-green-100 text-green-800';
      case 'on_track':
        return 'bg-blue-100 text-blue-800';
      case 'at_risk':
        return 'bg-orange-100 text-orange-800';
      case 'missed':
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Goal Management</h2>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            <Plus className="w-5 h-5" />
            Create Goal
          </button>
        )}
      </div>

      {/* Goal Creation Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-600">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingGoalId ? 'Edit Goal' : 'Create New Goal'}
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Goal Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Goal Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Q1 Revenue Target"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Goal Type Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Goal Type *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {GOAL_TYPES.map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => handleGoalTypeChange(type.value as GoalFormData['goalType'])}
                    className={`p-3 rounded-lg border-2 transition text-center ${
                      formData.goalType === type.value
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="text-2xl mb-1">{type.icon}</div>
                    <div className="text-sm font-medium text-gray-900">{type.label}</div>
                    <div className="text-xs text-gray-500">{type.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Target Value and Unit */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Value *
                </label>
                <input
                  type="number"
                  value={formData.targetValue}
                  onChange={(e) =>
                    setFormData({ ...formData, targetValue: parseFloat(e.target.value) || 0 })
                  }
                  placeholder="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit
                </label>
                <select
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {GOAL_UNITS[formData.goalType]?.map((unit) => (
                    <option key={unit} value={unit}>
                      {unit}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Current Value */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Value
              </label>
              <input
                type="number"
                value={formData.currentValue}
                onChange={(e) =>
                  setFormData({ ...formData, currentValue: parseFloat(e.target.value) || 0 })
                }
                placeholder="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Add any additional details about this goal..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.startDate}
                  onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={formData.endDate}
                  onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition font-medium"
              >
                {editingGoalId ? 'Update Goal' : 'Create Goal'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Goals List */}
      <div className="space-y-3">
        {existingGoals.length === 0 ? (
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <p className="text-gray-600">No goals created yet. Create your first goal to get started!</p>
          </div>
        ) : (
          existingGoals.map((goal) => {
            const progressPercentage = (goal.currentValue / goal.targetValue) * 100;
            return (
              <div
                key={goal.id}
                className="bg-white rounded-lg shadow p-4 hover:shadow-md transition"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{goal.name}</h4>
                      <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-700">
                        {goal.goalType}
                      </span>
                    </div>
                    {goal.description && (
                      <p className="text-sm text-gray-600">{goal.description}</p>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {getStatusIcon(goal.status)}
                      <span
                        className={`text-xs font-semibold px-2 py-1 rounded ${getStatusColor(
                          goal.status
                        )}`}
                      >
                        {goal.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>

                    <button
                      onClick={() => handleEditGoal(goal)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded transition"
                      title="Edit goal"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => onGoalDelete?.(goal.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded transition"
                      title="Delete goal"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-2">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>
                      {goal.unit}
                      {goal.currentValue.toLocaleString()} / {goal.unit}
                      {goal.targetValue.toLocaleString()}
                    </span>
                    <span className="font-medium">{Math.min(progressPercentage, 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${getProgressColor(
                        progressPercentage
                      )}`}
                      style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Date Range */}
                <div className="text-xs text-gray-500">
                  {new Date(goal.startDate).toLocaleDateString()} -{' '}
                  {new Date(goal.endDate).toLocaleDateString()}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
