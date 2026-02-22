import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Trash2Icon, PlusIcon, MinusIcon } from "@/components/icons";
import { Textarea } from "@/components/ui/textarea";
import type { POSCartItem } from "@/lib/api/hooks/usePOS";
import { formatCurrency, CURRENCY_SYMBOL } from "@/lib/utils/currency";

interface POSCartProps {
  items: POSCartItem[];
  onUpdateItem: (index: number, item: POSCartItem) => void;
  onRemoveItem: (index: number) => void;
  onAddItem: (item: POSCartItem) => void;
  subtotal: number;
  discount: number;
  tax: number;
  tip: number;
  total: number;
  notes: string;
  loyaltyDiscount?: number;
  discountReason?: string;
  membershipDiscount?: number;
  membershipPlanName?: string;
  membershipDiscountPercentage?: number;
  onUpdateDiscount: (discount: number) => void;
  onUpdateTax: (tax: number) => void;
  onUpdateTip: (tip: number) => void;
  onUpdateNotes: (notes: string) => void;
}

export function POSCart({
  items,
  onUpdateItem,
  onRemoveItem,
  subtotal,
  discount,
  tax,
  tip,
  total,
  notes,
  loyaltyDiscount = 0,
  discountReason,
  membershipDiscount = 0,
  membershipPlanName,
  membershipDiscountPercentage = 0,
  onUpdateDiscount,
  onUpdateTax,
  onUpdateTip,
  onUpdateNotes,
}: POSCartProps) {
  const updateQuantity = (index: number, delta: number) => {
    const item = items[index];
    const newQuantity = Math.max(1, item.quantity + delta);
    onUpdateItem(index, { ...item, quantity: newQuantity });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cart</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Cart Items */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto overflow-x-hidden">
          {items.length === 0 ? (
            <p className="text-sm text-[var(--muted-foreground)] text-center py-8">
              No items in cart. Add services or products to get started.
            </p>
          ) : (
            items.map((item, index) => (
              <div key={index} className="p-3 border rounded-lg">
                <div className="flex items-start justify-between gap-2 mb-2 min-w-0">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{item.item_name}</p>
                    <p className="text-sm text-[var(--muted-foreground)] truncate">
                      {formatCurrency(item.price)} each
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 flex-shrink-0"
                    onClick={() => onRemoveItem(index)}
                  >
                    <Trash2Icon className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => updateQuantity(index, -1)}
                    >
                      <MinusIcon className="h-4 w-4" />
                    </Button>
                    <span className="w-8 text-center">{item.quantity}</span>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => updateQuantity(index, 1)}
                    >
                      <PlusIcon className="h-4 w-4" />
                    </Button>
                  </div>
                  <span className="font-medium text-right flex-shrink-0">
                    {formatCurrency(item.price * item.quantity)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Totals */}
        {items.length > 0 && (
          <div className="space-y-3 pt-4 border-t">
            <div className="flex justify-between text-sm">
              <span>Subtotal:</span>
              <span>{formatCurrency(subtotal)}</span>
            </div>

            {/* Discount Input */}
            <div className="flex justify-between items-center text-sm">
              <Label htmlFor="discount">Discount:</Label>
              <div className="flex items-center gap-2">
                <span>{CURRENCY_SYMBOL}</span>
                <Input
                  id="discount"
                  type="number"
                  min="0"
                  step="0.01"
                  value={discount}
                  onChange={(e) =>
                    onUpdateDiscount(parseFloat(e.target.value) || 0)
                  }
                  className="w-24 h-8"
                />
              </div>
            </div>
            {discountReason && discount > 0 && (
              <div className="text-xs text-[var(--muted-foreground)] pl-4">
                {discountReason}
              </div>
            )}

            {/* Loyalty Discount Display */}
            {loyaltyDiscount > 0 && (
              <div className="flex justify-between text-sm text-[var(--accent)]">
                <span>Loyalty Discount:</span>
                <span>-{formatCurrency(loyaltyDiscount)}</span>
              </div>
            )}

            {/* Membership Discount Display */}
            {membershipDiscount > 0 && (
              <div className="flex justify-between text-sm text-[var(--accent)]">
                <div className="flex flex-col">
                  <span>Member Discount ({membershipDiscountPercentage}%)</span>
                  {membershipPlanName && (
                    <span className="text-xs text-[var(--muted-foreground)]">
                      Plan: {membershipPlanName}
                    </span>
                  )}
                </div>
                <span>-{formatCurrency(membershipDiscount)}</span>
              </div>
            )}

            {/* Tax Input */}
            <div className="flex justify-between items-center text-sm">
              <Label htmlFor="tax">Tax:</Label>
              <div className="flex items-center gap-2">
                <span>{CURRENCY_SYMBOL}</span>
                <Input
                  id="tax"
                  type="number"
                  min="0"
                  step="0.01"
                  value={tax}
                  onChange={(e) => onUpdateTax(parseFloat(e.target.value) || 0)}
                  className="w-24 h-8"
                />
              </div>
            </div>

            {/* Tip Input with Presets */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <Label htmlFor="tip">Tip:</Label>
                <div className="flex items-center gap-2">
                  <span>{CURRENCY_SYMBOL}</span>
                  <Input
                    id="tip"
                    type="number"
                    min="0"
                    step="0.01"
                    value={tip}
                    onChange={(e) =>
                      onUpdateTip(parseFloat(e.target.value) || 0)
                    }
                    className="w-24 h-8"
                  />
                </div>
              </div>
              {/* Tip Presets */}
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="flex-1 h-7 text-xs"
                  onClick={() => onUpdateTip(subtotal * 0.15)}
                >
                  15%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="flex-1 h-7 text-xs"
                  onClick={() => onUpdateTip(subtotal * 0.18)}
                >
                  18%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="flex-1 h-7 text-xs"
                  onClick={() => onUpdateTip(subtotal * 0.2)}
                >
                  20%
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="flex-1 h-7 text-xs"
                  onClick={() => onUpdateTip(0)}
                >
                  None
                </Button>
              </div>
            </div>

            {/* Total */}
            <div className="flex justify-between text-lg font-bold pt-2 border-t">
              <span>Total:</span>
              <span>{formatCurrency(total)}</span>
            </div>

            {/* Notes */}
            <div className="space-y-2 pt-2">
              <Label htmlFor="notes">Transaction Notes (Optional)</Label>
              <Textarea
                id="notes"
                placeholder="Add notes about this transaction..."
                value={notes}
                onChange={(e) => onUpdateNotes(e.target.value)}
                className="min-h-[60px] resize-none"
                maxLength={500}
              />
              <p className="text-xs text-[var(--muted-foreground)] text-right">
                {notes.length}/500
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
