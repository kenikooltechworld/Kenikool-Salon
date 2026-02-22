import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { XIcon } from "@/components/icons";

interface VariantFormData {
  name: string;
  description: string;
  price_adjustment: number;
  price_adjustment_type: "fixed" | "percentage";
  duration_adjustment: number;
  is_active: boolean;
}

interface VariantFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: VariantFormData) => void;
  variant?: any;
  basePrice: number;
  baseDuration: number;
}

export function VariantFormModal({
  isOpen,
  onClose,
  onSubmit,
  variant,
  basePrice,
  baseDuration,
}: VariantFormModalProps) {
  const [formData, setFormData] = useState<VariantFormData>({
    name: "",
    description: "",
    price_adjustment: 0,
    price_adjustment_type: "fixed",
    duration_adjustment: 0,
    is_active: true,
  });

  useEffect(() => {
    if (variant) {
      setFormData({
        name: variant.name || "",
        description: variant.description || "",
        price_adjustment: variant.price_adjustment || 0,
        price_adjustment_type: variant.price_adjustment_type || "fixed",
        duration_adjustment: variant.duration_adjustment || 0,
        is_active: variant.is_active ?? true,
      });
    } else {
      setFormData({
        name: "",
        description: "",
        price_adjustment: 0,
        price_adjustment_type: "fixed",
        duration_adjustment: 0,
        is_active: true,
      });
    }
  }, [variant, isOpen]);

  const calculateFinalPrice = () => {
    if (formData.price_adjustment_type === "fixed") {
      return basePrice + formData.price_adjustment;
    } else {
      return basePrice * (1 + formData.price_adjustment / 100);
    }
  };

  const calculateFinalDuration = () => {
    return baseDuration + formData.duration_adjustment;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-background rounded-lg shadow-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-bold text-foreground">
            {variant ? "Edit Variant" : "Create Variant"}
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <XIcon size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Name */}
          <div>
            <Label htmlFor="name">Variant Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Premium, Express, Deluxe"
              required
            />
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Describe what makes this variant different"
              rows={3}
            />
          </div>

          {/* Price Adjustment Type */}
          <div>
            <Label htmlFor="price_adjustment_type">Price Adjustment Type</Label>
            <Select
              value={formData.price_adjustment_type}
              onValueChange={(value: "fixed" | "percentage") =>
                setFormData({ ...formData, price_adjustment_type: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fixed">Fixed Amount (₦)</SelectItem>
                <SelectItem value="percentage">Percentage (%)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Price Adjustment */}
          <div>
            <Label htmlFor="price_adjustment">
              Price Adjustment{" "}
              {formData.price_adjustment_type === "fixed" ? "(₦)" : "(%)"}
            </Label>
            <Input
              id="price_adjustment"
              type="number"
              step="0.01"
              value={formData.price_adjustment}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  price_adjustment: parseFloat(e.target.value) || 0,
                })
              }
              placeholder="0"
            />
            <p className="text-sm text-muted-foreground mt-1">
              Base price: ₦{basePrice.toLocaleString()} → Final price: ₦
              {calculateFinalPrice().toLocaleString()}
            </p>
          </div>

          {/* Duration Adjustment */}
          <div>
            <Label htmlFor="duration_adjustment">
              Duration Adjustment (minutes)
            </Label>
            <Input
              id="duration_adjustment"
              type="number"
              value={formData.duration_adjustment}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  duration_adjustment: parseInt(e.target.value) || 0,
                })
              }
              placeholder="0"
            />
            <p className="text-sm text-muted-foreground mt-1">
              Base duration: {baseDuration} min → Final duration:{" "}
              {calculateFinalDuration()} min
            </p>
          </div>

          {/* Active Status */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) =>
                setFormData({ ...formData, is_active: e.target.checked })
              }
              className="w-4 h-4"
            />
            <Label htmlFor="is_active" className="cursor-pointer">
              Active (available for booking)
            </Label>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              {variant ? "Update Variant" : "Create Variant"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
