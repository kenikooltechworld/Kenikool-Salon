'use client';

import { MembershipSubscription } from '@/lib/api/hooks/useMemberships';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertIcon, CheckIcon } from '@/components/icons';

interface BenefitUsageCardProps {
  subscription: MembershipSubscription;
  className?: string;
}

export function BenefitUsageCard({
  subscription,
  className,
}: BenefitUsageCardProps) {
  if (!subscription.benefit_usage) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-lg">Benefit Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            No benefit usage tracking for this subscription
          </p>
        </CardContent>
      </Card>
    );
  }

  const { usage_count, limit, cycle_start } = subscription.benefit_usage;
  const isUnlimited = limit === -1;
  const usagePercentage = isUnlimited ? 0 : (usage_count / limit) * 100;
  const isNearLimit = usagePercentage >= 80;
  const isAtLimit = usagePercentage >= 100;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Benefit Usage</CardTitle>
          {isAtLimit && (
            <Badge variant="destructive">Limit Reached</Badge>
          )}
          {isNearLimit && !isAtLimit && (
            <Badge variant="warning">Approaching Limit</Badge>
          )}
          {!isNearLimit && !isUnlimited && (
            <Badge variant="success">Available</Badge>
          )}
          {isUnlimited && (
            <Badge variant="info">Unlimited</Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Usage Display */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Usage</span>
            <span className="text-sm text-muted-foreground">
              {usage_count} {isUnlimited ? '/ ∞' : `/ ${limit}`}
            </span>
          </div>

          {!isUnlimited && (
            <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
              <div
                className={`h-3 rounded-full transition-all ${
                  isAtLimit
                    ? 'bg-red-500'
                    : isNearLimit
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                }`}
                style={{
                  width: `${Math.min(usagePercentage, 100)}%`,
                }}
              />
            </div>
          )}
        </div>

        {/* Remaining */}
        {!isUnlimited && (
          <div className="p-3 bg-accent rounded-md">
            <p className="text-sm text-muted-foreground">Remaining</p>
            <p className="text-2xl font-bold">
              {Math.max(0, limit - usage_count)}
            </p>
          </div>
        )}

        {/* Reset Date */}
        <div className="p-3 bg-accent rounded-md">
          <p className="text-sm text-muted-foreground">Resets on</p>
          <p className="font-medium">{formatDate(cycle_start)}</p>
        </div>

        {/* Warnings */}
        {isAtLimit && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-start gap-2">
            <AlertIcon size={18} className="text-red-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">
              You have reached your benefit limit. Usage will reset on{' '}
              {formatDate(cycle_start)}.
            </p>
          </div>
        )}

        {isNearLimit && !isAtLimit && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md flex items-start gap-2">
            <AlertIcon size={18} className="text-yellow-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-yellow-700">
              You are approaching your benefit limit. You have{' '}
              {Math.max(0, limit - usage_count)} uses remaining.
            </p>
          </div>
        )}

        {!isNearLimit && !isUnlimited && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md flex items-start gap-2">
            <CheckIcon size={18} className="text-green-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-green-700">
              You have plenty of benefits available. Keep enjoying your
              membership!
            </p>
          </div>
        )}

        {isUnlimited && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md flex items-start gap-2">
            <CheckIcon size={18} className="text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-blue-700">
              You have unlimited benefits with this plan. Enjoy!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
