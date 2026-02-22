import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { CheckIcon, AlertTriangleIcon, XIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";

interface BulkOperationsPanelProps {
  selectedServiceIds: string[];
  onClose: () => void;
  onSuccess: () => void;
}

export function BulkOperationsPanel({
  selectedServiceIds,
  onClose,
  onSuccess,
}: BulkOperationsPanelProps) {
  const [operation, setOperation] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>("");

  // Operation-specific state
  const [category, setCategory] = useState("");
  const [priceAdjustmentType, setPriceAdjustmentType] = useState<
    "percentage" | "fixed"
  >("percentage");
  const [priceAdjustmentValue, setPriceAdjustmentValue] = useState(0);
  const [stylistId, setStylistId] = useState("");
  const [stylistAction, setStylistAction] = useState<"add" | "remove">("add");

  const handleOperation = async () => {
    if (!operation) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      let response;
      const payload = { service_ids: selectedServiceIds };

      switch (operation) {
        case "activate":
          response = await apiClient.post(
            "/api/services/bulk/activate",
            payload
          );
          break;
        case "deactivate":
          response = await apiClient.post(
            "/api/services/bulk/deactivate",
            payload
          );
          break;
        case "category":
          response = await apiClient.post(
            "/api/services/bulk/update-category",
            {
              ...payload,
              category,
            }
          );
          break;
        case "price":
          response = await apiClient.post("/api/services/bulk/adjust-price", {
            ...payload,
            adjustment_type: priceAdjustmentType,
            adjustment_value: priceAdjustmentValue,
          });
          break;
        case "stylist":
          response = await apiClient.post("/api/services/bulk/assign-stylist", {
            ...payload,
            stylist_id: stylistId,
            action: stylistAction,
          });
          break;
      }

      setResult(response?.data);
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Operation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Bulk Operations
            </h3>
            <p className="text-sm text-muted-foreground">
              {selectedServiceIds.length} service(s) selected
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={onClose}>
            <XIcon size={16} />
          </Button>
        </div>

        {error && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h4 className="font-semibold">Error</h4>
              <p className="text-sm">{error}</p>
            </div>
          </Alert>
        )}

        {result && (
          <Alert variant="success">
            <CheckIcon size={20} />
            <div>
              <h4 className="font-semibold">Success</h4>
              <p className="text-sm">
                {result.success_count} succeeded, {result.failed_count} failed
              </p>
            </div>
          </Alert>
        )}

        {/* Operation Selection */}
        <div>
          <Label>Select Operation</Label>
          <select
            value={operation}
            onChange={(e) => setOperation(e.target.value)}
            className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground mt-2"
          >
            <option value="">Choose an operation...</option>
            <option value="activate">Activate Services</option>
            <option value="deactivate">Deactivate Services</option>
            <option value="category">Update Category</option>
            <option value="price">Adjust Price</option>
            <option value="stylist">Assign/Remove Stylist</option>
          </select>
        </div>

        {/* Category Update */}
        {operation === "category" && (
          <div>
            <Label htmlFor="category">New Category</Label>
            <Input
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Enter category name"
            />
          </div>
        )}

        {/* Price Adjustment */}
        {operation === "price" && (
          <div className="space-y-4">
            <div>
              <Label>Adjustment Type</Label>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => setPriceAdjustmentType("percentage")}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                    priceAdjustmentType === "percentage"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-muted-foreground border-border hover:bg-muted"
                  }`}
                >
                  Percentage
                </button>
                <button
                  onClick={() => setPriceAdjustmentType("fixed")}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                    priceAdjustmentType === "fixed"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-muted-foreground border-border hover:bg-muted"
                  }`}
                >
                  Fixed Amount
                </button>
              </div>
            </div>
            <div>
              <Label htmlFor="priceValue">
                Adjustment Value{" "}
                {priceAdjustmentType === "percentage" ? "(%)" : "(₦)"}
              </Label>
              <Input
                id="priceValue"
                type="number"
                value={priceAdjustmentValue}
                onChange={(e) =>
                  setPriceAdjustmentValue(Number(e.target.value))
                }
                placeholder={
                  priceAdjustmentType === "percentage"
                    ? "e.g., 10 for +10%"
                    : "e.g., 1000"
                }
              />
              <p className="text-xs text-muted-foreground mt-1">
                {priceAdjustmentType === "percentage"
                  ? "Use positive for increase, negative for decrease"
                  : "Use positive to add, negative to subtract"}
              </p>
            </div>
          </div>
        )}

        {/* Stylist Assignment */}
        {operation === "stylist" && (
          <div className="space-y-4">
            <div>
              <Label htmlFor="stylistId">Stylist ID</Label>
              <Input
                id="stylistId"
                value={stylistId}
                onChange={(e) => setStylistId(e.target.value)}
                placeholder="Enter stylist ID"
              />
            </div>
            <div>
              <Label>Action</Label>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => setStylistAction("add")}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                    stylistAction === "add"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-muted-foreground border-border hover:bg-muted"
                  }`}
                >
                  Add Stylist
                </button>
                <button
                  onClick={() => setStylistAction("remove")}
                  className={`flex-1 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                    stylistAction === "remove"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background text-muted-foreground border-border hover:bg-muted"
                  }`}
                >
                  Remove Stylist
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={handleOperation}
            disabled={loading || !operation}
            className="flex-1"
          >
            {loading ? (
              <>
                <Spinner size="sm" />
                Processing...
              </>
            ) : (
              "Execute Operation"
            )}
          </Button>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </div>
    </Card>
  );
}
