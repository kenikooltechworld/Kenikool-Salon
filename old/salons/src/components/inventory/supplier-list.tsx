import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SupplierFormModal } from "./supplier-form-modal";

interface Supplier {
  _id: string;
  name: string;
  email?: string;
  phone?: string;
  city?: string;
  country?: string;
  is_active: boolean;
  total_orders: number;
  on_time_delivery_rate: number;
  total_spent: number;
}

export function SupplierList() {
  const [showForm, setShowForm] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);

  const { data: response, isLoading, refetch } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => {
      const res = await apiClient.get("/api/inventory/suppliers");
      return res.data;
    },
  });

  const suppliers = response?.suppliers || [];

  const handleEdit = (supplier: Supplier) => {
    setSelectedSupplier(supplier);
    setShowForm(true);
  };

  const handleClose = () => {
    setShowForm(false);
    setSelectedSupplier(null);
    refetch();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-[var(--foreground)]">Suppliers</h2>
        <Button
          onClick={() => {
            setSelectedSupplier(null);
            setShowForm(true);
          }}
        >
          Add Supplier
        </Button>
      </div>

      {isLoading ? (
        <p className="text-[var(--muted-foreground)]">Loading suppliers...</p>
      ) : suppliers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {suppliers.map((supplier: Supplier) => (
            <Card key={supplier._id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{supplier.name}</CardTitle>
                    <p className="text-sm text-[var(--muted-foreground)] mt-1">
                      {supplier.city && supplier.country
                        ? `${supplier.city}, ${supplier.country}`
                        : "Location not specified"}
                    </p>
                  </div>
                  <Badge variant={supplier.is_active ? "accent" : "secondary"}>
                    {supplier.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {supplier.email && (
                  <p className="text-sm">
                    <span className="text-[var(--muted-foreground)]">Email:</span>{" "}
                    {supplier.email}
                  </p>
                )}
                {supplier.phone && (
                  <p className="text-sm">
                    <span className="text-[var(--muted-foreground)]">Phone:</span>{" "}
                    {supplier.phone}
                  </p>
                )}

                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[var(--border)]">
                  <div>
                    <p className="text-xs text-[var(--muted-foreground)]">Orders</p>
                    <p className="text-lg font-bold text-[var(--foreground)]">
                      {supplier.total_orders}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[var(--muted-foreground)]">On-Time Rate</p>
                    <p className="text-lg font-bold text-[var(--foreground)]">
                      {supplier.on_time_delivery_rate.toFixed(1)}%
                    </p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-xs text-[var(--muted-foreground)]">Total Spent</p>
                    <p className="text-lg font-bold text-[var(--foreground)]">
                      ₦{supplier.total_spent.toLocaleString()}
                    </p>
                  </div>
                </div>

                <Button
                  onClick={() => handleEdit(supplier)}
                  variant="outline"
                  className="w-full"
                >
                  Edit
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-[var(--muted-foreground)]">No suppliers yet</p>
            <Button
              onClick={() => {
                setSelectedSupplier(null);
                setShowForm(true);
              }}
              className="mt-4"
            >
              Add Your First Supplier
            </Button>
          </CardContent>
        </Card>
      )}

      <SupplierFormModal
        isOpen={showForm}
        onClose={handleClose}
        supplier={selectedSupplier}
      />
    </div>
  );
}
