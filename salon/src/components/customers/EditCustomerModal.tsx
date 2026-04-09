import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
} from "@/components/ui/modal";
import { CustomerForm, type CustomerFormData } from "./CustomerForm";
import { useUpdateCustomer, useCustomer } from "@/hooks/useCustomers";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";

interface EditCustomerModalProps {
  customerId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function EditCustomerModal({
  customerId,
  open,
  onOpenChange,
  onSuccess,
}: EditCustomerModalProps) {
  const { data: customer, isLoading: isLoadingCustomer } = useCustomer(
    customerId || "",
  );
  const updateMutation = useUpdateCustomer();
  const { showToast } = useToast();

  const handleSubmit = async (data: CustomerFormData) => {
    if (!customerId) return;
    try {
      await updateMutation.mutateAsync({
        id: customerId,
        ...data,
      });
      showToast({
        title: "Success",
        description: "Customer updated successfully",
        variant: "success",
      });
      onOpenChange(false);
      onSuccess?.();
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        "Failed to update customer";
      showToast({
        title: "Error",
        description: errorMessage,
        variant: "error",
      });
      throw error;
    }
  };

  return (
    <Modal open={open} onClose={() => onOpenChange(false)} size="lg">
      <ModalHeader>
        <ModalTitle>Edit Customer</ModalTitle>
        <ModalDescription>Update customer information</ModalDescription>
      </ModalHeader>
      <div className="px-6 py-4">
        {isLoadingCustomer ? (
          <div className="space-y-4 xs:space-y-5">
            <Skeleton className="h-10 xs:h-11 w-full" />
            <Skeleton className="h-10 xs:h-11 w-full" />
            <Skeleton className="h-10 xs:h-11 w-full" />
          </div>
        ) : customer ? (
          <CustomerForm
            initialData={{
              firstName: customer.firstName,
              lastName: customer.lastName,
              email: customer.email,
              phone: customer.phone,
              address: customer.address,
              dateOfBirth: customer.dateOfBirth,
              communicationPreference: customer.communicationPreference,
              status: customer.status,
            }}
            onSubmit={handleSubmit}
            isLoading={updateMutation.isPending}
            onCancel={() => onOpenChange(false)}
          />
        ) : null}
      </div>
    </Modal>
  );
}
