import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CustomerForm, type CustomerFormData } from "./CustomerForm";
import { useUpdateCustomer, useCustomer } from "@/hooks/useCustomers";
import { Skeleton } from "@/components/ui/skeleton";

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

  const handleSubmit = async (data: CustomerFormData) => {
    if (!customerId) return;
    await updateMutation.mutateAsync({
      id: customerId,
      ...data,
    });
    onOpenChange(false);
    onSuccess?.();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader className="space-y-1 xs:space-y-2 flex-shrink-0">
          <DialogTitle className="text-lg xs:text-xl sm:text-2xl font-bold">
            Edit Customer
          </DialogTitle>
          <DialogDescription>Update customer information</DialogDescription>
        </DialogHeader>

        <div className="overflow-y-auto flex-1 min-h-0">
          <div className="pr-2">
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
        </div>
      </DialogContent>
    </Dialog>
  );
}
