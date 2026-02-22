import { useParams, useNavigate } from "react-router-dom";
import { useInventory } from "@/hooks/useInventory";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  ArrowLeftIcon,
  Edit2Icon,
  Trash2Icon,
  PlusIcon,
  MinusIcon,
} from "@/components/icons";
import { useState } from "react";

export default function InventoryDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { inventory, deductInventory, updateInventory, isLoadingInventory } =
    useInventory();
  const [quantity, setQuantity] = useState(1);

  const item = inventory.find((i: any) => i.id === id);

  if (isLoadingInventory || !item) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner />
      </div>
    );
  }

  const handleDeduct = async () => {
    if (quantity > 0 && quantity <= item.quantity) {
      deductInventory({
        inventoryId: item.id,
        quantity,
        reason: "Manual deduction",
      });
      setQuantity(1);
    }
  };

  const handleRestock = async () => {
    if (quantity > 0) {
      updateInventory({
        id: item.id,
        quantity: item.quantity + quantity,
      });
      setQuantity(1);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/inventory")}
        >
          <ArrowLeftIcon size={20} />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{item.name}</h1>
          <p className="text-gray-600">SKU: {item.sku}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Item Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Current Quantity</p>
                <p className="text-2xl font-bold">{item.quantity}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Reorder Level</p>
                <p className="text-2xl font-bold">{item.reorder_level}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Unit Cost</p>
                <p className="text-2xl font-bold">
                  ${item.unit_cost.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-2xl font-bold">
                  ${(item.quantity * item.unit_cost).toFixed(2)}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Status</p>
                {item.quantity === 0 ? (
                  <Badge variant="destructive">Out of Stock</Badge>
                ) : item.quantity <= item.reorder_level ? (
                  <Badge variant="outline" className="text-yellow-700">
                    Low Stock
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-green-700">
                    In Stock
                  </Badge>
                )}
              </div>
            </div>
          </Card>

          {/* Inventory Adjustment */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Adjust Inventory</h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Quantity</label>
                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) =>
                    setQuantity(Math.max(1, parseInt(e.target.value) || 1))
                  }
                  className="w-full px-3 py-2 border rounded-md mt-1"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleRestock}
                  className="flex-1 gap-2"
                  variant="outline"
                >
                  <PlusIcon size={18} />
                  Add Stock
                </Button>
                <Button
                  onClick={handleDeduct}
                  className="flex-1 gap-2"
                  variant="outline"
                  disabled={quantity > item.quantity}
                >
                  <MinusIcon size={18} />
                  Deduct
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar Actions */}
        <div className="space-y-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Actions</h3>
            <div className="space-y-2">
              <Button className="w-full gap-2" variant="outline">
                <Edit2Icon size={18} />
                Edit Item
              </Button>
              <Button className="w-full gap-2" variant="destructive">
                <Trash2Icon size={18} />
                Delete Item
              </Button>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold mb-3">Quick Info</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated</span>
                <span className="font-medium">
                  {new Date(item.updated_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Created</span>
                <span className="font-medium">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
