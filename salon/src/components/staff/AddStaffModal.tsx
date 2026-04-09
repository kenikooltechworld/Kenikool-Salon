import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
} from "@/components/ui/modal";
import { useToast } from "@/components/ui/toast";
import { StaffForm } from "./StaffForm";
import type { Staff } from "@/types/staff";

interface AddStaffModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (
    data: Omit<Staff, "id" | "createdAt" | "updatedAt">,
  ) => Promise<void>;
  isLoading?: boolean;
  initialData?: Partial<Staff>;
}

export function AddStaffModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  initialData,
}: AddStaffModalProps) {
  const isEditing = !!initialData?.id;
  const { showToast } = useToast();

  const handleSubmit = async (
    data: Omit<Staff, "id" | "createdAt" | "updatedAt">,
  ) => {
    try {
      await onSubmit(data);
      onClose();
    } catch (error) {
      showToast({
        variant: "error",
        title: "Error",
        description:
          error instanceof Error
            ? error.message
            : isEditing
              ? "Failed to update staff member"
              : "Failed to add staff member",
      });
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <ModalHeader>
        <ModalTitle>
          {isEditing ? "Edit Staff Member" : "Add Staff Member"}
        </ModalTitle>
        <ModalDescription>
          {isEditing
            ? "Update the staff member details"
            : "Fill in the details to add a new staff member to your salon"}
        </ModalDescription>
      </ModalHeader>
      <div className="px-6 py-4">
        <StaffForm
          key={isOpen ? "open" : "closed"}
          onSubmit={handleSubmit}
          isLoading={isLoading}
          initialData={initialData}
        />
      </div>
    </Modal>
  );
}
