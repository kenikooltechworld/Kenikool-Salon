import { Card } from "@/components/ui/card";

interface CostSummaryTotalProps {
  subtotal: number;
  discount?: number;
  tax?: number;
  total: number;
  currency?: string;
}

export function CostSummaryTotal({
  subtotal,
  discount = 0,
  tax = 0,
  total,
  currency = "₦",
}: CostSummaryTotalProps) {
  return (
    <Card className="p-4 bg-muted/50">
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Subtotal</span>
          <span>
            {currency}
            {subtotal.toLocaleString()}
          </span>
        </div>

        {discount > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Discount</span>
            <span className="text-success">
              -{currency}
              {discount.toLocaleString()}
            </span>
          </div>
        )}

        {tax > 0 && (
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Tax</span>
            <span>
              {currency}
              {tax.toLocaleString()}
            </span>
          </div>
        )}

        <div className="border-t pt-2 flex justify-between font-semibold">
          <span>Total</span>
          <span className="text-lg">
            {currency}
            {total.toLocaleString()}
          </span>
        </div>
      </div>
    </Card>
  );
}
