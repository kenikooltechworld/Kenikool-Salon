import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PurchaseOrderFormModal } from "./purchase-order-form-modal";

interface PurchaseOrder {
  _id: string;
  po_number: string;
  supplier_name: string;
  status: string;
  total_amount: number;
  expected_delivery_date?: string;
  created_at: string;
}

export function PurchaseOrderList() {
  const [showForm, setShowForm] = useState(false);
  const [statusFilter, setStatusFilter] = useState("");

  const { data: response, isLoading, refetch } = useQuery({
    queryKey: ["purchase-orders", statusFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (statusFilter) params.append("status", statusFilter);
      const res = await apiClient.get(`/api/inventory/purchase-orders?${params}`);
      return res.data;
    },
  });

  const pos = response?.purchase_orders || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "draft":
        return "secondary";
      case "sent":
        return "accent";
      case "received":
        return "secondary";
      case "partial":
        return "accent";
      case "cancelled":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const handleClose = () => {
    setShowForm(false);
    refetch();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-[var(--foreground)]">Purchase Orders</h2>
        <Button onClick={() => setShowForm(true)}>Create PO</Button>
      </div>

      {/* Status Filter */}
      <div className="flex gap-2">
        <Button
          variant={statusFilter === "" ? "primary" : "outline"}
          onClick={() => setStatusFilter("")}
          size="sm"
        >
          All
        </Button>
        {["draft", "sent", "received", "partial", "cancelled"].map((status) => (
          <Button
            key={status}
            variant={statusFilter === status ? "primary" : "outline"}
            onClick={() => setStatusFilter(status)}
            size="sm"
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-[var(--muted-foreground)]">Loading purchase orders...</p>
      ) : pos.length > 0 ? (
        <div className="space-y-3">
          {pos.map((po: PurchaseOrder) => (
            <Card key={po._id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-[var(--foreground)]">
                        {po.po_number}
                      </h3>
                      <Badge variant={getStatusColor(po.status)}>
                        {po.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      {po.supplier_name}
                    </p>
                    {po.expected_delivery_date && (
                      <p className="text-xs text-[var(--muted-foreground)] mt-1">
                        Expected: {new Date(po.expected_delivery_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-[var(--foreground)]">
                      ₦{po.total_amount.toLocaleString()}
                    </p>
                    <p className="text-xs text-[var(--muted-foreground)]">
                      {new Date(po.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-[var(--muted-foreground)]">No purchase orders yet</p>
            <Button onClick={() => setShowForm(true)} className="mt-4">
              Create Your First PO
            </Button>
          </CardContent>
        </Card>
      )}

      <PurchaseOrderFormModal isOpen={showForm} onClose={handleClose} />
    </div>
  );
}
