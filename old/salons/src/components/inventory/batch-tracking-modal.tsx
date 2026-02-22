import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
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
import { Badge } from "@/components/ui/badge";

interface Batch {
  _id: string;
  batch_id: string;
  quantity: number;
  quantity_used: number;
  expiration_date?: string;
  status: string;
  created_at: string;
}

interface BatchTrackingModalProps {
  isOpen: boolean;
  onClose: () => void;
  productId: string;
  productName: string;
}

export function BatchTrackingModal({
  isOpen,
  onClose,
  productId,
  productName,
}: BatchTrackingModalProps) {
  const { toast } = useToast();
  const [showAddBatch, setShowAddBatch] = useState(false);
  const [newBatchId, setNewBatchId] = useState("");
  const [newBatchQuantity, setNewBatchQuantity] = useState(0);
  const [newBatchExpiry, setNewBatchExpiry] = useState("");

  const { data: batches, refetch } = useQuery({
    queryKey: ["batches", productId],
    queryFn: async () => {
      const res = await apiClient.get(
        `/api/inventory/products/${productId}/batches`
      );
      return res.data.batches || [];
    },
    enabled: isOpen,
  });

  const addBatchMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post(
        `/api/inventory/products/${productId}/batches`,
        {
          batch_id: newBatchId,
          quantity: newBatchQuantity,
          expiration_date: newBatchExpiry || undefined,
        }
      );
      return res.data;
    },
    onSuccess: () => {
      toast("Batch added successfully", "success");
      setNewBatchId("");
      setNewBatchQuantity(0);
      setNewBatchExpiry("");
      setShowAddBatch(false);
      refetch();
    },
    onError: (error: any) => {
      toast(error.response?.data?.detail || "Failed to add batch", "error");
    },
  });

  const markExpiredMutation = useMutation({
    mutationFn: async (batchId: string) => {
      const res = await apiClient.patch(
        `/api/inventory/batches/${batchId}/mark-expired`
      );
      return res.data;
    },
    onSuccess: () => {
      toast("Batch marked as expired", "success");
      refetch();
    },
    onError: (error: any) => {
      toast(error.response?.data?.detail || "Failed to mark batch", "error");
    },
  });

  const getStatusColor = (status: string, expiryDate?: string) => {
    if (status === "expired") return "destructive";
    if (expiryDate) {
      const daysUntilExpiry = Math.ceil(
        (new Date(expiryDate).getTime() - new Date().getTime()) /
          (1000 * 60 * 60 * 24)
      );
      if (daysUntilExpiry <= 7) return "destructive";
      if (daysUntilExpiry <= 30) return "accent";
    }
    return "secondary";
  };

  const getAvailableQuantity = (batch: Batch) => {
    return batch.quantity - batch.quantity_used;
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>Batch Tracking - {productName}</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-4 max-h-96 overflow-y-auto">
        {/* Add Batch Form */}
        {showAddBatch && (
          <Card>
            <CardContent className="pt-4 space-y-3">
              <div>
                <Label>Batch ID</Label>
                <Input
                  value={newBatchId}
                  onChange={(e) => setNewBatchId(e.target.value)}
                  placeholder="e.g., LOT-2024-001"
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Quantity</Label>
                <Input
                  type="number"
                  value={newBatchQuantity}
                  onChange={(e) => setNewBatchQuantity(parseInt(e.target.value) || 0)}
                  placeholder="0"
                  className="mt-1"
                />
              </div>
              <div>
                <Label>Expiration Date</Label>
                <Input
                  type="date"
                  value={newBatchExpiry}
                  onChange={(e) => setNewBatchExpiry(e.target.value)}
                  className="mt-1"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => setShowAddBatch(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => addBatchMutation.mutate()}
                  disabled={
                    addBatchMutation.isPending ||
                    !newBatchId ||
                    newBatchQuantity <= 0
                  }
                  className="flex-1"
                >
                  {addBatchMutation.isPending ? "Adding..." : "Add Batch"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Batches List */}
        {batches && batches.length > 0 ? (
          <div className="space-y-2">
            {batches.map((batch: Batch) => (
              <Card key={batch._id}>
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium text-[var(--foreground)]">
                        {batch.batch_id}
                      </h4>
                      <p className="text-xs text-[var(--muted-foreground)]">
                        Created: {new Date(batch.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={getStatusColor(batch.status, batch.expiration_date)}>
                      {batch.status}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-sm mb-3">
                    <div>
                      <p className="text-[var(--muted-foreground)]">Total</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {batch.quantity}
                      </p>
                    </div>
                    <div>
                      <p className="text-[var(--muted-foreground)]">Used</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {batch.quantity_used}
                      </p>
                    </div>
                    <div>
                      <p className="text-[var(--muted-foreground)]">Available</p>
                      <p className="font-semibold text-[var(--foreground)]">
                        {getAvailableQuantity(batch)}
                      </p>
                    </div>
                  </div>

                  {batch.expiration_date && (
                    <p className="text-xs text-[var(--muted-foreground)] mb-2">
                      Expires: {new Date(batch.expiration_date).toLocaleDateString()}
                    </p>
                  )}

                  {batch.status === "active" && batch.expiration_date && (
                    <Button
                      onClick={() => markExpiredMutation.mutate(batch._id)}
                      size="sm"
                      variant="destructive"
                      className="w-full"
                      disabled={markExpiredMutation.isPending}
                    >
                      Mark Expired
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-[var(--muted-foreground)] text-center py-4">
            No batches yet
          </p>
        )}
      </ModalBody>

      <ModalFooter>
        <Button
          onClick={() => setShowAddBatch(!showAddBatch)}
          variant="outline"
        >
          {showAddBatch ? "Cancel" : "Add Batch"}
        </Button>
        <Button onClick={onClose}>Close</Button>
      </ModalFooter>
    </Modal>
  );
}
