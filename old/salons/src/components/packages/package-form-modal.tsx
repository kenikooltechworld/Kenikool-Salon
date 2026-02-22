import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { XIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

interface ServiceQuantity {
  service_id: string;
  quantity: number;
}

interface PackageFormData {
  name: string;
  description: string;
  services: ServiceQuantity[];
  original_price: number;
  package_price: number;
  validity_days?: number;
  is_active: boolean;
  is_transferable: boolean;
  is_giftable: boolean;
}

interface PackageFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PackageFormData) => void;
  packageData?: any;
}

export function PackageFormModal({
  isOpen,
  onClose,
  onSubmit,
  packageData,
}: PackageFormModalProps) {
  const [formData, setFormData] = useState<PackageFormData>({
    name: "",
    description: "",
    services: [],
    original_price: 0,
    package_price: 0,
    validity_days: undefined,
    is_active: true,
    is_transferable: true,
    is_giftable: true,
  });

  const { data: servicesData } = useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const response = await apiClient.get("/api/services", {
        params: { is_active: true },
      });
      return response.data;
    },
  });

  const services = Array.isArray(servicesData) ? servicesData : [];

  useEffect(() => {
    if (packageData) {
      setFormData({
        name: packageData.name || "",
        description: packageData.description || "",
        services: packageData.services || [],
        original_price: packageData.original_price || 0,
        package_price: packageData.package_price || 0,
        validity_days: packageData.validity_days,
        is_active: packageData.is_active ?? true,
        is_transferable: packageData.is_transferable ?? true,
        is_giftable: packageData.is_giftable ?? true,
      });
    } else {
      setFormData({
        name: "",
        description: "",
        services: [],
        original_price: 0,
        package_price: 0,
        validity_days: undefined,
        is_active: true,
        is_transferable: true,
        is_giftable: true,
      });
    }
  }, [packageData, isOpen]);

  const calculateTotalPrice = () => {
    return formData.services.reduce((total, serviceItem) => {
      const service = services.find((s: any) => s.id === serviceItem.service_id);
      return total + ((service?.price || 0) * serviceItem.quantity);
    }, 0);
  };

  const calculateSavings = () => {
    const totalPrice = calculateTotalPrice();
    return totalPrice - formData.package_price;
  };

  const calculateSavingsPercentage = () => {
    const totalPrice = calculateTotalPrice();
    if (totalPrice === 0) return 0;
    return ((calculateSavings() / totalPrice) * 100).toFixed(1);
  };

  const handleServiceToggle = (serviceId: string) => {
    setFormData((prev) => {
      const existingService = prev.services.find(
        (s) => s.service_id === serviceId
      );
      if (existingService) {
        return {
          ...prev,
          services: prev.services.filter((s) => s.service_id !== serviceId),
        };
      } else {
        return {
          ...prev,
          services: [...prev.services, { service_id: serviceId, quantity: 1 }],
        };
      }
    });
  };

  const handleQuantityChange = (serviceId: string, quantity: number) => {
    if (quantity <= 0) return;
    setFormData((prev) => ({
      ...prev,
      services: prev.services.map((s) =>
        s.service_id === serviceId ? { ...s, quantity } : s
      ),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  if (!isOpen) return null;

  const totalPrice = calculateTotalPrice();
  const savings = calculateSavings();
  const savingsPercentage = calculateSavingsPercentage();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-background rounded-lg shadow-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-bold text-foreground">
            {packageData ? "Edit Package" : "Create Package"}
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
            <Label htmlFor="name">Package Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Full Makeover Package"
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
              placeholder="Describe what's included in this package"
              rows={3}
            />
          </div>

          {/* Services Selection with Quantities */}
          <div>
            <Label>Select Services * (minimum 1)</Label>
            <div className="mt-2 max-h-48 overflow-y-auto border border-border rounded-lg p-3 space-y-2">
              {services.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No active services available
                </p>
              ) : (
                services.map((service: any) => {
                  const serviceItem = formData.services.find(
                    (s) => s.service_id === service.id
                  );
                  return (
                    <div
                      key={service.id}
                      className="flex items-center gap-3 p-2 hover:bg-muted/50 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={!!serviceItem}
                        onChange={() => handleServiceToggle(service.id)}
                        className="w-4 h-4"
                      />
                      <div className="flex-1">
                        <p className="font-medium text-foreground">
                          {service.name}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          ₦{service.price.toLocaleString()} -{" "}
                          {service.duration_minutes} mins
                        </p>
                      </div>
                      {serviceItem && (
                        <div className="flex items-center gap-2">
                          <Label className="text-xs text-muted-foreground">
                            Qty:
                          </Label>
                          <Input
                            type="number"
                            min="1"
                            max="10"
                            value={serviceItem.quantity}
                            onChange={(e) =>
                              handleQuantityChange(
                                service.id,
                                parseInt(e.target.value) || 1
                              )
                            }
                            className="w-12 h-8"
                          />
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
            {formData.services.length === 0 && (
              <p className="text-sm text-red-500 mt-1">
                Please select at least one service
              </p>
            )}
          </div>

          {/* Original Price */}
          <div>
            <Label htmlFor="original_price">Original Total Price (₦) *</Label>
            <Input
              id="original_price"
              type="number"
              step="0.01"
              min="0"
              value={formData.original_price}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  original_price: parseFloat(e.target.value) || 0,
                })
              }
              placeholder="0"
              required
            />
          </div>

          {/* Package Price */}
          <div>
            <Label htmlFor="package_price">Package Price (₦) *</Label>
            <Input
              id="package_price"
              type="number"
              step="0.01"
              min="0"
              value={formData.package_price}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  package_price: parseFloat(e.target.value) || 0,
                })
              }
              placeholder="0"
              required
            />
            {formData.services.length > 0 && (
              <div className="mt-2 p-3 bg-muted/50 rounded-lg space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">
                    Total service price:
                  </span>
                  <span className="font-medium text-foreground">
                    ₦{calculateTotalPrice().toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Package price:</span>
                  <span className="font-medium text-foreground">
                    ₦{formData.package_price.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm font-bold pt-2 border-t border-border">
                  <span
                    className={
                      calculateSavings() > 0 ? "text-green-600" : "text-red-600"
                    }
                  >
                    Savings:
                  </span>
                  <span
                    className={
                      calculateSavings() > 0 ? "text-green-600" : "text-red-600"
                    }
                  >
                    ₦{calculateSavings().toLocaleString()} (
                    {calculateSavingsPercentage()}%)
                  </span>
                </div>
                {formData.package_price >= calculateTotalPrice() && (
                  <p className="text-sm text-red-500 mt-2">
                    Package price must be less than total service price
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Validity Days */}
          <div>
            <Label htmlFor="validity_days">Validity Days (Optional)</Label>
            <Input
              id="validity_days"
              type="number"
              min="1"
              value={formData.validity_days || ""}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  validity_days: e.target.value
                    ? parseInt(e.target.value)
                    : undefined,
                })
              }
              placeholder="e.g., 365 for 1 year"
            />
          </div>

          {/* Flags */}
          <div className="space-y-2">
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
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_transferable"
                checked={formData.is_transferable}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    is_transferable: e.target.checked,
                  })
                }
                className="w-4 h-4"
              />
              <Label htmlFor="is_transferable" className="cursor-pointer">
                Transferable (can be transferred between clients)
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_giftable"
                checked={formData.is_giftable}
                onChange={(e) =>
                  setFormData({ ...formData, is_giftable: e.target.checked })
                }
                className="w-4 h-4"
              />
              <Label htmlFor="is_giftable" className="cursor-pointer">
                Giftable (can be purchased as a gift)
              </Label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={
                formData.services.length === 0 ||
                formData.package_price >= calculateTotalPrice()
              }
            >
              {packageData ? "Update Package" : "Create Package"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
