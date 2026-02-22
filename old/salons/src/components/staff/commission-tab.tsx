import { Card } from "@/components/ui/card";
import type { Stylist } from "@/lib/api/types";

interface StylistStatistics {
  totalRevenue: number;
}

interface CommissionTabProps {
  stylist: Stylist;
  statistics: StylistStatistics | null;
}

export function CommissionTab({ stylist, statistics }: CommissionTabProps) {
  return (
    <Card className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
        Commission Details
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Commission Type</p>
          <p className="text-lg font-bold capitalize">
            {stylist.commission_type}
          </p>
        </div>
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Commission Value</p>
          <p className="text-lg font-bold">
            {stylist.commission_type === "percentage"
              ? `${stylist.commission_value}%`
              : `₦${(stylist.commission_value || 0).toLocaleString()}`}
          </p>
        </div>
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Total Revenue</p>
          <p className="text-lg font-bold">
            ₦{(statistics?.totalRevenue || 0).toLocaleString()}
          </p>
        </div>
      </div>
    </Card>
  );
}
