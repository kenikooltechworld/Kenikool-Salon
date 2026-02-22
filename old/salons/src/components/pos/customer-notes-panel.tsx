import { useGetCustomerNotes } from "@/lib/api/hooks/usePOS";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Loader2, AlertCircle, ShoppingBag, Star } from "@/components/icons";

interface CustomerNotesPanelProps {
  clientId: string | null;
}

export function CustomerNotesPanel({ clientId }: CustomerNotesPanelProps) {
  const { data: notes, isLoading } = useGetCustomerNotes(clientId);

  if (!clientId) {
    return null;
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-6">
          <Loader2 className="h-6 w-6 animate-spin" />
        </CardContent>
      </Card>
    );
  }

  if (!notes) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Customer Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <p className="text-2xl font-bold">{notes.visit_count}</p>
            <p className="text-xs text-muted-foreground">Visits</p>
          </div>
          <div>
            <p className="text-2xl font-bold">
              ${notes.total_spent.toFixed(0)}
            </p>
            <p className="text-xs text-muted-foreground">Total Spent</p>
          </div>
          <div>
            <p className="text-2xl font-bold">
              {notes.last_visit
                ? new Date(notes.last_visit).toLocaleDateString()
                : "N/A"}
            </p>
            <p className="text-xs text-muted-foreground">Last Visit</p>
          </div>
        </div>

        <Separator />

        {/* Allergies */}
        {notes.allergies && notes.allergies.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="h-4 w-4 text-destructive" />
              <p className="text-sm font-medium">Allergies</p>
            </div>
            <div className="flex flex-wrap gap-1">
              {notes.allergies.map((allergy, index) => (
                <Badge key={index} variant="destructive" className="text-xs">
                  {allergy}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Special Requirements */}
        {notes.special_requirements && (
          <div>
            <p className="text-sm font-medium mb-1">Special Requirements</p>
            <p className="text-sm text-muted-foreground">
              {notes.special_requirements}
            </p>
          </div>
        )}

        {/* Recommended Products */}
        {notes.recommended_products &&
          notes.recommended_products.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Star className="h-4 w-4 text-[var(--accent)]" />
                <p className="text-sm font-medium">Frequently Purchased</p>
              </div>
              <div className="space-y-1">
                {notes.recommended_products
                  .slice(0, 3)
                  .map((product, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="text-muted-foreground">
                        {product.name}
                      </span>
                      <Badge variant="secondary" className="text-xs">
                        {product.purchase_count}x
                      </Badge>
                    </div>
                  ))}
              </div>
            </div>
          )}

        {/* Recent Purchases */}
        {notes.purchase_history && notes.purchase_history.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <ShoppingBag className="h-4 w-4" />
              <p className="text-sm font-medium">Recent Purchases</p>
            </div>
            <div className="space-y-2">
              {notes.purchase_history.slice(0, 3).map((purchase, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-xs"
                >
                  <div>
                    <p className="font-medium">{purchase.transaction_number}</p>
                    <p className="text-muted-foreground">
                      {new Date(purchase.date).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatCurrency(purchase.total)}</p>
                    <p className="text-muted-foreground">
                      {purchase.items_count} items
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
