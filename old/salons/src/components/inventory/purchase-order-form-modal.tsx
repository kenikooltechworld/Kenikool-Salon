import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";

interface LineItem {
  product_id: string;
  product_name: string;
  quantity_ordered: number;
  unit_price: number;
  total_price: number;
}

interface PurchaseOrderFormModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function PurchaseOrderFormModal({
  isOpen,
  onClose,
}: PurchaseOrderFormModalProps) {
  const { toast } = useToast();
  const [supplierId, setSupplierId] = useState("");
  const [supplierName, setSupplierName] = useState("");
  const [lineItems, setLineItems] = useState<LineItem[]>([]);
  const [currentItem, setCurrentItem] = useState<Partial<LineItem>>({
    product_name: "",
    quantity_ordered: 1,
    unit_price: 0,
  });
  const [taxAmount, setTaxAmount] = useState(0);
  const [shippingCost, setShippingCost] = useState(0);
  const [notes, setNotes] = useState("");
  const [expectedDeliveryDate, setExpectedDeliveryDate] = useState("");

  const { data: suppliers } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => {
      const res = await apiClient.get("/api/inventory/suppliers");
      return res.data.suppliers || [];
    },
    enabled: isOpen,
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const subtotal = lineItems.reduce((sum, item) => sum + item.total_price, 0);
      const totalAmount = subtotal + taxAmount + shippingCost;

      const res = await apiClient.post("/api/inventory/purchase-orders", {
        supplier_id: supplierId,
        supplier_name: supplierName,
        line_items: lineItems,
        tax_amount: taxAmount,
        shipping_cost: shippingCost,
        total_amount: totalAmount,
        notes: notes || undefined,
        expected_delivery_date: expectedDeliveryDate || undefined,
      });
      return res.data;
    },
    onSuccess: () => {
      toast("Purchase order created successfully", "success");
      handleClose();
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to create purchase order",
        "error"
      );
    },
  });

  const handleAddItem = () => {
    if (!currentItem.product_name || !currentItem.quantity_ordered || !currentItem.unit_price) {
      toast("Please fill in all item fields", "error");
      return;
    }

    const newItem: LineItem = {
      product_id: `product_${Date.now()}`,
      product_name: currentItem.product_name || "",
      quantity_ordered: currentItem.quantity_ordered || 1,
      unit_price: currentItem.unit_price || 0,
      total_price: (currentItem.quantity_ordered || 1) * (currentItem.unit_price || 0),
    };

    setLineItems([...lineItems, newItem]);
    setCurrentItem({ product_name: "", quantity_ordered: 1, unit_price: 0 });
  };

  const handleRemoveItem = (index: number) => {
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!supplierId || !supplierName) {
      toast("Please select a supplier", "error");
      return;
    }

    if (lineItems.length === 0) {
      toast("Please add at least one item", "error");
      return;
    }

    await createMutation.mutateAsync();
  };

  const handleClose = () => {
    setSupplierId("");
    setSupplierName("");
    setLineItems([]);
    setCurrentItem({ product_name: "", quantity_ordered: 1, unit_price: 0 });
    setTaxAmount(0);
    setShippingCost(0);
    setNotes("");
    setExpectedDeliveryDate("");
    onClose();
  };

  const subtotal = lineItems.reduce((sum, item) => sum + item.total_price, 0);
  const totalAmount = subtotal + taxAmount + shippingCost;

  return (
    <Modal open={isOpen} onClose={handleClose} size="lg">
      <ModalHeader>
        <ModalTitle>Create Purchase Order</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-6 max-h-96 overflow-y-auto">
        {/* Supplier Selection */}
        <div>
          <Label required>Supplier</Label>
          <select
            value={supplierId}
            onChange={(e) => {
              const supplier = suppliers?.find((s: any) => s._id === e.target.value);
              setSupplierId(e.target.value);
              setSupplierName(supplier?.name || "");
            }}
            className="w-full mt-1 p-2 border border-[var(--border)] rounded"
          >
            <option value="">Select a supplier</option>
            {suppliers?.map((supplier: any) => (
              <option key={supplier._id} value={supplier._id}>
                {supplier.name}
              </option>
            ))}
          </select>
        </div>

        {/* Line Items */}
        <div>
          <Label>Line Items</Label>
          <div className="space-y-3 mt-2">
            {lineItems.map((item, index) => (
              <Card key={index}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-medium text-[var(--foreground)]">
                        {item.product_name}
                      </p>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        {item.quantity_ordered} × ₦{item.unit_price.toLocaleString()} = ₦
                        {item.total_price.toLocaleString()}
                      </p>
                    </div>
                    <Button
                      onClick={() => handleRemoveItem(index)}
                      variant="destructive"
                      size="sm"
                    >
                      Remove
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Add Item Form */}
          <div className="space-y-2 mt-4 p-3 bg-[var(--muted)] rounded">
            <div className="grid grid-cols-2 gap-2">
              <Input
                placeholder="Product name"
                value={currentItem.product_name || ""}
                onChange={(e) =>
                  setCurrentItem({ ...currentItem, product_name: e.target.value })
                }
              />
              <Input
                type="number"
                placeholder="Quantity"
                value={currentItem.quantity_ordered || 1}
                onChange={(e) =>
                  setCurrentItem({
                    ...currentItem,
                    quantity_ordered: parseInt(e.target.value) || 1,
                  })
                }
              />
            </div>
            <Input
              type="number"
              placeholder="Unit price"
              value={currentItem.unit_price || 0}
              onChange={(e) =>
                setCurrentItem({
                  ...currentItem,
                  unit_price: parseFloat(e.target.value) || 0,
                })
              }
            />
            <Button onClick={handleAddItem} variant="secondary" className="w-full">
              Add Item
            </Button>
          </div>
        </div>

        {/* Costs */}
        <div className="grid grid-cols-3 gap-2">
          <div>
            <Label>Tax</Label>
            <Input
              type="number"
              value={taxAmount}
              onChange={(e) => setTaxAmount(parseFloat(e.target.value) || 0)}
              className="mt-1"
            />
          </div>
          <div>
            <Label>Shipping</Label>
            <Input
              type="number"
              value={shippingCost}
              onChange={(e) => setShippingCost(parseFloat(e.target.value) || 0)}
              className="mt-1"
            />
          </div>
          <div>
            <Label>Total</Label>
            <Input
              type="text"
              value={`₦${totalAmount.toLocaleString()}`}
              disabled
              className="mt-1"
            />
          </div>
        </div>

        {/* Other Fields */}
        <div>
          <Label>Expected Delivery Date</Label>
          <Input
            type="date"
            value={expectedDeliveryDate}
            onChange={(e) => setExpectedDeliveryDate(e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <Label>Notes</Label>
          <Input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Additional notes"
            className="mt-1"
          />
        </div>
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={handleClose}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={createMutation.isPending}
        >
          {createMutation.isPending ? "Creating..." : "Create PO"}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
