import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useState } from "react";

export interface Inventory {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  reorder_level: number;
  unit_cost: number;
  unit: string;
  category?: string;
  supplier_id?: string;
  last_restocked_at?: string;
  expiry_date?: string;
  is_active: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface InventoryTransaction {
  id: string;
  inventory_id: string;
  transaction_type: "in" | "out" | "adjustment" | "reconciliation";
  quantity_change: number;
  reason: string;
  reference_id?: string;
  reference_type?: string;
  user_id?: string;
  notes?: string;
  created_at: string;
}

export interface StockAlert {
  id: string;
  inventory_id: string;
  alert_type: "low_stock" | "out_of_stock" | "overstock" | "expiry_warning";
  current_quantity: number;
  threshold: number;
  is_resolved: boolean;
  resolved_at?: string;
  created_at: string;
}

export const useInventory = () => {
  const queryClient = useQueryClient();
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(100);

  // List inventory
  const {
    data: inventoryData,
    isLoading: isLoadingInventory,
    error: inventoryError,
  } = useQuery({
    queryKey: ["inventory", skip, limit],
    queryFn: async () => {
      const response = await apiClient.get("/inventory", {
        params: { skip, limit },
      });
      return response.data;
    },
  });

  // Get single inventory
  const getInventory = useQuery({
    queryKey: ["inventory", "single"],
    queryFn: async (inventoryId: string) => {
      const response = await apiClient.get(`/inventory/${inventoryId}`);
      return response.data;
    },
    enabled: false,
  });

  // Create inventory
  const createInventoryMutation = useMutation({
    mutationFn: async (
      data: Omit<Inventory, "id" | "created_at" | "updated_at">,
    ) => {
      const response = await apiClient.post("/inventory", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });

  // Update inventory
  const updateInventoryMutation = useMutation({
    mutationFn: async ({
      id,
      ...data
    }: Partial<Inventory> & { id: string }) => {
      const response = await apiClient.put(`/inventory/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });

  // Deduct inventory
  const deductInventoryMutation = useMutation({
    mutationFn: async ({
      inventoryId,
      quantity,
      reason,
    }: {
      inventoryId: string;
      quantity: number;
      reason: string;
    }) => {
      const response = await apiClient.post(
        `/inventory/${inventoryId}/deduct`,
        {
          quantity,
          reason,
        },
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });

  // Restock inventory
  const restockInventoryMutation = useMutation({
    mutationFn: async ({
      inventoryId,
      quantity,
    }: {
      inventoryId: string;
      quantity: number;
    }) => {
      const response = await apiClient.post(
        `/inventory/${inventoryId}/restock`,
        {
          quantity,
          reason: "restock",
        },
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });

  // Get transactions
  const { data: transactionsData, isLoading: isLoadingTransactions } = useQuery(
    {
      queryKey: ["inventory", "transactions"],
      queryFn: async () => {
        const response = await apiClient.get("/inventory/transactions/list");
        return response.data;
      },
    },
  );

  // Get stock alerts
  const { data: alertsData, isLoading: isLoadingAlerts } = useQuery({
    queryKey: ["inventory", "alerts"],
    queryFn: async () => {
      const response = await apiClient.get("/inventory/alerts/list");
      return response.data;
    },
  });

  // Get low stock items
  const { data: lowStockData, isLoading: isLoadingLowStock } = useQuery({
    queryKey: ["inventory", "low-stock"],
    queryFn: async () => {
      const response = await apiClient.get("/inventory/low-stock/list");
      return response.data;
    },
  });

  // Get inventory value
  const { data: inventoryValue, isLoading: isLoadingValue } = useQuery({
    queryKey: ["inventory", "value"],
    queryFn: async () => {
      const response = await apiClient.get("/inventory/value/summary");
      return response.data;
    },
  });

  // Reconcile inventory
  const reconcileInventoryMutation = useMutation({
    mutationFn: async ({
      inventoryId,
      physicalCount,
      notes,
    }: {
      inventoryId: string;
      physicalCount: number;
      notes?: string;
    }) => {
      const response = await apiClient.post(
        `/inventory/${inventoryId}/reconcile`,
        {
          physical_count: physicalCount,
          notes,
        },
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
    },
  });

  return {
    // Queries
    inventory: inventoryData?.items || [],
    inventoryTotal: inventoryData?.total || 0,
    isLoadingInventory,
    inventoryError,
    transactions: transactionsData?.transactions || [],
    isLoadingTransactions,
    alerts: alertsData?.alerts || [],
    isLoadingAlerts,
    lowStockItems: lowStockData?.items || [],
    isLoadingLowStock,
    inventoryValue,
    isLoadingValue,

    // Mutations
    createInventory: createInventoryMutation.mutate,
    isCreatingInventory: createInventoryMutation.isPending,
    updateInventory: updateInventoryMutation.mutate,
    isUpdatingInventory: updateInventoryMutation.isPending,
    deductInventory: deductInventoryMutation.mutate,
    isDeductingInventory: deductInventoryMutation.isPending,
    restockInventory: restockInventoryMutation.mutate,
    isRestockingInventory: restockInventoryMutation.isPending,
    reconcileInventory: reconcileInventoryMutation.mutate,
    isReconcilingInventory: reconcileInventoryMutation.isPending,

    // Pagination
    skip,
    setSkip,
    limit,
    setLimit,
  };
};
