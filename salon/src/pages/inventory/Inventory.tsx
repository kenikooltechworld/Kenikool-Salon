import { useState } from "react";
import { useInventory } from "@/hooks/useInventory";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  AlertTriangleIcon,
  PlusIcon,
  Edit2Icon,
  Trash2Icon,
  TrendingDownIcon,
} from "@/components/icons";

export default function Inventory() {
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
  } = useInventory();

  const [searchTerm, setSearchTerm] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);

  const filteredInventory = inventory.filter(
    (item) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const totalPages = Math.ceil(inventoryTotal / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  if (isLoadingInventory) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner />
      </div>
    );
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
        <Button onClick={() => setShowCreateModal(true)} className="gap-2">
          <PlusIcon size={20} />
          Add Item
        </Button>
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
            {lowStockItems.slice(0, 3).map((item) => (
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
              {filteredInventory.map((item) => (
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
                      <Button variant="ghost" size="sm">
                        <Edit2Icon size={16} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600"
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
    </div>
  );
}
