import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangleIcon, XCircleIcon, PackageIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/currency";

interface InventoryAlertProps {
  alert: {
    alert_type: string;
    message: string;
    available: boolean;
    current_stock?: number;
    quantity_needed?: number;
    remaining_after_sale?: number;
    threshold?: number;
    alternatives?: Array<{
      id: string;
      name: string;
      price: number;
      quantity: number;
    }>;
  };
  onSelectAlternative?: (alternative: {
    id: string;
    name: string;
    price: number;
    quantity: number;
  }) => void;
  onDismiss?: () => void;
}

export function InventoryAlert({
  alert,
  onSelectAlternative,
  onDismiss,
}: InventoryAlertProps) {
  if (alert.alert_type === "ok") {
    return null;
  }

  const isOutOfStock = alert.alert_type === "out_of_stock";
  const isLowStock = alert.alert_type === "low_stock";

  return (
    <div className="space-y-3">
      <Alert variant={isOutOfStock ? "destructive" : "default"}>
        <div className="flex items-start gap-3">
          {isOutOfStock ? (
            <XCircleIcon className="h-5 w-5 mt-0.5" />
          ) : (
            <AlertTriangleIcon className="h-5 w-5 mt-0.5" />
          )}
          <div className="flex-1">
            <AlertTitle>
              {isOutOfStock ? "Out of Stock" : "Low Stock Warning"}
            </AlertTitle>
            <AlertDescription className="mt-2 space-y-2">
              <p>{alert.message}</p>
              {alert.current_stock !== undefined && (
                <div className="flex gap-4 text-sm">
                  <span>
                    Current: <strong>{alert.current_stock}</strong>
                  </span>
                  {alert.quantity_needed !== undefined && (
                    <span>
                      Needed: <strong>{alert.quantity_needed}</strong>
                    </span>
                  )}
                  {alert.remaining_after_sale !== undefined && (
                    <span>
                      After Sale: <strong>{alert.remaining_after_sale}</strong>
                    </span>
                  )}
                </div>
              )}
            </AlertDescription>
          </div>
          {onDismiss && (
            <Button variant="ghost" size="sm" onClick={onDismiss}>
              Dismiss
            </Button>
          )}
        </div>
      </Alert>

      {/* Alternative Products */}
      {alert.alternatives && alert.alternatives.length > 0 && (
        <div className="border rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <PackageIcon className="h-4 w-4" />
            <h4 className="font-medium">Alternative Products</h4>
          </div>
          <div className="grid gap-2">
            {alert.alternatives.map((alt) => (
              <div
                key={alt.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1">
                  <p className="font-medium">{alt.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-sm text-muted-foreground">
                      {formatCurrency(alt.price)}
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {alt.quantity} in stock
                    </Badge>
                  </div>
                </div>
                {onSelectAlternative && (
                  <Button size="sm" onClick={() => onSelectAlternative(alt)}>
                    Use This
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
