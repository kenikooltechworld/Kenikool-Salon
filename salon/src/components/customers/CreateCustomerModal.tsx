import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CustomerForm, type CustomerFormData } from "./CustomerForm";
import { useCreateCustomer } from "@/hooks/useCustomers";

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

  const handleSubmit = async (data: CustomerFormData) => {
    const submitData = {
      ...data,
      status: (data.status || "active") as "active" | "inactive",
    };
    await createMutation.mutateAsync(submitData);
    onOpenChange(false);
    onSuccess?.();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="space-y-1 xs:space-y-2 flex-shrink-0">
          <DialogTitle className="text-lg xs:text-xl sm:text-2xl font-bold">
            Add New Customer
          </DialogTitle>
          <DialogDescription>
            Create a new customer profile with their contact information
          </DialogDescription>
        </DialogHeader>
        <div className="overflow-y-auto flex-1 min-h-0">
          <div className="pr-2">
            <CustomerForm
              onSubmit={handleSubmit}
              isLoading={createMutation.isPending}
              onCancel={() => onOpenChange(false)}
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
