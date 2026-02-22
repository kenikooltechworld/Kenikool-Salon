import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  SearchIcon,
  PackageIcon,
  AlertTriangleIcon,
  EditIcon,
  TrashIcon,
  FilterIcon,
  TrendingUpIcon,
} from "@/components/icons";
import { useInventory, useDeleteProduct } from "@/lib/api/hooks/useInventory";
import {
  ProductFormModal,
  AdjustmentModal,
  LowStockAlerts,
  InventoryForecasting,
} from "@/components/inventory";
import { InventoryProduct } from "@/lib/api/types";

export default function InventoryPage() {
  const [activeTab, setActiveTab] = useState("inventory");
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [isProductModalOpen, setIsProductModalOpen] = useState(false);
  const [isAdjustmentModalOpen, setIsAdjustmentModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<InventoryProduct>();
  const [adjustingProduct, setAdjustingProduct] = useState<InventoryProduct>();
  const [showLowStock, setShowLowStock] = useState(false);

  const {
    data: products = [],
    isLoading,
    error,
    refetch,
  } = useInventory({
    search: searchQuery || undefined,
    category: categoryFilter !== "all" ? categoryFilter : undefined,
    low_stock: showLowStock || undefined,
  });

  const deleteProductMutation = useDeleteProduct();

  const filteredProducts = products.filter((product: InventoryProduct) =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleOpenProductModal = (product?: InventoryProduct) => {
    setEditingProduct(product);
    setIsProductModalOpen(true);
  };

  const handleCloseProductModal = () => {
    setEditingProduct(undefined);
    setIsProductModalOpen(false);
  };

  const handleOpenAdjustmentModal = (product: InventoryProduct) => {
    setAdjustingProduct(product);
    setIsAdjustmentModalOpen(true);
  };

  const handleCloseAdjustmentModal = () => {
    setAdjustingProduct(undefined);
    setIsAdjustmentModalOpen(false);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this product?")) return;

    try {
      await deleteProductMutation.mutateAsync(id);
      refetch();
    } catch (error) {
      console.error("Error deleting product:", error);
    }
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading inventory</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Inventory</h1>
          <p className="text-muted-foreground">
            Manage your product stock and supplies
          </p>
        </div>
        <Button onClick={() => handleOpenProductModal()}>
          <PlusIcon size={20} />
          Add Product
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-border">
        <button
          onClick={() => setActiveTab("inventory")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "inventory"
              ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <div className="flex items-center gap-2">
            <PackageIcon size={18} />
            Inventory List
          </div>
        </button>
        <button
          onClick={() => setActiveTab("forecasting")}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === "forecasting"
              ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <div className="flex items-center gap-2">
            <TrendingUpIcon size={18} />
            Forecasting
          </div>
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "inventory" && (
        <>
          {/* Low Stock Alerts */}
          <LowStockAlerts />

          {/* Filters */}
          <Card className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <SearchIcon
                    size={20}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                  />
                  <Input
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Category Filter */}
              <div className="flex items-center gap-2">
                <FilterIcon size={20} className="text-muted-foreground" />
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
                >
                  <option value="all">All Categories</option>
                  <option value="hair_products">Hair Products</option>
                  <option value="nail_products">Nail Products</option>
                  <option value="tools">Tools</option>
                  <option value="supplies">Supplies</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Low Stock Toggle */}
              <Button
                variant={showLowStock ? "primary" : "outline"}
                onClick={() => setShowLowStock(!showLowStock)}
              >
                <AlertTriangleIcon size={16} />
                Low Stock Only
              </Button>
            </div>
          </Card>

          {/* Products Table */}
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : filteredProducts.length === 0 ? (
            <Card className="p-12">
              <div className="text-center">
                <PackageIcon
                  size={48}
                  className="mx-auto text-muted-foreground mb-4"
                />
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  No products found
                </h3>
                <p className="text-muted-foreground mb-4">
                  {searchQuery || showLowStock
                    ? "Try adjusting your filters"
                    : "Get started by adding your first product"}
                </p>
                {!searchQuery && !showLowStock && (
                  <Button onClick={() => handleOpenProductModal()}>
                    <PlusIcon size={20} />
                    Add Product
                  </Button>
                )}
              </div>
            </Card>
          ) : (
            <>
              {/* Desktop Table */}
              <Card className="hidden md:block overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-4 font-semibold text-foreground">
                          Product
                        </th>
                        <th className="text-left p-4 font-semibold text-foreground">
                          Category
                        </th>
                        <th className="text-left p-4 font-semibold text-foreground">
                          Stock
                        </th>
                        <th className="text-left p-4 font-semibold text-foreground">
                          Unit Cost
                        </th>
                        <th className="text-left p-4 font-semibold text-foreground">
                          Reorder Level
                        </th>
                        <th className="text-right p-4 font-semibold text-foreground">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredProducts.map((product: InventoryProduct) => {
                        const isLowStock =
                          product.quantity <= (product.reorder_level || 0);

                        return (
                          <tr
                            key={product.id}
                            className="border-t border-border hover:bg-muted/50 transition-colors"
                          >
                            <td className="p-4">
                              <div>
                                <p className="font-medium text-foreground">
                                  {product.name}
                                </p>
                                {product.supplier && (
                                  <p className="text-xs text-muted-foreground">
                                    Supplier: {product.supplier}
                                  </p>
                                )}
                              </div>
                            </td>
                            <td className="p-4">
                              <Badge variant="secondary">
                                {product.category}
                              </Badge>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                <span
                                  className={`font-medium ${
                                    isLowStock
                                      ? "text-[var(--error)]"
                                      : "text-foreground"
                                  }`}
                                >
                                  {product.quantity} {product.unit}
                                </span>
                                {isLowStock && (
                                  <Badge variant="error" size="sm">
                                    Low
                                  </Badge>
                                )}
                              </div>
                            </td>
                            <td className="p-4">
                              <span className="text-foreground">
                                {product.cost_price
                                  ? `₦${product.cost_price.toLocaleString()}`
                                  : "-"}
                              </span>
                            </td>
                            <td className="p-4">
                              <span className="text-muted-foreground">
                                {product.reorder_level || "-"}
                              </span>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center justify-end gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() =>
                                    handleOpenAdjustmentModal(product)
                                  }
                                >
                                  Adjust
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() =>
                                    handleOpenProductModal(product)
                                  }
                                >
                                  <EditIcon size={16} />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleDelete(product.id)}
                                >
                                  <TrashIcon size={16} />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Mobile Card View */}
              <div className="md:hidden space-y-4">
                {filteredProducts.map((product: InventoryProduct) => {
                  const isLowStock =
                    product.quantity <= (product.reorder_level || 0);

                  return (
                    <Card key={product.id} className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-foreground mb-1">
                            {product.name}
                          </h3>
                          <Badge variant="secondary" size="sm">
                            {product.category}
                          </Badge>
                        </div>
                        {isLowStock && (
                          <Badge variant="error" size="sm">
                            Low Stock
                          </Badge>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Stock
                          </p>
                          <p
                            className={`font-medium ${
                              isLowStock
                                ? "text-[var(--error)]"
                                : "text-foreground"
                            }`}
                          >
                            {product.quantity} {product.unit}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Unit Cost
                          </p>
                          <p className="font-medium text-foreground">
                            {product.cost_price
                              ? `₦${product.cost_price.toLocaleString()}`
                              : "-"}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          variant="primary"
                          size="sm"
                          className="flex-1"
                          onClick={() => handleOpenAdjustmentModal(product)}
                        >
                          Adjust Stock
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleOpenProductModal(product)}
                        >
                          <EditIcon size={16} />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(product.id)}
                        >
                          <TrashIcon size={16} />
                        </Button>
                      </div>
                    </Card>
                  );
                })}
              </div>
            </>
          )}
        </>
      )}

      {/* Forecasting Tab */}
      {activeTab === "forecasting" && <InventoryForecasting />}

      {/* Product Form Modal */}
      <ProductFormModal
        isOpen={isProductModalOpen}
        onClose={handleCloseProductModal}
        onSuccess={refetch}
        product={editingProduct}
      />

      {/* Adjustment Modal */}
      {adjustingProduct && (
        <AdjustmentModal
          isOpen={isAdjustmentModalOpen}
          onClose={handleCloseAdjustmentModal}
          onSuccess={refetch}
          product={adjustingProduct}
        />
      )}
    </div>
  );
}
