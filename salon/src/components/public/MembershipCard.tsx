import { Check, Crown, Star, Zap } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { MembershipTier } from "@/hooks/useMemberships";

interface MembershipCardProps {
  tier: MembershipTier;
  isCurrentTier?: boolean;
  onSubscribe?: (tierId: string) => void;
}

export default function MembershipCard({
  tier,
  isCurrentTier = false,
  onSubscribe,
}: MembershipCardProps) {
  const getTierIcon = (tierName: string) => {
    const name = tierName.toLowerCase();
    if (name.includes("vip") || name.includes("premium")) return Crown;
    if (name.includes("gold") || name.includes("platinum")) return Star;
    return Zap;
  };

  const Icon = getTierIcon(tier.name);

  return (
    <Card
      className={`relative overflow-hidden transition-all hover:shadow-lg ${
        isCurrentTier ? "border-blue-500 border-2" : ""
      }`}
    >
      {isCurrentTier && (
        <div className="absolute top-0 right-0 bg-blue-500 text-white px-4 py-1 text-sm font-medium">
          Current Plan
        </div>
      )}

      <div className="p-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary/10 rounded-lg">
            <Icon className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h3 className="text-2xl font-bold">{tier.name}</h3>
            {tier.description && (
              <p className="text-sm text-muted-foreground">
                {tier.description}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-bold">
              ₦{tier.monthly_price.toLocaleString()}
            </span>
            <span className="text-muted-foreground">/month</span>
          </div>
          {tier.annual_price && (
            <div className="text-sm text-green-600 font-medium">
              Save ₦
              {(tier.monthly_price * 12 - tier.annual_price).toLocaleString()}{" "}
              with annual billing
            </div>
          )}
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-600" />
            <span className="font-medium">
              {tier.discount_percentage}% discount on all services
            </span>
          </div>

          {tier.priority_booking && (
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-600" />
              <span>Priority booking access</span>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Check className="w-5 h-5 text-green-600" />
            <span>{tier.free_services_per_month} free services per month</span>
          </div>

          {tier.rollover_unused && (
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-600" />
              <span>Unused services rollover</span>
            </div>
          )}

          {tier.benefits.map((benefit, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-600" />
              <span>{benefit.description}</span>
            </div>
          ))}
        </div>

        {onSubscribe && (
          <Button
            className="w-full"
            size="lg"
            disabled={isCurrentTier}
            onClick={() => onSubscribe(tier.id)}
          >
            {isCurrentTier ? "Current Plan" : "Subscribe Now"}
          </Button>
        )}
      </div>
    </Card>
  );
}
