import { useState } from "react";
import {
  useGetPromoCodes,
  useDeletePromoCode,
} from "@/lib/api/hooks/usePromoCodes";
import { PromoCodeList, PromoCodeFormModal } from "@/components/promo-codes";
import { TagIcon, PlusIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { showToast } from "@/lib/utils/toast";

export default function PromoCodesPage() {
  const { data: promoCodes = [], isLoading } = useGetPromoCodes();
  const deleteMutation = useDeletePromoCode();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedCode, setSelectedCode] = useState(null);

  const handleEdit = (code: any) => {
    setSelectedCode(code);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this promo code?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      showToast("Promo code deleted successfully", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to delete promo code",
        "error"
      );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <TagIcon size={32} className="text-(--primary)" />
            Promo Codes
          </h1>
          <p className="text-(--muted-foreground) mt-1">
            Create and manage promotional discount codes
          </p>
        </div>
        <Button
          onClick={() => {
            setSelectedCode(null);
            setIsFormOpen(true);
          }}
        >
          <PlusIcon size={20} />
          Create Code
        </Button>
      </div>

      <Card className="p-6">
        <PromoCodeList
          promoCodes={promoCodes}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </Card>

      <PromoCodeFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedCode(null);
        }}
        promoCode={selectedCode}
      />
    </div>
  );
}
