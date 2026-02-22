import { MembershipPlan } from "@/lib/api/hooks/useMemberships";
import {
  CreditCardIcon,
  EditIcon,
  TrashIcon,
  CheckIcon,
  EyeIcon,
} from "@/components/icons";

interface MembershipListProps {
  plans: MembershipPlan[];
  onEdit: (plan: MembershipPlan) => void;
  onDelete: (id: string) => void;
  onViewDetails?: (id: string) => void;
}

export function MembershipList({
  plans,
  onEdit,
  onDelete,
  onViewDetails,
}: MembershipListProps) {
  if (plans.length === 0) {
    return (
      <div className="text-center py-12">
        <CreditCardIcon
          size={48}
          className="mx-auto text-muted-foreground mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No membership plans yet</h3>
        <p className="text-muted-foreground">
          Create your first membership plan to offer recurring benefits
        </p>
      </div>
    );
  }

  const getBillingCycleLabel = (cycle: string) => {
    switch (cycle) {
      case "monthly":
        return "per month";
      case "quarterly":
        return "per quarter";
      case "yearly":
        return "per year";
      default:
        return "";
    }
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {plans.map((plan) => (
        <div
          key={plan._id}
          className="bg-card border border-border rounded-[var(--radius-lg)] p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-2">
              <CreditCardIcon size={20} className="text-primary" />
              <h3 className="font-semibold text-lg">{plan.name}</h3>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold text-primary">
                ${plan.price}
              </span>
              <span className="text-sm text-muted-foreground">
                {getBillingCycleLabel(plan.billing_cycle)}
              </span>
            </div>
            {plan.discount_percentage && (
              <p className="text-sm text-green-600 mt-1">
                {plan.discount_percentage}% discount on services
              </p>
            )}
          </div>

          <p className="text-sm text-muted-foreground mb-4">
            {plan.description}
          </p>

          {plan.benefits && plan.benefits.length > 0 && (
            <div className="mb-4 space-y-2">
              {plan.benefits.slice(0, 3).map((benefit, index) => (
                <div key={index} className="flex items-start gap-2 text-sm">
                  <CheckIcon
                    size={16}
                    className="text-green-500 mt-0.5 flex-shrink-0"
                  />
                  <span className="text-foreground">{benefit}</span>
                </div>
              ))}
              {plan.benefits.length > 3 && (
                <p className="text-xs text-muted-foreground">
                  +{plan.benefits.length - 3} more benefits
                </p>
              )}
            </div>
          )}

          <div className="flex gap-2 pt-4 border-t border-border">
            {onViewDetails && (
              <button
                onClick={() => onViewDetails(plan._id)}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue/10 text-blue rounded-[var(--radius-md)] hover:bg-blue/20 transition-colors text-sm font-medium"
              >
                <EyeIcon size={16} />
                View
              </button>
            )}
            <button
              onClick={() => onEdit(plan)}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors text-sm font-medium"
            >
              <EditIcon size={16} />
              Edit
            </button>
            <button
              onClick={() => onDelete(plan._id)}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-destructive/10 text-destructive rounded-[var(--radius-md)] hover:bg-destructive/20 transition-colors text-sm font-medium"
            >
              <TrashIcon size={16} />
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
