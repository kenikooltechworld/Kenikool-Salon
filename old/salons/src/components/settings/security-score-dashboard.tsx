import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { ShieldIcon, AlertTriangleIcon, CheckIcon } from "@/components/icons";
import { useSecurityScore } from "@/lib/api/hooks/useSettings";

export function SecurityScoreDashboard() {
  const { data: securityData, isLoading } = useSecurityScore();

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  const score = securityData?.score || 0;
  const recommendations = securityData?.recommendations || [];

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    return "Needs Improvement";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-100 dark:bg-green-900";
    if (score >= 60) return "bg-yellow-100 dark:bg-yellow-900";
    return "bg-red-100 dark:bg-red-900";
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Security Score
      </h2>

      {/* Score Display */}
      <div className={`${getScoreBgColor(score)} p-6 rounded-lg mb-6`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-2">
              Your Security Score
            </p>
            <div className="flex items-baseline gap-2">
              <span className={`text-4xl font-bold ${getScoreColor(score)}`}>
                {score}
              </span>
              <span className="text-lg text-muted-foreground">/100</span>
            </div>
            <p className={`text-sm font-medium mt-2 ${getScoreColor(score)}`}>
              {getScoreLabel(score)}
            </p>
          </div>
          <ShieldIcon
            size={64}
            className={`${getScoreColor(score)} opacity-20`}
          />
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-foreground mb-3">
          Score Breakdown
        </h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Password Strength</span>
            <span className="font-medium">25 points</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Two-Factor Authentication</span>
            <span className="font-medium">30 points</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Recent Password Change</span>
            <span className="font-medium">15 points</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">No Suspicious Activity</span>
            <span className="font-medium">15 points</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Email Verified</span>
            <span className="font-medium">10 points</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Phone Verified</span>
            <span className="font-medium">5 points</span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-foreground mb-3">
            Recommendations
          </h3>
          <div className="space-y-2">
            {recommendations.map((recommendation, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 bg-muted rounded-lg"
              >
                <AlertTriangleIcon
                  size={18}
                  className="text-yellow-600 flex-shrink-0 mt-0.5"
                />
                <p className="text-sm text-foreground">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations.length === 0 && (
        <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900 rounded-lg">
          <CheckIcon size={20} className="text-green-600" />
          <p className="text-sm text-green-800 dark:text-green-100">
            Great job! Your account security is in excellent shape.
          </p>
        </div>
      )}
    </Card>
  );
}
