import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { PlusIcon } from "@/components/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { PackageList } from "@/components/packages/package-list";
import { PackageFormModal } from "@/components/packages/package-form-modal";
import { toast } from "sonner";

export default function PackagesPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPackage, setEditingPackage] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["service-packages"],
    queryFn: async () => {
      const response = await apiClient.get("/api/services/packages");
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (packageData: any) => {
      const response = await apiClient.post(
        "/api/services/packages",
        packageData
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      setIsModalOpen(false);
      toast.success("Package created successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to create package");
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({
      packageId,
      data,
    }: {
      packageId: string;
      data: any;
    }) => {
      const response = await apiClient.patch(
        `/api/services/packages/${packageId}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      setIsModalOpen(false);
      setEditingPackage(null);
      toast.success("Package updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update package");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (packageId: string) => {
      const response = await apiClient.delete(
        `/api/services/packages/${packageId}`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      toast.success("Package deleted successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete package");
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: async ({
      packageId,
      isActive,
    }: {
      packageId: string;
      isActive: boolean;
    }) => {
      const response = await apiClient.patch(
        `/api/services/packages/${packageId}`,
        { is_active: isActive }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      toast.success("Package status updated");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update status");
    },
  });

  const packages = data?.packages || [];

  const handleCreatePackage = (packageData: any) => {
    createMutation.mutate(packageData);
  };

  const handleUpdatePackage = (packageData: any) => {
    if (editingPackage) {
      updateMutation.mutate({
        packageId: editingPackage.id,
        data: packageData,
      });
    }
  };

  const handleDeletePackage = (packageId: string, packageName: string) => {
    if (
      confirm(
        `Are you sure you want to delete the package "${packageName}"? This action cannot be undone.`
      )
    ) {
      deleteMutation.mutate(packageId);
    }
  };

  const handleToggleActive = (packageId: string, currentStatus: boolean) => {
    toggleActiveMutation.mutate({
      packageId,
      isActive: !currentStatus,
    });
  };

  const handleEditClick = (pkg: any) => {
    setEditingPackage(pkg);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingPackage(null);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Service Packages
          </h1>
          <p className="text-muted-foreground mt-1">
            Create bundled service packages with discounted pricing
          </p>
        </div>
        <Button
          onClick={() => {
            setEditingPackage(null);
            setIsModalOpen(true);
          }}
        >
          <PlusIcon size={20} className="mr-2" />
          Create Package
        </Button>
      </div>

      <PackageList
        packages={packages}
        onEdit={handleEditClick}
        onDelete={handleDeletePackage}
        onToggleActive={handleToggleActive}
      />

      <PackageFormModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onSubmit={editingPackage ? handleUpdatePackage : handleCreatePackage}
        packageData={editingPackage}
      />
    </div>
  );
}
