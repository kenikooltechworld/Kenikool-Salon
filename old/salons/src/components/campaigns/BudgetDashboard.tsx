import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, AlertTriangle, TrendingUp } from 'lucide-react';
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
} from 'recharts';

interface BudgetData {
  total_budget: number;
  spent: number;
  remaining: number;
  percentage_used: number;
  monthly_limit: number;
  monthly_spent: number;
  campaigns: Array<{
    id: string;
    name: string;
    budget: number;
    spent: number;
    status: string;
  }>;
  spending_trends: Array<{
    date: string;
    spent: number;
    budget: number;
  }>;
}

interface BudgetDashboardProps {
  tenantId: string;
}

export const BudgetDashboard: React.FC<BudgetDashboardProps> = ({ tenantId }) => {
  const [budgetData, setBudgetData] = useState<BudgetData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBudgetData();
  }, [tenantId]);

  const fetchBudgetData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/campaigns/budget-summary');
      if (!response.ok) throw new Error('Failed to fetch budget data');
      const data = await response.json();
      setBudgetData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load budget data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!budgetData) {
    return (
      <Card>
        <CardContent className="pt-6 text-center text-gray-500">
          No budget data available
        </CardContent>
      </Card>
    );
  }

  const budgetPercentage = (budgetData.spent / budgetData.total_budget) * 100;
  const monthlyPercentage = (budgetData.monthly_spent / budgetData.monthly_limit) * 100;
  const isNearLimit = budgetPercentage >= 80;
  const isOverLimit = budgetPercentage > 100;

  return (
    <div className="space-y-4">
      {/* Alerts */}
      {isOverLimit && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Budget limit exceeded! You've spent ${budgetData.spent.toFixed(2)} of ${budgetData.total_budget.toFixed(2)}
          </AlertDescription>
        </Alert>
      )}

      {isNearLimit && !isOverLimit && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Approaching budget limit. {budgetPercentage.toFixed(1)}% of budget used.
          </AlertDescription>
        </Alert>
      )}

      {/* Budget Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${budgetData.total_budget.toFixed(2)}</div>
            <p className="text-xs text-gray-500 mt-1">Campaign budget limit</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Spent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${budgetData.spent.toFixed(2)}</div>
            <p className="text-xs text-gray-500 mt-1">{budgetPercentage.toFixed(1)}% of budget</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Remaining</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${budgetData.remaining.toFixed(2)}</div>
            <p className="text-xs text-gray-500 mt-1">Available to spend</p>
          </CardContent>
        </Card>
      </div>

      {/* Budget Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Budget Usage</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Campaign Budget</span>
              <Badge variant={isOverLimit ? 'destructive' : isNearLimit ? 'secondary' : 'default'}>
                {budgetPercentage.toFixed(1)}%
              </Badge>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  isOverLimit ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(budgetPercentage, 100)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Monthly Budget</span>
              <Badge variant={monthlyPercentage > 100 ? 'destructive' : monthlyPercentage >= 80 ? 'secondary' : 'default'}>
                {monthlyPercentage.toFixed(1)}%
              </Badge>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  monthlyPercentage > 100 ? 'bg-red-500' : monthlyPercentage >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(monthlyPercentage, 100)}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Spending Trends */}
      {budgetData.spending_trends && budgetData.spending_trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Spending Trends</CardTitle>
            <CardDescription>Daily spending over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={budgetData.spending_trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="spent"
                  stroke="#3b82f6"
                  name="Spent"
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="budget"
                  stroke="#10b981"
                  name="Budget"
                  dot={false}
                  strokeDasharray="5 5"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Campaign Breakdown */}
      {budgetData.campaigns && budgetData.campaigns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Campaign Budget Breakdown</CardTitle>
            <CardDescription>Budget allocation by campaign</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={budgetData.campaigns}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                <Legend />
                <Bar dataKey="budget" fill="#3b82f6" name="Budget" />
                <Bar dataKey="spent" fill="#ef4444" name="Spent" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
