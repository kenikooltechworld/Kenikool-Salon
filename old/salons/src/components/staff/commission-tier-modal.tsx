"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CommissionTier {
  min_revenue: number;
  commission_rate: number;
}

interface CommissionTierModalProps {
  staffId: string;
  staffName: string;
  isOpen: boolean;
  onClose: () => void;
  onTiersUpdated?: () => void;
}

export function CommissionTierModal({
  staffId,
  staffName,
  isOpen,
  onClose,
  onTiersUpdated,
}: CommissionTierModalProps) {
  const [tiers, setTiers] = useState<CommissionTier[]>([
    { min_revenue: 0, commission_rate: 10 },
    { min_revenue: 5000, commission_rate: 12 },
    { min_revenue: 10000, commission_rate: 15 },
  ]);

  // Fetch existing tiers
  useQuery({
    queryKey: ["commission-tiers", staffId],
    queryFn: async () => {
      const res = await fetch(`/api/staff/commissions/${staffId}/tiers`);
      if (!res.ok) throw new Error("Failed to fetch tiers");
      const data = await res.json();
      if (data.data && data.data.length > 0) {
        setTiers(data.data);
      }
      return data;
    },
  });

  const updateTiersMutation = useMutation({
    mutationFn: async () => {
      if (tiers.length === 0) {
        throw new Error("At least one tier is required");
      }

      const res = await fetch(`/api/staff/commissions/${staffId}/tiers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tiers),
      });

      if (!res.ok) throw new Error("Failed to update tiers");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Commission tiers updated");
      onTiersUpdated?.();
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to update tiers");
    },
  });

  const addTier = () => {
    const newTier: CommissionTier = {
      min_revenue:
        tiers.length > 0 ? tiers[tiers.length - 1].min_revenue + 5000 : 0,
      commission_rate: 10,
    };
    setTiers([...tiers, newTier]);
  };

  const removeTier = (index: number) => {
    if (tiers.length > 1) {
      setTiers(tiers.filter((_, i) => i !== index));
    }
  };

  const updateTier = (
    index: number,
    field: keyof CommissionTier,
    value: number,
  ) => {
    const updated = [...tiers];
    updated[index][field] = value;
    setTiers(updated);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Commission Tiers - {staffName}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Tiers Table */}
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Min Revenue</TableHead>
                  <TableHead>Commission Rate</TableHead>
                  <TableHead className="w-20">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tiers.map((tier, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="text-sm">$</span>
                        <Input
                          type="number"
                          value={tier.min_revenue}
                          onChange={(e) =>
                            updateTier(
                              index,
                              "min_revenue",
                              parseFloat(e.target.value),
                            )
                          }
                          className="w-24"
                          min="0"
                          step="100"
                        />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Input
                          type="number"
                          value={tier.commission_rate}
                          onChange={(e) =>
                            updateTier(
                              index,
                              "commission_rate",
                              parseFloat(e.target.value),
                            )
                          }
                          className="w-24"
                          min="0"
                          max="100"
                          step="0.1"
                        />
                        <span className="text-sm">%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeTier(index)}
                        disabled={tiers.length === 1}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Add Tier Button */}
          <Button onClick={addTier} variant="outline" className="w-full">
            + Add Tier
          </Button>

          {/* Example */}
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Example</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-blue-900">
              <p>
                If a staff member generates $7,500 in revenue, they would earn
                12% commission (the tier for $5,000+).
              </p>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => updateTiersMutation.mutate()}
            disabled={updateTiersMutation.isPending}
          >
            {updateTiersMutation.isPending ? "Saving..." : "Save Tiers"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
