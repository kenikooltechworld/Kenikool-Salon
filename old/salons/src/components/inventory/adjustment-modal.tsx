import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { useAdjustInventory } from "@/lib/api/hooks/useInventory";
import { InventoryProduct } from "@/lib/api/types";

interface AdjustmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  product: InventoryProduct;
}

export function AdjustmentModal({
  isOpen,
  onClose,
  onSuccess,
  product,
}: AdjustmentModalProps) {
  const [adjustmentType, setAdjustmentType] = useState<
    "add" | "remove" | "set"
  >("add");
  const [quantity, setQuantity] = useState(0);
  const [reason, setReason] = useState("");

  const adjustInventoryMutation = useAdjustInventory();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await adjustInventoryMutation.mutateAsync({
        id: product.id,
        data: {
          adjustment_type: adjustmentType,
          quantity,
          reason,
        },
      });
      onSuccess();
      onClose();
      // Reset form
      setAdjustmentType("add");
      setQuantity(0);
      setReason("");
    } catch (error) {
      console.error("Error adjusting inventory:", error);
    }
  };

  const getNewQuantity = () => {
    switch (adjustmentType) {
      case "add":
        return product.quantity + quantity;
      case "remove":
        return Math.max(0, product.quantity - quantity);
      case "set":
        return quantity;
      default:
        return product.quantity;
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Adjust Inventory
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Current Stock */}
          <div className="p-4 bg-[var(--muted)]/50 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">Current Stock</p>
            <p className="text-2xl font-bold text-foreground">
              {product.quantity} {product.unit}
            </p>
            <p className="text-sm font-medium text-foreground mt-2">
              {product.name}
            </p>
          </div>

          {/* Adjustment Type */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Adjustment Type *
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setAdjustmentType("add")}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  adjustmentType === "add"
                    ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                    : "border-[var(--border)] text-foreground hover:border-[var(--primary)]/50"
                }`}
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => setAdjustmentType("remove")}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  adjustmentType === "remove"
                    ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                    : "border-[var(--border)] text-foreground hover:border-[var(--primary)]/50"
                }`}
              >
                Remove
              </button>
              <button
                type="button"
                onClick={() => setAdjustmentType("set")}
                className={`px-4 py-2 rounded-lg border transition-colors ${
                  adjustmentType === "set"
                    ? "border-[var(--primary)] bg-[var(--primary)]/10 text-[var(--primary)]"
                    : "border-[var(--border)] text-foreground hover:border-[var(--primary)]/50"
                }`}
              >
                Set
              </button>
            </div>
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Quantity *
            </label>
            <Input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              min="0"
              placeholder={adjustmentType === "set" ? "New quantity" : "Amount"}
              required
            />
          </div>

          {/* New Quantity Preview */}
          <div className="p-3 bg-[var(--info)]/10 border border-[var(--info)]/20 rounded-lg">
            <p className="text-sm text-muted-foreground mb-1">
              New Stock Level
            </p>
            <p className="text-lg font-semibold text-foreground">
              {getNewQuantity()} {product.unit}
            </p>
          </div>

          {/* Reason */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Reason *
            </label>
            <Input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g., Restocked, Used for service, Damaged"
              required
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={adjustInventoryMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={adjustInventoryMutation.isPending}
            >
              {adjustInventoryMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Adjusting...
                </>
              ) : (
                "Adjust Stock"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
