import { useState } from "react";
import {
  useGetLoyaltyBalance,
  useGetLoyaltyHistory,
  useEarnPoints,
  useRedeemPoints,
  type LoyaltyTransaction,
} from "@/lib/api/hooks/useLoyalty";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  TrophyIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  StarIcon,
} from "@/components/icons";

interface LoyaltyBalanceProps {
  clientId: string;
}

export function LoyaltyBalance({ clientId }: LoyaltyBalanceProps) {
  const { data: balance, isLoading } = useGetLoyaltyBalance(clientId);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Spinner size="lg" />
        </CardContent>
      </Card>
    );
  }

  if (!balance) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <p className="text-(--muted-foreground)">No loyalty data available</p>
        </CardContent>
      </Card>
    );
  }

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      bronze: "bg-orange-600",
      silver: "bg-gray-400",
      gold: "bg-yellow-500",
      platinum: "bg-purple-600",
    };
    return colors[tier.toLowerCase()] || colors.bronze;
  };

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case "platinum":
        return "💎";
      case "gold":
        return "🥇";
      case "silver":
        return "🥈";
      default:
        return "🥉";
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card variant="gradient">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <StarIcon size={24} />
            Current Balance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold text-white">
            {balance.points_balance.toLocaleString()}
          </p>
          <p className="text-white/80 mt-1">points</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrophyIcon size={24} className="text-(--primary)" />
            Loyalty Tier
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <span className="text-3xl">{getTierIcon(balance.tier)}</span>
            <div>
              <Badge
                className={`${getTierColor(balance.tier)} text-white border-0`}
              >
                {balance.tier.toUpperCase()}
              </Badge>
              {balance.tier_progress && (
                <p className="text-sm text-(--muted-foreground) mt-2">
                  {balance.tier_progress.points_to_next || 0} points to next
                  tier
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUpIcon size={24} className="text-green-500" />
            Lifetime Points
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">
            {balance.lifetime_points.toLocaleString()}
          </p>
          <p className="text-(--muted-foreground) mt-1">total earned</p>
        </CardContent>
      </Card>
    </div>
  );
}

interface LoyaltyHistoryProps {
  clientId: string;
  limit?: number;
}

export function LoyaltyHistory({ clientId, limit = 50 }: LoyaltyHistoryProps) {
  const [offset, setOffset] = useState(0);
  const { data: history, isLoading } = useGetLoyaltyHistory(
    clientId,
    limit,
    offset
  );

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Spinner size="lg" />
        </CardContent>
      </Card>
    );
  }

  if (!history || history.transactions.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-8">
          <StarIcon
            size={48}
            className="mx-auto text-(--muted-foreground) mb-4"
          />
          <h3 className="text-lg font-semibold mb-2">No transaction history</h3>
          <p className="text-(--muted-foreground)">
            Loyalty points transactions will appear here
          </p>
        </CardContent>
      </Card>
    );
  }

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case "earn":
        return <TrendingUpIcon size={20} className="text-green-500" />;
      case "redeem":
        return <TrendingDownIcon size={20} className="text-red-500" />;
      default:
        return <StarIcon size={20} className="text-(--muted-foreground)" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Transaction History</CardTitle>
          <div className="flex gap-4 text-sm">
            <div>
              <span className="text-(--muted-foreground)">Total Earned:</span>
              <span className="ml-2 font-semibold text-green-600">
                +{history.total_earned.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-(--muted-foreground)">Total Redeemed:</span>
              <span className="ml-2 font-semibold text-red-600">
                -{history.total_redeemed.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {history.transactions.map((transaction: LoyaltyTransaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between p-4 bg-(--muted) rounded-lg hover:bg-(--muted)/80 transition-colors"
            >
              <div className="flex items-center gap-3">
                {getTransactionIcon(transaction.transaction_type)}
                <div>
                  <p className="font-medium">
                    {transaction.description || transaction.transaction_type}
                  </p>
                  <div className="flex items-center gap-2 text-sm text-(--muted-foreground)">
                    <span>
                      {new Date(transaction.created_at).toLocaleDateString()}
                    </span>
                    {transaction.reference_type && (
                      <>
                        <span>•</span>
                        <span className="capitalize">
                          {transaction.reference_type}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <p
                  className={`text-lg font-semibold ${
                    transaction.points > 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {transaction.points > 0 ? "+" : ""}
                  {transaction.points.toLocaleString()}
                </p>
                <p className="text-sm text-(--muted-foreground)">
                  Balance: {transaction.balance_after.toLocaleString()}
                </p>
              </div>
            </div>
          ))}
        </div>

        {history.transactions.length >= limit && (
          <div className="flex justify-center gap-2 mt-6">
            <button
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-(--muted) hover:bg-(--muted)/80 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setOffset(offset + limit)}
              className="px-4 py-2 text-sm font-medium rounded-lg bg-(--muted) hover:bg-(--muted)/80"
            >
              Next
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface LoyaltyEarnRedeemFormProps {
  clientId: string;
  type: "earn" | "redeem";
  onSuccess?: () => void;
}

export function LoyaltyEarnRedeemForm({
  clientId,
  type,
  onSuccess,
}: LoyaltyEarnRedeemFormProps) {
  const earnMutation = useEarnPoints();
  const redeemMutation = useRedeemPoints();
  const [points, setPoints] = useState<number>(0);
  const [description, setDescription] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const data = {
        client_id: clientId,
        points,
        description,
      };

      if (type === "earn") {
        await earnMutation.mutateAsync(data);
      } else {
        await redeemMutation.mutateAsync(data);
      }

      setPoints(0);
      setDescription("");
      onSuccess?.();
    } catch (error) {
      console.error("Failed to process loyalty points:", error);
    }
  };

  const mutation = type === "earn" ? earnMutation : redeemMutation;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {type === "earn" ? "Award Points" : "Redeem Points"}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Points <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="1"
              value={points || ""}
              onChange={(e) => setPoints(parseInt(e.target.value))}
              className="w-full px-3 py-2 border-2 rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={`Reason for ${
                type === "earn" ? "awarding" : "redeeming"
              } points`}
              className="w-full px-3 py-2 border-2 rounded-lg"
            />
          </div>

          <button
            type="submit"
            disabled={mutation.isPending}
            className={`w-full py-2 px-4 rounded-lg font-medium ${
              type === "earn"
                ? "bg-green-600 hover:bg-green-700"
                : "bg-red-600 hover:bg-red-700"
            } text-white disabled:opacity-50`}
          >
            {mutation.isPending ? (
              <Spinner size="sm" />
            ) : type === "earn" ? (
              "Award Points"
            ) : (
              "Redeem Points"
            )}
          </button>
        </form>
      </CardContent>
    </Card>
  );
}
