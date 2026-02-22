import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { PlusIcon, EditIcon, TrashIcon } from "@/components/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { VariantFormModal } from "./variant-form-modal";
import { toast } from "sonner";

interface Variant {
  id: string;
  name: string;
  description: string;
  price_adjustment: number;
  price_adjustment_type: string;
  duration_adjustment: number;
  final_price: number;
  final_duration: number;
  is_active: boolean;
}

interface ServiceVariantManagerProps {
  serviceId: string;
  basePrice: number;
  baseDuration: number;
}

export function ServiceVariantManager({
  serviceId,
  basePrice,
  baseDuration,
}: ServiceVariantManagerProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVariant, setEditingVariant] = useState<Variant | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["service-variants", serviceId],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/services/${serviceId}/variants`
      );
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (variantData: any) => {
      const response = await apiClient.post(
        `/api/services/${serviceId}/variants`,
        variantData
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["service-variants", serviceId],
      });
      setIsModalOpen(false);
      toast.success("Variant created successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create variant");
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({
      variantId,
      data,
    }: {
      variantId: string;
      data: any;
    }) => {
      const response = await apiClient.patch(
        `/api/services/${serviceId}/variants/${variantId}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["service-variants", serviceId],
      });
      setIsModalOpen(false);
      setEditingVariant(null);
      toast.success("Variant updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update variant");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (variantId: string) => {
      const response = await apiClient.delete(
        `/api/services/${serviceId}/variants/${variantId}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["service-variants", serviceId],
      });
      toast.success("Variant deleted successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete variant");
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: async ({
      variantId,
      isActive,
    }: {
      variantId: string;
      isActive: boolean;
    }) => {
      const response = await apiClient.patch(
        `/api/services/${serviceId}/variants/${variantId}`,
        { is_active: isActive }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["service-variants", serviceId],
      });
      toast.success("Variant status updated");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update status");
    },
  });

  const variants: Variant[] = data?.variants || [];

  const handleCreateVariant = (variantData: any) => {
    createMutation.mutate(variantData);
  };

  const handleUpdateVariant = (variantData: any) => {
    if (editingVariant) {
      updateMutation.mutate({
        variantId: editingVariant.id,
        data: variantData,
      });
    }
  };

  const handleDeleteVariant = (variantId: string, variantName: string) => {
    if (
      confirm(
        `Are you sure you want to delete the variant "${variantName}"? This action cannot be undone.`
      )
    ) {
      deleteMutation.mutate(variantId);
    }
  };

  const handleToggleActive = (variantId: string, currentStatus: boolean) => {
    toggleActiveMutation.mutate({
      variantId,
      isActive: !currentStatus,
    });
  };

  const handleEditClick = (variant: Variant) => {
    setEditingVariant(variant);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingVariant(null);
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-foreground">
            Service Variants
          </h2>
          <Button
            onClick={() => {
              setEditingVariant(null);
              setIsModalOpen(true);
            }}
            size="sm"
          >
            <PlusIcon size={16} className="mr-2" />
            Add Variant
          </Button>
        </div>

        {variants.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">
              No variants created yet
            </p>
            <p className="text-sm text-muted-foreground">
              Create variants to offer different pricing or duration options for
              this service
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {variants.map((variant) => (
              <div
                key={variant.id}
                className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-medium text-foreground">
                        {variant.name}
                      </h3>
                      <Badge
                        variant={variant.is_active ? "success" : "secondary"}
                      >
                        {variant.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>

                    {variant.description && (
                      <p className="text-sm text-muted-foreground mb-3">
                        {variant.description}
                      </p>
                    )}

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Price</p>
                        <p className="font-medium text-foreground">
                          ₦{variant.final_price.toLocaleString()}
                          <span className="text-xs text-muted-foreground ml-2">
                            (
                            {variant.price_adjustment_type === "fixed"
                              ? `${
                                  variant.price_adjustment >= 0 ? "+" : ""
                                }₦${variant.price_adjustment.toLocaleString()}`
                              : `${variant.price_adjustment >= 0 ? "+" : ""}${
                                  variant.price_adjustment
                                }%`}
                            )
                          </span>
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Duration</p>
                        <p className="font-medium text-foreground">
                          {variant.final_duration} min
                          <span className="text-xs text-muted-foreground ml-2">
                            ({variant.duration_adjustment >= 0 ? "+" : ""}
                            {variant.duration_adjustment} min)
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        handleToggleActive(variant.id, variant.is_active)
                      }
                    >
                      {variant.is_active ? "Deactivate" : "Activate"}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditClick(variant)}
                    >
                      <EditIcon size={16} />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        handleDeleteVariant(variant.id, variant.name)
                      }
                    >
                      <TrashIcon size={16} />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <VariantFormModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onSubmit={editingVariant ? handleUpdateVariant : handleCreateVariant}
        variant={editingVariant}
        basePrice={basePrice}
        baseDuration={baseDuration}
      />
    </>
  );
}
