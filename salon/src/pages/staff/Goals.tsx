import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  TargetIcon,
  RefreshCwIcon,
  TrophyIcon,
  GiftIcon,
  AlertCircleIcon,
  CalendarIcon,
  TrendingUpIcon,
} from "@/components/icons";
import { GoalsDisplay } from "@/components/staff/GoalsDisplay";
import { TargetProgress } from "@/components/staff/TargetProgress";
import {
  useGoals,
  useGoalAchievements,
  useBonusIncentives,
  usePerformanceVsTargets,
} from "@/hooks/useGoals";

/**
 * Goals page for staff members
 * Displays personal sales and commission targets, progress tracking, and achievement history
 *
 * Features:
 * - Display personal sales targets
 * - Display commission targets
 * - Display progress toward targets (percentage complete)
 * - Display target achievement history
 * - Display bonus/incentive information
 * - Display performance metrics relative to targets
 * - Handle errors with retry capability
 *
 * Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7
 */
export default function Goals() {
  // Fetch goals data
  const {
    data: goalsData,
    isLoading: goalsLoading,
    error: goalsError,
    refetch: refetchGoals,
  } = useGoals();

  // Fetch goal achievements
  const {
    data: achievements = [],
    isLoading: achievementsLoading,
    error: achievementsError,
    refetch: refetchAchievements,
  } = useGoalAchievements();

  // Fetch bonus incentives
  const {
    data: bonuses = [],
    isLoading: bonusesLoading,
    error: bonusesError,
    refetch: refetchBonuses,
  } = useBonusIncentives();

  // Fetch performance vs targets
  const {
    data: performanceData,
    isLoading: performanceLoading,
    error: performanceError,
    refetch: refetchPerformance,
  } = usePerformanceVsTargets();

  const handleRefreshAll = () => {
    refetchGoals();
    refetchAchievements();
    refetchBonuses();
    refetchPerformance();
  };

  const isLoading =
    goalsLoading || achievementsLoading || bonusesLoading || performanceLoading;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <TargetIcon size={28} className="text-primary" />
            My Goals & Targets
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your progress toward sales and commission targets
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleRefreshAll}
            variant="outline"
            size="sm"
            disabled={isLoading}
            className="self-start sm:self-auto"
          >
            <RefreshCwIcon size={16} className="mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Goals Overview Summary */}
      {goalsData && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Goals */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TargetIcon size={16} />
                Total Goals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-foreground">
                {goalsData.total_goals}
              </p>
              <p className="text-xs text-muted-foreground mt-1">All goals</p>
            </CardContent>
          </Card>

          {/* Active Goals */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrendingUpIcon size={16} />
                Active Goals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-foreground">
                {goalsData.active_goals}
              </p>
              <p className="text-xs text-muted-foreground mt-1">In progress</p>
            </CardContent>
          </Card>

          {/* Completed Goals */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <TrophyIcon size={16} />
                Completed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-foreground">
                {goalsData.completed_goals}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Achieved</p>
            </CardContent>
          </Card>

          {/* Overall Progress */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <CalendarIcon size={16} />
                Overall Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-foreground">
                {goalsData.overall_progress.toFixed(1)}%
              </p>
              <p className="text-xs text-muted-foreground mt-1">Average</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Goals Display - Personal Sales and Commission Targets */}
      <GoalsDisplay
        goals={goalsData?.goals || []}
        isLoading={goalsLoading}
        error={goalsError?.message}
        onRetry={refetchGoals}
      />

      {/* Performance vs Targets */}
      <TargetProgress
        salesVsTarget={performanceData?.sales_vs_target}
        commissionVsTarget={performanceData?.commission_vs_target}
        appointmentsVsTarget={performanceData?.appointments_vs_target}
        isLoading={performanceLoading}
        error={performanceError?.message}
        onRetry={refetchPerformance}
      />

      {/* Bonus & Incentive Information */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <GiftIcon size={20} />
              Bonuses & Incentives
            </CardTitle>
            {bonusesError && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetchBonuses()}
                title="Retry loading bonuses"
                className="px-2"
              >
                <RefreshCwIcon size={14} />
              </Button>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Available bonuses and incentive programs
          </p>
        </CardHeader>
        <CardContent>
          {bonusesLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : bonusesError ? (
            <div className="text-center py-8">
              <AlertCircleIcon
                size={48}
                className="mx-auto text-destructive mb-3"
              />
              <p className="text-sm text-destructive font-medium mb-2">
                Unable to load bonuses
              </p>
              <p className="text-xs text-muted-foreground mb-4">
                {bonusesError.message}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetchBonuses()}
              >
                <RefreshCwIcon size={14} className="mr-1" />
                Retry
              </Button>
            </div>
          ) : bonuses.length === 0 ? (
            <div className="text-center py-8">
              <GiftIcon
                size={48}
                className="mx-auto text-muted-foreground mb-3"
              />
              <p className="text-muted-foreground">
                No active bonuses or incentives at this time. Check back later
                for new opportunities!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {bonuses.map((bonus) => (
                <div
                  key={bonus.id}
                  className={`p-4 border rounded-lg space-y-2 ${
                    bonus.active
                      ? "border-primary/50 bg-primary/5"
                      : "border-border bg-muted/30"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-foreground">
                          {bonus.name}
                        </h4>
                        <Badge
                          variant={bonus.active ? "default" : "outline"}
                          className="text-xs"
                        >
                          {bonus.active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {bonus.description}
                      </p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-lg font-bold text-primary">
                        ₦
                        {bonus.bonus_amount.toLocaleString("en-NG", {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-border">
                    <p className="text-xs text-muted-foreground">
                      <span className="font-medium">Criteria:</span>{" "}
                      {bonus.criteria}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Target Achievement History */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <TrophyIcon size={20} />
              Achievement History
            </CardTitle>
            {achievementsError && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetchAchievements()}
                title="Retry loading achievements"
                className="px-2"
              >
                <RefreshCwIcon size={14} />
              </Button>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Your completed goals and earned bonuses
          </p>
        </CardHeader>
        <CardContent>
          {achievementsLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : achievementsError ? (
            <div className="text-center py-8">
              <AlertCircleIcon
                size={48}
                className="mx-auto text-destructive mb-3"
              />
              <p className="text-sm text-destructive font-medium mb-2">
                Unable to load achievements
              </p>
              <p className="text-xs text-muted-foreground mb-4">
                {achievementsError.message}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetchAchievements()}
              >
                <RefreshCwIcon size={14} className="mr-1" />
                Retry
              </Button>
            </div>
          ) : achievements.length === 0 ? (
            <div className="text-center py-8">
              <TrophyIcon
                size={48}
                className="mx-auto text-muted-foreground mb-3"
              />
              <p className="text-muted-foreground">
                No achievements yet. Keep working toward your goals to earn your
                first achievement!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className="p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 bg-green-500/10 rounded-full flex items-center justify-center shrink-0">
                        <TrophyIcon size={20} className="text-green-500" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-foreground">
                          Goal Achieved
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(achievement.achieved_at).toLocaleDateString(
                            "en-NG",
                            {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            },
                          )}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">
                          Target: ₦
                          {achievement.target_value.toLocaleString("en-NG", {
                            maximumFractionDigits: 2,
                          })}
                        </p>
                        <p className="font-bold text-foreground">
                          Achieved: ₦
                          {achievement.achieved_value.toLocaleString("en-NG", {
                            maximumFractionDigits: 2,
                          })}
                        </p>
                      </div>
                      {achievement.bonus_earned && (
                        <Badge
                          variant="default"
                          className="bg-green-500 text-xs"
                        >
                          +₦
                          {achievement.bonus_earned.toLocaleString("en-NG", {
                            maximumFractionDigits: 2,
                          })}{" "}
                          bonus
                        </Badge>
                      )}
                    </div>
                  </div>
                  {achievement.incentive_details && (
                    <div className="mt-3 pt-3 border-t border-border">
                      <p className="text-xs text-muted-foreground">
                        {achievement.incentive_details}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
