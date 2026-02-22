import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
} from "@/components/ui/modal";
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

  const handleSubmit = async (
    data: Omit<Staff, "id" | "createdAt" | "updatedAt">,
  ) => {
    await onSubmit(data);
    onClose();
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
          onSubmit={handleSubmit}
          isLoading={isLoading}
          initialData={initialData}
        />
      </div>
    </Modal>
  );
}
