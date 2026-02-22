import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CheckIcon,
  AlertTriangleIcon,
  DollarIcon,
  TrashIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

interface CommissionStructure {
  commission_type: "percentage" | "fixed";
  default_rate: number;
  stylist_overrides: Record<string, number>;
}

interface CommissionEditorProps {
  serviceId: string;
  servicePrice: number;
  assignedStylists: string[];
}

export function CommissionEditor({
  serviceId,
  servicePrice,
  assignedStylists,
}: CommissionEditorProps) {
  const [commissionType, setCommissionType] = useState<"percentage" | "fixed">(
    "percentage"
  );
  const [defaultRate, setDefaultRate] = useState(0);
  const [stylistOverrides, setStylistOverrides] = useState<
    Record<string, number>
  >({});
  const [showSuccess, setShowSuccess] = useState(false);
  const queryClient = useQueryClient();

  // Fetch current commission structure
  const { data: commissionData } = useQuery({
    queryKey: ["service-commission", serviceId],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/services/${serviceId}/commission`
      );
      return response.data;
    },
    enabled: !!serviceId && serviceId !== "undefined",
  });

  useEffect(() => {
    if (commissionData?.commission_structure) {
      const structure = commissionData.commission_structure;
      setCommissionType(structure.commission_type);
      setDefaultRate(structure.default_rate);
      setStylistOverrides(structure.stylist_overrides || {});
    }
  }, [commissionData]);

  const saveMutation = useMutation({
    mutationFn: async (structure: CommissionStructure) => {
      const response = await apiClient.put(
        `/api/services/${serviceId}/commission`,
        structure
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["service-commission", serviceId],
      });
      queryClient.invalidateQueries({
        queryKey: ["service-details", serviceId],
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    },
  });

  const handleSave = () => {
    saveMutation.mutate({
      commission_type: commissionType,
      default_rate: defaultRate,
      stylist_overrides: stylistOverrides,
    });
  };

  const handleReset = () => {
    if (commissionData?.commission_structure) {
      const structure = commissionData.commission_structure;
      setCommissionType(structure.commission_type);
      setDefaultRate(structure.default_rate);
      setStylistOverrides(structure.stylist_overrides || {});
    } else {
      setCommissionType("percentage");
      setDefaultRate(0);
      setStylistOverrides({});
    }
  };

  const setStylistOverride = (stylistId: string, rate: number) => {
    setStylistOverrides((prev) => ({
      ...prev,
      [stylistId]: rate,
    }));
  };

  const removeStylistOverride = (stylistId: string) => {
    setStylistOverrides((prev) => {
      const newOverrides = { ...prev };
      delete newOverrides[stylistId];
      return newOverrides;
    });
  };

  const calculateCommission = (rate: number) => {
    if (commissionType === "percentage") {
      return (servicePrice * rate) / 100;
    }
    return rate;
  };

  const examples = commissionData?.examples || {};

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Commission Structure
          </h3>
          <p className="text-sm text-muted-foreground">
            Configure how stylists earn commission for this service
          </p>
        </div>

        {showSuccess && (
          <Alert variant="success">
            <CheckIcon size={20} />
            <div>
              <h4 className="font-semibold">Success</h4>
              <p className="text-sm">
                Commission structure updated successfully
              </p>
            </div>
          </Alert>
        )}

        {saveMutation.isError && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h4 className="font-semibold">Error</h4>
              <p className="text-sm">
                {saveMutation.error instanceof Error
                  ? saveMutation.error.message
                  : "Failed to update commission structure"}
              </p>
            </div>
          </Alert>
        )}

        {/* Commission Type */}
        <div>
          <Label>Commission Type</Label>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setCommissionType("percentage")}
              className={`flex-1 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                commissionType === "percentage"
                  ? "bg-primary text-primary-foreground border-primary shadow-sm"
                  : "bg-background text-muted-foreground border-border hover:bg-muted hover:shadow-sm"
              }`}
            >
              Percentage
            </button>
            <button
              onClick={() => setCommissionType("fixed")}
              className={`flex-1 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
                commissionType === "fixed"
                  ? "bg-primary text-primary-foreground border-primary shadow-sm"
                  : "bg-background text-muted-foreground border-border hover:bg-muted hover:shadow-sm"
              }`}
            >
              Fixed Amount
            </button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {commissionType === "percentage"
              ? "Commission as a percentage of service price"
              : "Fixed commission amount per booking"}
          </p>
        </div>

        {/* Default Rate */}
        <div>
          <Label htmlFor="default_rate">
            Default Commission Rate
            {commissionType === "percentage" ? " (%)" : " (₦)"}
          </Label>
          <Input
            id="default_rate"
            type="number"
            min="0"
            max={commissionType === "percentage" ? "100" : undefined}
            step={commissionType === "percentage" ? "0.1" : "100"}
            value={defaultRate}
            onChange={(e) => setDefaultRate(parseFloat(e.target.value) || 0)}
          />
          <p className="text-xs text-muted-foreground mt-1">
            Default commission for all stylists (can be overridden per stylist)
          </p>
        </div>

        {/* Commission Example */}
        <div className="bg-muted/50 p-4 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <DollarIcon size={16} className="text-primary" />
            <h4 className="font-medium text-foreground">Commission Example</h4>
          </div>
          <p className="text-sm text-muted-foreground">
            Service Price: ₦{servicePrice.toLocaleString()}
          </p>
          <p className="text-lg font-bold text-foreground mt-1">
            Default Commission: ₦
            {calculateCommission(defaultRate).toLocaleString()}
          </p>
        </div>

        {/* Stylist Overrides */}
        {assignedStylists.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label>Stylist-Specific Overrides</Label>
              <span className="text-xs text-muted-foreground">
                {Object.keys(stylistOverrides).length} override(s)
              </span>
            </div>

            <div className="space-y-3">
              {assignedStylists.map((stylistId) => {
                const hasOverride = stylistId in stylistOverrides;
                const overrideRate = stylistOverrides[stylistId] || defaultRate;

                return (
                  <div
                    key={stylistId}
                    className="flex items-center gap-3 p-3 border border-border rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">
                        Stylist {stylistId.slice(0, 8)}
                      </p>
                      {hasOverride ? (
                        <p className="text-xs text-muted-foreground">
                          Custom: ₦
                          {calculateCommission(overrideRate).toLocaleString()}
                        </p>
                      ) : (
                        <p className="text-xs text-muted-foreground">
                          Using default rate
                        </p>
                      )}
                    </div>

                    {hasOverride ? (
                      <>
                        <Input
                          type="number"
                          min="0"
                          max={
                            commissionType === "percentage" ? "100" : undefined
                          }
                          step={commissionType === "percentage" ? "0.1" : "100"}
                          value={overrideRate}
                          onChange={(e) =>
                            setStylistOverride(
                              stylistId,
                              parseFloat(e.target.value) || 0
                            )
                          }
                          className="w-24"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeStylistOverride(stylistId)}
                        >
                          <TrashIcon size={16} />
                        </Button>
                      </>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          setStylistOverride(stylistId, defaultRate)
                        }
                      >
                        Add Override
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>

            <p className="text-xs text-muted-foreground mt-2">
              Set custom commission rates for specific stylists
            </p>
          </div>
        )}

        {/* Commission Summary */}
        <div className="bg-muted/50 p-4 rounded-lg">
          <h4 className="font-medium text-foreground mb-2">
            Commission Summary
          </h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>
              • Type:{" "}
              {commissionType === "percentage" ? "Percentage" : "Fixed Amount"}
            </li>
            <li>
              • Default Rate: {defaultRate}
              {commissionType === "percentage" ? "%" : " ₦"}
            </li>
            <li>
              • Default Commission: ₦
              {calculateCommission(defaultRate).toLocaleString()}
            </li>
            {Object.keys(stylistOverrides).length > 0 && (
              <li>
                • {Object.keys(stylistOverrides).length} stylist override(s)
                configured
              </li>
            )}
          </ul>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="flex-1"
          >
            {saveMutation.isPending ? (
              <>
                <Spinner size="sm" />
                Saving...
              </>
            ) : (
              "Save Commission Structure"
            )}
          </Button>
          <Button variant="outline" onClick={handleReset}>
            Reset
          </Button>
        </div>
      </div>
    </Card>
  );
}
