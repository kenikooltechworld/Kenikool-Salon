import { MembershipSubscription } from "@/lib/api/hooks/useMemberships";
import { StarIcon, XIcon, CheckIcon, EyeIcon } from "@/components/icons";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface SubscriptionListProps {
  subscriptions: MembershipSubscription[];
  onCancel: (id: string) => void;
  onViewDetails?: (id: string) => void;
}

export function SubscriptionList({
  subscriptions,
  onCancel,
  onViewDetails,
}: SubscriptionListProps) {
  if (subscriptions.length === 0) {
    return (
      <div className="text-center py-12">
        <StarIcon
          size={48}
          className="mx-auto text-[var(--muted-foreground)] mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No active subscriptions</h3>
        <p className="text-[var(--muted-foreground)]">
          Subscribe clients to membership plans to see them here
        </p>
      </div>
    );
  }

  const getStatusVariant = (status: string) => {
    switch (status) {
      case "active":
        return "success";
      case "cancelled":
        return "error";
      case "expired":
        return "ghost";
      default:
        return "ghost";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-4">
      {subscriptions.map((subscription) => (
        <Card key={subscription._id} hover>
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <StarIcon size={20} className="text-[var(--primary)]" />
                  <h3 className="font-semibold">
                    Client ID: {subscription.client_id}
                  </h3>
                  <Badge variant={getStatusVariant(subscription.status)}>
                    {subscription.status.charAt(0).toUpperCase() +
                      subscription.status.slice(1)}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-[var(--muted-foreground)]">
                      Start Date:
                    </span>
                    <p className="font-medium">
                      {formatDate(subscription.start_date)}
                    </p>
                  </div>
                  {subscription.end_date && (
                    <div>
                      <span className="text-[var(--muted-foreground)]">
                        End Date:
                      </span>
                      <p className="font-medium">
                        {formatDate(subscription.end_date)}
                      </p>
                    </div>
                  )}
                  <div>
                    <span className="text-[var(--muted-foreground)]">
                      Auto-Renew:
                    </span>
                    <p className="font-medium flex items-center gap-1">
                      {subscription.auto_renew ? (
                        <>
                          <CheckIcon
                            size={16}
                            className="text-[var(--success)]"
                          />
                          Yes
                        </>
                      ) : (
                        <>
                          <XIcon size={16} className="text-[var(--error)]" />
                          No
                        </>
                      )}
                    </p>
                  </div>
                </div>
              </div>

              {subscription.status === "active" && (
                <>
                  {onViewDetails && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewDetails(subscription._id)}
                      className="ml-2"
                    >
                      <EyeIcon size={16} />
                      View
                    </Button>
                  )}
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => onCancel(subscription._id)}
                    className="ml-2"
                  >
                    Cancel
                  </Button>
                </>
              )}
              {subscription.status !== "active" && onViewDetails && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewDetails(subscription._id)}
                  className="ml-2"
                >
                  <EyeIcon size={16} />
                  View
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
