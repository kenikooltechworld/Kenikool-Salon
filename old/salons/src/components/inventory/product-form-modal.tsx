import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import {
  useCreateInventoryProduct,
  useUpdateInventoryProduct,
} from "@/lib/api/hooks/useInventory";
import { InventoryProduct } from "@/lib/api/types";

interface ProductFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  product?: InventoryProduct;
}

export function ProductFormModal({
  isOpen,
  onClose,
  onSuccess,
  product,
}: ProductFormModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    category: "hair_products",
    quantity: 0,
    unit: "pieces",
    cost_price: 0,
    reorder_level: 10,
    supplier: "",
  });

  const createProductMutation = useCreateInventoryProduct();
  const updateProductMutation = useUpdateInventoryProduct(product?.id || "");

  const isEditing = !!product;
  const isSubmitting =
    createProductMutation.isPending || updateProductMutation.isPending;

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || "",
        category: product.category || "hair_products",
        quantity: product.quantity || 0,
        unit: product.unit || "pieces",
        cost_price: product.cost_price || 0,
        reorder_level: product.reorder_level || 10,
        supplier: product.supplier || "",
      });
    } else {
      setFormData({
        name: "",
        category: "hair_products",
        quantity: 0,
        unit: "pieces",
        cost_price: 0,
        reorder_level: 10,
        supplier: "",
      });
    }
  }, [product, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (isEditing) {
        await updateProductMutation.mutateAsync(formData);
      } else {
        await createProductMutation.mutateAsync(formData);
      }
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Error saving product:", error);
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          {isEditing ? "Edit Product" : "Add Product"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Product Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Shampoo, Nail Polish"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Category *
            </label>
            <select
              value={formData.category}
              onChange={(e) =>
                setFormData({ ...formData, category: e.target.value })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
              required
            >
              <option value="hair_products">Hair Products</option>
              <option value="nail_products">Nail Products</option>
              <option value="tools">Tools</option>
              <option value="supplies">Supplies</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Quantity & Unit */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Quantity *
              </label>
              <Input
                type="number"
                value={formData.quantity}
                onChange={(e) =>
                  setFormData({ ...formData, quantity: Number(e.target.value) })
                }
                min="0"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Unit *
              </label>
              <select
                value={formData.unit}
                onChange={(e) =>
                  setFormData({ ...formData, unit: e.target.value })
                }
                className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
                required
              >
                <option value="pieces">Pieces</option>
                <option value="ml">ML</option>
                <option value="kg">KG</option>
                <option value="liters">Liters</option>
                <option value="boxes">Boxes</option>
              </select>
            </div>
          </div>

          {/* Unit Cost */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Unit Cost (₦)
            </label>
            <Input
              type="number"
              value={formData.cost_price}
              onChange={(e) =>
                setFormData({ ...formData, cost_price: Number(e.target.value) })
              }
              min="0"
              placeholder="0"
            />
          </div>

          {/* Reorder Level */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Reorder Level
            </label>
            <Input
              type="number"
              value={formData.reorder_level}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  reorder_level: Number(e.target.value),
                })
              }
              min="0"
              placeholder="10"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Alert when stock falls below this level
            </p>
          </div>

          {/* Supplier */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Supplier
            </label>
            <Input
              value={formData.supplier}
              onChange={(e) =>
                setFormData({ ...formData, supplier: e.target.value })
              }
              placeholder="Supplier name"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Spinner size="sm" />
                  {isEditing ? "Updating..." : "Creating..."}
                </>
              ) : isEditing ? (
                "Update Product"
              ) : (
                "Add Product"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
