import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
} from "@/components/ui/modal";
import { useCreateServiceCategory } from "@/hooks/useServiceCategories";
import { ColorPicker } from "@/components/services/ColorPicker";
import { IconPicker } from "@/components/services/IconPicker";
import { useToast } from "@/components/ui/toast";

interface ServiceCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ServiceCategoryModal({
  isOpen,
  onClose,
}: ServiceCategoryModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    color: "#3b82f6",
    icon: "",
  });

  const { showToast } = useToast();
  const { mutate: createCategory, isPending } = useCreateServiceCategory();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      showToast({
        title: "Validation Error",
        description: "Category name is required",
        variant: "error",
      });
      return;
    }

    createCategory(
      {
        name: formData.name,
        description: formData.description || undefined,
        color: formData.color || undefined,
        icon: formData.icon || undefined,
        is_active: true,
      },
      {
        onSuccess: () => {
          showToast({
            title: "Success",
            description: "Category created successfully",
            variant: "success",
          });
          setFormData({
            name: "",
            description: "",
            color: "#3b82f6",
            icon: "",
          });
          onClose();
        },
        onError: (error: any) => {
          const errorMessage =
            error?.response?.data?.detail ||
            error?.message ||
            "Failed to create category";
          showToast({
            title: "Error",
            description: errorMessage,
            variant: "error",
          });
        },
      },
    );
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>Add Service Category</ModalTitle>
        <ModalDescription>
          Create a new service category for your salon
        </ModalDescription>
      </ModalHeader>

      <form
        onSubmit={handleSubmit}
        id="category-form"
        className="space-y-4 p-6"
      >
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Category Name *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Hair Services"
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="Optional description"
            rows={3}
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Color
            </label>
            <ColorPicker
              value={formData.color}
              onChange={(color: string) => setFormData({ ...formData, color })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Icon
            </label>
            <IconPicker
              value={formData.icon}
              onChange={(icon: string) => setFormData({ ...formData, icon })}
            />
          </div>
        </div>
      </form>

      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isPending}>
          Cancel
        </Button>
        <Button
          type="submit"
          form="category-form"
          disabled={isPending || !formData.name.trim()}
          className="cursor-pointer"
        >
          {isPending ? "Creating..." : "Create Category"}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
