import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface Goal {
  id: string;
  staff_id: string;
  goal_type: "sales" | "commission" | "appointments" | "customer_satisfaction";
  target_value: number;
  current_value: number;
  period_start: string;
  period_end: string;
  status: "active" | "completed" | "expired";
  created_at: string;
  updated_at: string;
}

export interface GoalProgress {
  goal: Goal;
  progress_percentage: number;
  remaining_value: number;
  days_remaining: number;
  on_track: boolean;
}

export interface GoalsSummary {
  goals: GoalProgress[];
  total_goals: number;
  completed_goals: number;
  active_goals: number;
  overall_progress: number;
}

export interface GoalAchievement {
  id: string;
  goal_id: string;
  staff_id: string;
  achieved_at: string;
  target_value: number;
  achieved_value: number;
  bonus_earned?: number;
  incentive_details?: string;
}

export interface BonusIncentive {
  id: string;
  name: string;
  description: string;
  bonus_amount: number;
  criteria: string;
  active: boolean;
}

/**
 * Fetch current staff member's goals and targets
 * Displays personal sales targets, commission targets, and progress
 */
export function useGoals() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-goals"],
    queryFn: async () => {
      const { data } = await apiClient.get<GoalsSummary>(
        `/staff/${user?.id}/goals`,
      );
      return (
        data || {
          goals: [],
          total_goals: 0,
          completed_goals: 0,
          active_goals: 0,
          overall_progress: 0,
        }
      );
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch goal achievement history for current staff member
 */
export function useGoalAchievements() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-goal-achievements"],
    queryFn: async () => {
      const { data } = await apiClient.get<GoalAchievement[]>(
        `/staff/${user?.id}/goals/achievements`,
      );
      return data || [];
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch available bonuses and incentives
 */
export function useBonusIncentives() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["bonus-incentives"],
    queryFn: async () => {
      const { data } = await apiClient.get<BonusIncentive[]>(
        `/staff/${user?.id}/bonuses`,
      );
      return data || [];
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch performance metrics relative to targets
 */
export function usePerformanceVsTargets() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["performance-vs-targets"],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        sales_vs_target: {
          target: number;
          actual: number;
          percentage: number;
        };
        commission_vs_target: {
          target: number;
          actual: number;
          percentage: number;
        };
        appointments_vs_target: {
          target: number;
          actual: number;
          percentage: number;
        };
      }>(`/staff/${user?.id}/performance-vs-targets`);
      return (
        data || {
          sales_vs_target: { target: 0, actual: 0, percentage: 0 },
          commission_vs_target: { target: 0, actual: 0, percentage: 0 },
          appointments_vs_target: { target: 0, actual: 0, percentage: 0 },
        }
      );
    },
    enabled: !!user?.id,
  });
}
