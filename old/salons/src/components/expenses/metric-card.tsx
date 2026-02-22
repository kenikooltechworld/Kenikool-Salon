import { Card } from "@/components/ui/card";
import { TrendingUpIcon, TrendingDownIcon } from "@/components/icons";

interface MetricCardProps {
  label: string;
  value: number;
  format?: "currency" | "percentage";
  isPositive?: boolean;
  icon?: React.ReactNode;
}

export function MetricCard({
  label,
  value,
  format = "currency",
  isPositive,
  icon,
}: MetricCardProps) {
  const formattedValue =
    format === "currency"
      ? `₦${Math.abs(value).toFixed(2)}`
      : `${value.toFixed(2)}%`;

  const isValuePositive = isPositive !== undefined ? isPositive : value >= 0;
  const textColor = isValuePositive
    ? "text-[var(--success)]"
    : "text-[var(--destructive)]";
  const bgColor = isValuePositive
    ? "bg-[var(--success)]/10"
    : "bg-[var(--destructive)]/10";

  const TrendIcon = isValuePositive ? TrendingUpIcon : TrendingDownIcon;

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-[var(--muted-foreground)] mb-2">
            {label}
          </p>
          <p className={`text-2xl font-bold ${textColor}`}>
            {formattedValue}
          </p>
        </div>
        <div className={`p-3 rounded-[var(--radius-md)] ${bgColor}`}>
          {icon ? (
            icon
          ) : (
            <TrendIcon size={24} className={textColor} />
          )}
        </div>
      </div>
    </Card>
  );
}
