import { ReactNode } from "react";
import { Link } from "react-router-dom";
import { LockIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTenant } from "@/lib/api/hooks/useTenant";

interface FeatureGateProps {
  feature: string;
  requiredPlan: "professional" | "enterprise";
  children: ReactNode;
  fallback?: ReactNode;
}

export function FeatureGate({
  feature,
  requiredPlan,
  children,
  fallback,
}: FeatureGateProps) {
  const { data: tenant, isLoading } = useTenant();

  // Show loading state
  if (isLoading) {
    return <>{children}</>;
  }

  // Check if user has access based on their current plan
  const currentPlan = tenant?.subscription_plan || "starter";

  // Plan hierarchy: starter < professional < enterprise
  const planHierarchy: Record<string, number> = {
    starter: 1,
    professional: 2,
    enterprise: 3,
  };

  const hasAccess = planHierarchy[currentPlan] >= planHierarchy[requiredPlan];

  if (hasAccess) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  return (
    <Card className="p-6">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10">
          <LockIcon size={32} className="text-primary" />
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-2">{feature} is Locked</h3>
          <p className="text-muted-foreground mb-4">
            Upgrade to the {requiredPlan} plan to unlock this feature
          </p>
        </div>
        <Link to="/dashboard/settings/billing">
          <Button>
            <LockIcon size={16} className="mr-2" />
            Upgrade Plan
          </Button>
        </Link>
      </div>
    </Card>
  );
}
