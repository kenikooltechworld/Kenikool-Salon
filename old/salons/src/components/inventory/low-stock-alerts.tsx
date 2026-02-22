import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon, PackageIcon } from "@/components/icons";
import { useInventory } from "@/lib/api/hooks/useInventory";
import { InventoryProduct } from "@/lib/api/types";

export function LowStockAlerts() {
  const { data: products = [], isLoading } = useInventory({ low_stock: true });

  const lowStockProducts = products.filter(
    (product: InventoryProduct) =>
      product.quantity <= (product.reorder_level || 0)
  );

  if (isLoading) {
    return (
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <Spinner size="sm" />
          <span className="text-sm text-muted-foreground">
            Checking stock levels...
          </span>
        </div>
      </Card>
    );
  }

  if (lowStockProducts.length === 0) {
    return null;
  }

  return (
    <Card className="p-4 border-[var(--warning)]">
      <div className="flex items-start gap-3">
        <AlertTriangleIcon size={20} className="text-[var(--warning)] mt-0.5" />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-foreground">Low Stock Alert</h3>
            <Badge variant="warning">{lowStockProducts.length}</Badge>
          </div>
          <p className="text-sm text-muted-foreground mb-3">
            The following products are running low and need to be reordered:
          </p>
          <div className="space-y-2">
            {lowStockProducts.slice(0, 5).map((product: InventoryProduct) => (
              <div
                key={product.id}
                className="flex items-center justify-between p-2 bg-[var(--muted)]/50 rounded-lg"
              >
                <div className="flex items-center gap-2">
                  <PackageIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm font-medium text-foreground">
                    {product.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-[var(--error)]">
                    {product.quantity} {product.unit}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    / {product.reorder_level} min
                  </span>
                </div>
              </div>
            ))}
            {lowStockProducts.length > 5 && (
              <p className="text-xs text-muted-foreground text-center pt-2">
                +{lowStockProducts.length - 5} more products
              </p>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
