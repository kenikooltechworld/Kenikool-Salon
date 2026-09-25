import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
} from "@/components/ui/modal";
import { CustomerForm, type CustomerFormData } from "./CustomerForm";
import { useCreateCustomer } from "@/hooks/useCustomers";
import { useToast } from "@/components/ui/toast";
import { useEffect, useRef } from "react";

interface CreateCustomerModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function CreateCustomerModal({
  open,
  onOpenChange,
  onSuccess,
}: CreateCustomerModalProps) {
  const createMutation = useCreateCustomer();
  const { showToast } = useToast();
  const submitStarted = useRef(false);

  useEffect(() => {
    if (open) {
      submitStarted.current = false;
    }
  }, [open]);

  const handleSubmit = async (data: CustomerFormData) => {
    if (submitStarted.current) {
      return;
    }
    submitStarted.current = true;

    try {
      const submitData = {
        ...data,
        status: (data.status || "active") as "active" | "inactive",
      };
      await createMutation.mutateAsync(submitData);
      showToast({
        title: "Success",
        description: "Customer created successfully",
        variant: "success",
      });
      onOpenChange(false);
      onSuccess?.();
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail ||
        error.message ||
        "Failed to create customer";
      showToast({
        title: "Error",
        description: errorMessage,
        variant: "error",
      });
    }
  };

  return (
    <Modal open={open} onClose={() => onOpenChange(false)} size="lg">
      <ModalHeader>
        <ModalTitle>Add New Customer</ModalTitle>
        <ModalDescription>
          Create a new customer profile with their contact information
        </ModalDescription>
      </ModalHeader>
      <div className="px-6 py-4">
        <CustomerForm
          onSubmit={handleSubmit}
          isLoading={createMutation.isPending}
          onCancel={() => onOpenChange(false)}
        />
      </div>
    </Modal>
  );
}
