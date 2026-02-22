import { useState } from "react";
import {
  useDiscounts,
  useCreateDiscount,
  useUpdateDiscount,
} from "@/hooks/useDiscount";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

interface DiscountForm {
  discountCode: string;
  discountType: "percentage" | "fixed" | "loyalty" | "bulk";
  discountValue: number;
  applicableTo: "transaction" | "item" | "service" | "product";
  maxDiscount?: number;
  validFrom?: string;
  validUntil?: string;
  usageLimit?: number;
}

export default function DiscountManagement() {
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<DiscountForm>({
    discountCode: "",
    discountType: "percentage",
    discountValue: 0,
    applicableTo: "transaction",
  });

  const { data: discountsData, isLoading } = useDiscounts({
    page,
    pageSize: 20,
  });
  const createDiscount = useCreateDiscount();
  const updateDiscount = useUpdateDiscount();
  const { showToast } = useToast();

  const discounts = discountsData?.discounts || [];
  const total = discountsData?.total || 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.discountCode || formData.discountValue <= 0) {
      showToast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "error",
      });
      return;
    }

    try {
      if (editingId) {
        await updateDiscount.mutateAsync({
          discountId: editingId,
          data: {
            discountValue: formData.discountValue,
            active: true,
            validUntil: formData.validUntil,
            usageLimit: formData.usageLimit,
          },
        });
        showToast({
          title: "Success",
          description: "Discount updated successfully",
          variant: "success",
        });
      } else {
        await createDiscount.mutateAsync(formData);
        showToast({
          title: "Success",
          description: "Discount created successfully",
          variant: "success",
        });
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({
        discountCode: "",
        discountType: "percentage",
        discountValue: 0,
        applicableTo: "transaction",
      });
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to save discount",
        variant: "error",
      });
    }
  };

  const handleEdit = (discount: any) => {
    setFormData({
      discountCode: discount.discountCode,
      discountType: discount.discountType,
      discountValue: discount.discountValue,
      applicableTo: discount.applicableTo,
      maxDiscount: discount.maxDiscount,
      validFrom: discount.validFrom,
      validUntil: discount.validUntil,
      usageLimit: discount.usageLimit,
    });
    setEditingId(discount.id);
    setShowForm(true);
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <h2 className="text-xl md:text-2xl font-bold text-foreground">
          Discount Management
        </h2>
        <Button
          onClick={() => {
            setShowForm(!showForm);
            setEditingId(null);
            setFormData({
              discountCode: "",
              discountType: "percentage",
              discountValue: 0,
              applicableTo: "transaction",
            });
          }}
          className="w-full sm:w-auto text-sm md:text-base"
        >
          {showForm ? "Cancel" : "New Discount"}
        </Button>
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <Card className="p-4 md:p-6">
          <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
            {editingId ? "Edit Discount" : "Create New Discount"}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Discount Code
                </label>
                <Input
                  type="text"
                  value={formData.discountCode}
                  onChange={(e) =>
                    setFormData({ ...formData, discountCode: e.target.value })
                  }
                  placeholder="e.g., SUMMER20"
                  disabled={!!editingId}
                  className="text-sm"
                />
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Type
                </label>
                <select
                  value={formData.discountType}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      discountType: e.target.value as any,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
                >
                  <option value="percentage">Percentage</option>
                  <option value="fixed">Fixed Amount</option>
                  <option value="loyalty">Loyalty</option>
                  <option value="bulk">Bulk</option>
                </select>
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Value
                </label>
                <Input
                  type="number"
                  value={formData.discountValue}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      discountValue: parseFloat(e.target.value),
                    })
                  }
                  placeholder="0"
                  step="0.01"
                  className="text-sm"
                />
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Applicable To
                </label>
                <select
                  value={formData.applicableTo}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      applicableTo: e.target.value as any,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
                >
                  <option value="transaction">Transaction</option>
                  <option value="item">Item</option>
                  <option value="service">Service</option>
                  <option value="product">Product</option>
                </select>
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Max Discount (Optional)
                </label>
                <Input
                  type="number"
                  value={formData.maxDiscount || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      maxDiscount: e.target.value
                        ? parseFloat(e.target.value)
                        : undefined,
                    })
                  }
                  placeholder="No limit"
                  step="0.01"
                  className="text-sm"
                />
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Usage Limit (Optional)
                </label>
                <Input
                  type="number"
                  value={formData.usageLimit || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      usageLimit: e.target.value
                        ? parseInt(e.target.value)
                        : undefined,
                    })
                  }
                  placeholder="No limit"
                  className="text-sm"
                />
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Valid From (Optional)
                </label>
                <Input
                  type="date"
                  value={formData.validFrom || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, validFrom: e.target.value })
                  }
                  className="text-sm"
                />
              </div>
              <div>
                <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
                  Valid Until (Optional)
                </label>
                <Input
                  type="date"
                  value={formData.validUntil || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, validUntil: e.target.value })
                  }
                  className="text-sm"
                />
              </div>
            </div>
            <div className="flex gap-2 md:gap-3 flex-col sm:flex-row">
              <Button
                type="submit"
                disabled={createDiscount.isPending || updateDiscount.isPending}
                className="flex-1 text-sm md:text-base"
              >
                {createDiscount.isPending || updateDiscount.isPending
                  ? "Saving..."
                  : "Save Discount"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowForm(false);
                  setEditingId(null);
                }}
                className="flex-1 text-sm md:text-base"
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Discounts List */}
      <Card className="p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
          Active Discounts
        </h3>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : discounts.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No discounts yet
          </p>
        ) : (
          <div className="space-y-2 md:space-y-3">
            {discounts.map((discount) => (
              <div
                key={discount.id}
                className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2 p-3 md:p-4 bg-muted rounded-lg"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm md:text-base text-foreground truncate">
                    {discount.discountCode}
                  </p>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    <Badge variant="secondary" className="capitalize text-xs">
                      {discount.discountType}
                    </Badge>
                    <Badge variant="outline" className="capitalize text-xs">
                      {discount.applicableTo}
                    </Badge>
                    {discount.active && (
                      <Badge className="text-xs">Active</Badge>
                    )}
                  </div>
                  <p className="text-xs md:text-sm text-muted-foreground mt-2">
                    Value: {discount.discountValue}
                    {discount.discountType === "percentage" ? "%" : "₦"} | Used:{" "}
                    {discount.usageCount}
                    {discount.usageLimit ? `/${discount.usageLimit}` : ""}
                  </p>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(discount)}
                    className="text-xs md:text-sm"
                  >
                    Edit
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div className="flex justify-between items-center mt-6 pt-6 border-t border-border gap-2 flex-wrap">
            <Button
              variant="outline"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="text-sm"
            >
              Previous
            </Button>
            <span className="text-xs md:text-sm text-muted-foreground">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage(page + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className="text-sm"
            >
              Next
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
