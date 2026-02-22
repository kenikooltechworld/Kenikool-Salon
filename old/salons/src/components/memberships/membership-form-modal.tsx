import { useState, useEffect } from "react";
import {
  useCreatePlan,
  MembershipPlan,
  PlanCreate,
} from "@/lib/api/hooks/useMemberships";
import { XIcon, PlusIcon, TrashIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface MembershipFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan?: MembershipPlan | null;
}

export function MembershipFormModal({
  isOpen,
  onClose,
  plan,
}: MembershipFormModalProps) {
  const createMutation = useCreatePlan();

  const [formData, setFormData] = useState<PlanCreate>({
    name: "",
    description: "",
    price: 0,
    billing_cycle: "monthly",
    benefits: [],
    discount_percentage: 0,
  });

  const [newBenefit, setNewBenefit] = useState("");

  useEffect(() => {
    if (plan) {
      setFormData({
        name: plan.name,
        description: plan.description,
        price: plan.price,
        billing_cycle: plan.billing_cycle,
        benefits: plan.benefits || [],
        discount_percentage: plan.discount_percentage,
      });
    } else {
      setFormData({
        name: "",
        description: "",
        price: 0,
        billing_cycle: "monthly",
        benefits: [],
        discount_percentage: 0,
      });
    }
  }, [plan, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await createMutation.mutateAsync(formData);
      showToast(
        `Membership plan ${plan ? "updated" : "created"} successfully`,
        "success"
      );
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to save membership plan",
        "error"
      );
    }
  };

  const addBenefit = () => {
    if (newBenefit.trim()) {
      setFormData({
        ...formData,
        benefits: [...formData.benefits, newBenefit.trim()],
      });
      setNewBenefit("");
    }
  };

  const removeBenefit = (index: number) => {
    setFormData({
      ...formData,
      benefits: formData.benefits.filter((_, i) => i !== index),
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-[var(--radius-lg)] w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
          <h2 className="text-xl font-bold">
            {plan ? "Edit" : "Create"} Membership Plan
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <XIcon size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Plan Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="Gold Membership"
                className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Billing Cycle *
              </label>
              <select
                value={formData.billing_cycle}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    billing_cycle: e.target.value as any,
                  })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary"
                required
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Describe the membership plan..."
              rows={3}
              className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Price ($) *
              </label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    price: parseFloat(e.target.value),
                  })
                }
                min="0"
                step="0.01"
                className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Discount (%)
              </label>
              <input
                type="number"
                value={formData.discount_percentage || 0}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    discount_percentage: parseFloat(e.target.value),
                  })
                }
                min="0"
                max="100"
                step="1"
                className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Benefits</label>
            <div className="space-y-2">
              {formData.benefits.map((benefit, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 p-2 bg-muted rounded-[var(--radius-md)]"
                >
                  <span className="flex-1 text-sm">{benefit}</span>
                  <button
                    type="button"
                    onClick={() => removeBenefit(index)}
                    className="p-1 text-destructive hover:bg-destructive/10 rounded"
                  >
                    <TrashIcon size={16} />
                  </button>
                </div>
              ))}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newBenefit}
                  onChange={(e) => setNewBenefit(e.target.value)}
                  onKeyPress={(e) =>
                    e.key === "Enter" && (e.preventDefault(), addBenefit())
                  }
                  placeholder="Add a benefit..."
                  className="flex-1 px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <button
                  type="button"
                  onClick={addBenefit}
                  className="px-4 py-2 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors"
                >
                  <PlusIcon size={20} />
                </button>
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-muted text-foreground rounded-[var(--radius-md)] hover:bg-muted/80 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-[var(--radius-md)] hover:bg-primary/90 transition-colors font-medium disabled:opacity-50"
            >
              {createMutation.isPending
                ? "Saving..."
                : plan
                ? "Update Plan"
                : "Create Plan"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
