import { useState } from "react";
import { Check, Crown, Star, Zap } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  usePublicMembershipTiers,
  useSubscribeToMembership,
  useMyMembership,
  type MembershipTier,
} from "@/hooks/useMemberships";
import { useToast } from "@/components/ui/toast";

export default function Memberships() {
  const { data: tiers, isLoading } = usePublicMembershipTiers();
  const { data: myMembership } = useMyMembership();
  const subscribe = useSubscribeToMembership();
  const { toast } = useToast();
  const [selectedTier, setSelectedTier] = useState<MembershipTier | null>(null);

  const handleSubscribe = async (tierId: string) => {
    try {
      // In a real implementation, this would open a payment modal
      // For now, we'll just show a toast
      toast({
        title: "Coming Soon",
        description: "Payment integration for memberships is coming soon",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to subscribe to membership",
        variant: "destructive",
      });
    }
  };

  const getTierIcon = (tierName: string) => {
    const name = tierName.toLowerCase();
    if (name.includes("vip") || name.includes("premium")) return Crown;
    if (name.includes("gold") || name.includes("platinum")) return Star;
    return Zap;
  };

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Membership Plans</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Join our exclusive membership program and enjoy amazing benefits,
            discounts, and priority access
          </p>
        </div>

        {myMembership && (
          <Card className="p-6 mb-8 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/20">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Current Membership</h3>
                <p className="text-2xl font-bold mt-1">
                  {myMembership.tier_name}
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  {myMembership.services_remaining_this_cycle} services
                  remaining this cycle
                </p>
              </div>
              <Badge variant="default" className="text-lg px-4 py-2">
                {myMembership.status}
              </Badge>
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {tiers?.map((tier) => {
            const Icon = getTierIcon(tier.name);
            const isCurrentTier = myMembership?.tier_id === tier.id;

            return (
              <Card
                key={tier.id}
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
                        {(
                          tier.monthly_price * 12 -
                          tier.annual_price
                        ).toLocaleString()}{" "}
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
                      <span>
                        {tier.free_services_per_month} free services per month
                      </span>
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

                  <Button
                    className="w-full"
                    size="lg"
                    disabled={isCurrentTier}
                    onClick={() => handleSubscribe(tier.id)}
                  >
                    {isCurrentTier ? "Current Plan" : "Subscribe Now"}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>

        {(!tiers || tiers.length === 0) && (
          <Card className="p-12 text-center">
            <h3 className="text-lg font-semibold mb-2">
              No membership plans available
            </h3>
            <p className="text-muted-foreground">
              Check back soon for exclusive membership offers
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
