'use client';

import { useState, useMemo } from 'react';
import { useGetPlans, MembershipPlan } from '@/lib/api/hooks/useMemberships';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckIcon, XIcon } from '@/components/icons';
import { Spinner } from '@/components/ui/spinner';

interface PlanComparisonProps {
  onSelectPlan?: (plan: MembershipPlan) => void;
  maxPlans?: number;
}

export function PlanComparison({
  onSelectPlan,
  maxPlans = 4,
}: PlanComparisonProps) {
  const { data: plans = [], isLoading } = useGetPlans();
  const [selectedPlanIds, setSelectedPlanIds] = useState<string[]>([]);

  const selectedPlans = useMemo(() => {
    return plans.filter((p) => selectedPlanIds.includes(p._id));
  }, [plans, selectedPlanIds]);

  const allBenefits = useMemo(() => {
    const benefits = new Set<string>();
    selectedPlans.forEach((plan) => {
      plan.benefits?.forEach((benefit) => benefits.add(benefit));
    });
    return Array.from(benefits);
  }, [selectedPlans]);

  const togglePlanSelection = (planId: string) => {
    setSelectedPlanIds((prev) => {
      if (prev.includes(planId)) {
        return prev.filter((id) => id !== planId);
      } else if (prev.length < maxPlans) {
        return [...prev, planId];
      }
      return prev;
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getBillingCycleLabel = (cycle: string) => {
    switch (cycle) {
      case 'monthly':
        return 'per month';
      case 'quarterly':
        return 'per quarter';
      case 'yearly':
        return 'per year';
      default:
        return '';
    }
  };

  const calculateMonthlyPrice = (plan: MembershipPlan) => {
    switch (plan.billing_cycle) {
      case 'monthly':
        return plan.price;
      case 'quarterly':
        return plan.price / 3;
      case 'yearly':
        return plan.price / 12;
      default:
        return plan.price;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Plan Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium">
          Select Plans to Compare (up to {maxPlans})
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {plans.map((plan) => (
            <button
              key={plan._id}
              onClick={() => togglePlanSelection(plan._id)}
              className={`p-4 border rounded-lg transition-all text-left ${
                selectedPlanIds.includes(plan._id)
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <p className="font-semibold">{plan.name}</p>
              <p className="text-sm text-muted-foreground">
                ${plan.price} {getBillingCycleLabel(plan.billing_cycle)}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      {selectedPlans.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left p-4 font-semibold">Feature</th>
                {selectedPlans.map((plan) => (
                  <th key={plan._id} className="text-center p-4 font-semibold">
                    <div className="space-y-2">
                      <p>{plan.name}</p>
                      <Badge variant="info">
                        ${calculateMonthlyPrice(plan).toFixed(2)}/mo
                      </Badge>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {/* Price Row */}
              <tr className="border-b border-border bg-accent/50">
                <td className="p-4 font-medium">Price</td>
                {selectedPlans.map((plan) => (
                  <td key={plan._id} className="text-center p-4">
                    <div>
                      <p className="text-lg font-bold text-primary">
                        ${plan.price}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {getBillingCycleLabel(plan.billing_cycle)}
                      </p>
                    </div>
                  </td>
                ))}
              </tr>

              {/* Discount Row */}
              <tr className="border-b border-border">
                <td className="p-4 font-medium">Service Discount</td>
                {selectedPlans.map((plan) => (
                  <td key={plan._id} className="text-center p-4">
                    {plan.discount_percentage ? (
                      <Badge variant="success">
                        {plan.discount_percentage}% off
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">None</span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Benefits Rows */}
              {allBenefits.map((benefit) => (
                <tr key={benefit} className="border-b border-border">
                  <td className="p-4 text-sm">{benefit}</td>
                  {selectedPlans.map((plan) => (
                    <td key={plan._id} className="text-center p-4">
                      {plan.benefits?.includes(benefit) ? (
                        <CheckIcon size={20} className="mx-auto text-green-500" />
                      ) : (
                        <XIcon size={20} className="mx-auto text-muted-foreground" />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Plan Cards */}
      {selectedPlans.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {selectedPlans.map((plan) => {
            const isPopular = selectedPlans.length > 1 &&
              selectedPlans.reduce((max, p) =>
                p.price > max.price ? p : max
              ) === plan;
            const isBestValue = plan.billing_cycle === 'yearly';

            return (
              <Card
                key={plan._id}
                className={`relative ${
                  isPopular ? 'ring-2 ring-primary' : ''
                }`}
              >
                {isPopular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                    Most Popular
                  </Badge>
                )}
                {isBestValue && (
                  <Badge
                    variant="success"
                    className="absolute -top-3 right-4"
                  >
                    Best Value
                  </Badge>
                )}

                <CardHeader>
                  <CardTitle className="text-lg">{plan.name}</CardTitle>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div>
                    <p className="text-3xl font-bold text-primary">
                      ${plan.price}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {getBillingCycleLabel(plan.billing_cycle)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      ${calculateMonthlyPrice(plan).toFixed(2)}/month
                    </p>
                  </div>

                  {plan.discount_percentage && (
                    <div className="p-2 bg-green-50 border border-green-200 rounded-md">
                      <p className="text-sm text-green-700">
                        {plan.discount_percentage}% discount on services
                      </p>
                    </div>
                  )}

                  {plan.benefits && plan.benefits.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Benefits:</p>
                      <ul className="space-y-1">
                        {plan.benefits.map((benefit, index) => (
                          <li
                            key={index}
                            className="flex items-start gap-2 text-sm"
                          >
                            <CheckIcon
                              size={16}
                              className="text-green-500 mt-0.5 flex-shrink-0"
                            />
                            <span>{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <Button
                    onClick={() => onSelectPlan?.(plan)}
                    className="w-full"
                    variant={isPopular ? 'default' : 'outline'}
                  >
                    Subscribe
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {selectedPlans.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            Select plans above to compare them side-by-side
          </p>
        </div>
      )}
    </div>
  );
}
