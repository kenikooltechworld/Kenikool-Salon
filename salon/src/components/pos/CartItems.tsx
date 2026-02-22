import { usePOSStore } from "@/stores/pos";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";

export default function CartItems() {
  const { cartItems, removeFromCart, updateCartItem } = usePOSStore();
  const { showToast } = useToast();

  const handleQuantityChange = (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) {
      showToast({
        title: "Invalid Quantity",
        description: "Quantity must be at least 1",
        variant: "error",
      });
      return;
    }
    updateCartItem(itemId, newQuantity);
    showToast({
      title: "Quantity Updated",
      description: `Item quantity changed to ${newQuantity}`,
      variant: "default",
    });
  };

  const handleRemoveItem = (itemId: string, itemName: string) => {
    removeFromCart(itemId);
    showToast({
      title: "Item Removed",
      description: `${itemName} removed from cart`,
      variant: "default",
    });
  };

  return (
    <div className="space-y-2 md:space-y-3">
      {cartItems.map((item) => (
        <div
          key={item.itemId}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-3 p-2 md:p-3 bg-muted rounded-lg hover:bg-muted/80 transition"
        >
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm text-foreground truncate">
              {item.itemName}
            </p>
            <p className="text-xs text-muted-foreground">
              ₦
              {item.unitPrice.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </p>
          </div>

          <div className="flex items-center gap-1 sm:gap-2 flex-wrap sm:flex-nowrap">
            <Input
              type="number"
              min="1"
              value={item.quantity}
              onChange={(e) =>
                handleQuantityChange(item.itemId, parseInt(e.target.value) || 1)
              }
              className="w-12 h-8 text-center text-sm"
            />
            <span className="text-sm font-medium w-20 sm:w-16 text-right text-foreground">
              ₦
              {item.lineTotal.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleRemoveItem(item.itemId, item.itemName)}
              className="text-destructive hover:text-destructive hover:bg-destructive/10 flex-shrink-0"
            >
              ✕
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
