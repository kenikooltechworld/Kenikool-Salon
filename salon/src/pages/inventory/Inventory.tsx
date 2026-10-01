import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useInventory } from "@/hooks/useInventory";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  AlertTriangleIcon,
  PlusIcon,
  Edit2Icon,
  Trash2Icon,
  TrendingDownIcon,
} from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { usePageRefresh } from "@/contexts/PageRefreshContext";
import { InventorySkeleton } from "@/components/skeletons/InventorySkeleton";

export default function Inventory() {
  const navigate = useNavigate();
  const {
    inventory,
    inventoryTotal,
    isLoadingInventory,
    lowStockItems,
    isLoadingLowStock,
    alerts,
    isLoadingAlerts,
    skip,
    setSkip,
    limit,
    setLimit,
    refetch,
    createInventory,
    updateInventory,
    deleteInventory,
    isCreatingInventory,
    isUpdatingInventory,
    isDeletingInventory,
  } = useInventory();
  const [searchTerm, setSearchTerm] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const { showToast } = useToast();
  const { setRefreshHandler } = usePageRefresh();

  const [formData, setFormData] = useState({
    name: "",
    sku: "",
    quantity: 0,
    reorder_level: 0,
    unit_cost: 0,
    unit: "unit",
    category: "",
    supplier_id: "",
    expiry_date: "",
    notes: "",
    is_active: true,
  });

  const filteredInventory = inventory.filter(
    (item: any) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const totalPages = Math.ceil(inventoryTotal / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  useEffect(() => {
    setRefreshHandler(() => refetch);
  }, [refetch, setRefreshHandler]);

  const openCreateModal = () => {
    setEditingItem(null);
    setFormData({
      name: "",
      sku: "",
      quantity: 0,
      reorder_level: 0,
      unit_cost: 0,
      unit: "unit",
      category: "",
      supplier_id: "",
      expiry_date: "",
      notes: "",
      is_active: true,
    });
    setShowCreateModal(true);
  };

  const openEditModal = (item: any) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      sku: item.sku,
      quantity: item.quantity,
      reorder_level: item.reorder_level,
      unit_cost: item.unit_cost,
      unit: item.unit || "unit",
      category: item.category || "",
      supplier_id: item.supplier_id || "",
      expiry_date: item.expiry_date || "",
      notes: item.notes || "",
      is_active: item.is_active ?? true,
    });
    setShowCreateModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingItem) {
        updateInventory(
          {
            id: editingItem.id,
            ...formData,
            quantity: editingItem.quantity,
            unit_cost: Number(formData.unit_cost),
            reorder_level: Number(formData.reorder_level),
          },
          {
            onSuccess: () => {
              showToast({ title: "Inventory updated successfully", variant: "success" });
              setShowCreateModal(false);
            },
            onError: () => {
              showToast({ title: "Failed to update inventory", variant: "error" });
            },
          }
        );
      } else {
        createInventory(
          {
            ...formData,
            quantity: Number(formData.quantity),
            unit_cost: Number(formData.unit_cost),
            reorder_level: Number(formData.reorder_level),
          },
          {
            onSuccess: () => {
              showToast({ title: "Inventory created successfully", variant: "success" });
              setShowCreateModal(false);
              setFormData({
                name: "",
                sku: "",
                quantity: 0,
                reorder_level: 0,
                unit_cost: 0,
                unit: "unit",
                category: "",
                supplier_id: "",
                expiry_date: "",
                notes: "",
                is_active: true,
              });
            },
            onError: () => {
              showToast({ title: "Failed to create inventory", variant: "error" });
            },
          }
        );
      }
    } catch {
      showToast({ title: "An error occurred", variant: "error" });
    }
  };

  const handleDelete = (id: string) => {
    setDeleteConfirmId(id);
  };

  const confirmDelete = () => {
    if (deleteConfirmId) {
      deleteInventory(deleteConfirmId, {
        onSuccess: () => {
          showToast({ title: "Inventory deleted successfully", variant: "success" });
          setDeleteConfirmId(null);
        },
        onError: () => {
          showToast({ title: "Failed to delete inventory", variant: "error" });
        },
      });
    }
  };

  if (isLoadingInventory) {
    return <InventorySkeleton />;
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Inventory Management</h1>
          <p className="text-gray-600 mt-1">
            Track and manage your products and supplies
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={openCreateModal} className="gap-2">
            <PlusIcon size={20} />
            Add Item
          </Button>
        </div>
      </div>

      {/* Alerts Summary */}
      {!isLoadingAlerts && alerts.length > 0 && (
        <Card className="bg-red-50 border-red-200 p-4">
          <div className="flex items-start gap-3">
            <AlertTriangleIcon className="text-red-600 mt-1" size={20} />
            <div>
              <h3 className="font-semibold text-red-900">Stock Alerts</h3>
              <p className="text-red-700 text-sm">
                {alerts.length} item{alerts.length !== 1 ? "s" : ""} need
                attention
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Low Stock Items */}
      {!isLoadingLowStock && lowStockItems.length > 0 && (
        <Card className="p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <TrendingDownIcon size={18} />
            Low Stock Items
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {lowStockItems.slice(0, 3).map((item: any) => (
              <div
                key={item.id}
                className="bg-yellow-50 border border-yellow-200 rounded p-3"
              >
                <p className="font-medium text-sm">{item.name}</p>
                <p className="text-xs text-gray-600">SKU: {item.sku}</p>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-sm font-semibold">
                    {item.quantity} left
                  </span>
                  <Badge
                    variant="outline"
                    className="text-yellow-700 border-yellow-300"
                  >
                    Reorder: {item.reorder_level}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Search and Filter */}
      <div className="flex gap-4">
        <Input
          placeholder="Search by name or SKU..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1"
        />
      </div>

      {/* Inventory Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Reorder Level
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Unit Cost
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map((item: any) => (
                <tr key={item.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">{item.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {item.sku}
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold">
                    {item.quantity}
                  </td>
                  <td className="px-6 py-4 text-sm">{item.reorder_level}</td>
                  <td className="px-6 py-4 text-sm">
                    ${item.unit_cost.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {item.quantity === 0 ? (
                      <Badge variant="destructive">Out of Stock</Badge>
                    ) : item.quantity <= item.reorder_level ? (
                      <Badge
                        variant="outline"
                        className="text-yellow-700 border-yellow-300"
                      >
                        Low Stock
                      </Badge>
                    ) : (
                      <Badge
                        variant="outline"
                        className="text-green-700 border-green-300"
                      >
                        In Stock
                      </Badge>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditModal(item)}
                      >
                        <Edit2Icon size={16} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600"
                        onClick={() => handleDelete(item.id)}
                      >
                        <Trash2Icon size={16} />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex justify-between items-center px-6 py-4 border-t bg-gray-50">
          <p className="text-sm text-gray-600">
            Page {currentPage} of {totalPages} ({inventoryTotal} total items)
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSkip(skip + limit)}
              disabled={currentPage >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>

      {/* Create/Edit Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingItem ? "Edit Inventory Item" : "Add Inventory Item"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="sku">SKU</Label>
              <Input
                id="sku"
                value={formData.sku}
                onChange={(e) =>
                  setFormData({ ...formData, sku: e.target.value })
                }
                required
              />
            </div>
            {!editingItem && (
              <div>
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="0"
                  value={formData.quantity}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      quantity: parseInt(e.target.value) || 0,
                    })
                  }
                  required
                />
              </div>
            )}
            <div>
              <Label htmlFor="reorder_level">Reorder Level</Label>
              <Input
                id="reorder_level"
                type="number"
                min="0"
                value={formData.reorder_level}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    reorder_level: parseInt(e.target.value) || 0,
                  })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="unit_cost">Unit Cost ($)</Label>
              <Input
                id="unit_cost"
                type="number"
                min="0"
                step="0.01"
                value={formData.unit_cost}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    unit_cost: parseFloat(e.target.value) || 0,
                  })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="unit">Unit</Label>
              <Input
                id="unit"
                value={formData.unit}
                onChange={(e) =>
                  setFormData({ ...formData, unit: e.target.value })
                }
                placeholder="e.g. pcs, ml, g, oz"
              />
            </div>
            <div>
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                value={formData.category}
                onChange={(e) =>
                  setFormData({ ...formData, category: e.target.value })
                }
                placeholder="e.g. Hair Care, Skin Care"
              />
            </div>
            <div>
              <Label htmlFor="supplier_id">Supplier ID (optional)</Label>
              <Input
                id="supplier_id"
                value={formData.supplier_id}
                onChange={(e) =>
                  setFormData({ ...formData, supplier_id: e.target.value })
                }
              />
            </div>
            <div>
              <Label htmlFor="expiry_date">Expiry Date (optional)</Label>
              <Input
                id="expiry_date"
                type="date"
                value={formData.expiry_date}
                onChange={(e) =>
                  setFormData({ ...formData, expiry_date: e.target.value })
                }
              />
            </div>
            <div>
              <Label htmlFor="notes">Notes</Label>
              <Input
                id="notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isCreatingInventory || isUpdatingInventory}
              >
                {editingItem ? "Update" : "Create"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={!!deleteConfirmId} onOpenChange={(open) => !open && setDeleteConfirmId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Inventory Item</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-gray-600">
            Are you sure you want to delete this inventory item? This action
            cannot be undone.
          </p>
          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setDeleteConfirmId(null)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
              disabled={isDeletingInventory}
            >
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
