import { Card, CardContent } from "@/components/ui/card";
import { DollarSignIcon } from "@/components/icons";

interface CashDrawerStatusProps {
  expectedBalance: number;
}

export function CashDrawerStatus({ expectedBalance }: CashDrawerStatusProps) {
  return (
    <Card className="bg-green-50 border-green-200">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">Cash Drawer Open</p>
            <p className="text-sm text-muted-foreground">
              Expected Balance: ${expectedBalance.toFixed(2)}
            </p>
          </div>
          <DollarSignIcon className="h-8 w-8 text-[var(--primary)]" />
        </div>
      </CardContent>
    </Card>
  );
}
