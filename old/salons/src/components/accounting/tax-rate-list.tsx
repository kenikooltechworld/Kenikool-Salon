import { TaxRate } from "@/lib/api/hooks/useAccounting";
import { PercentIcon, EditIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface TaxRateListProps {
  taxRates: TaxRate[];
  onEdit: (taxRate: TaxRate) => void;
}

export function TaxRateList({ taxRates, onEdit }: TaxRateListProps) {
  if (taxRates.length === 0) {
    return (
      <div className="text-center py-12">
        <PercentIcon
          size={48}
          className="mx-auto text-[var(--muted-foreground)] mb-4"
        />
        <h3 className="text-lg font-semibold mb-2">No tax rates yet</h3>
        <p className="text-[var(--muted-foreground)]">
          Create your first tax rate to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {taxRates.map((taxRate) => (
        <Card
          key={taxRate.id}
          className="p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="p-2 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
                <PercentIcon size={20} className="text-[var(--primary)]" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-semibold">{taxRate.name}</p>
                  <Badge variant="secondary">{taxRate.rate}%</Badge>
                  {!taxRate.active && (
                    <Badge variant="destructive">Inactive</Badge>
                  )}
                </div>
                {taxRate.description && (
                  <p className="text-sm text-[var(--muted-foreground)] mt-1">
                    {taxRate.description}
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-lg font-bold text-[var(--primary)]">
                  {taxRate.rate}%
                </p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  Tax Rate
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(taxRate)}
              >
                <EditIcon size={16} />
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}