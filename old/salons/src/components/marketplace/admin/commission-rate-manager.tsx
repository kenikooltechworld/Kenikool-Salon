import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  useUpdateCommissionRates,
  useSalons,
} from "@/lib/api/hooks/useMarketplaceQueries";
import { EditIcon, CheckIcon, XIcon } from "@/components/icons";

interface SalonRate {
  tenantId: string;
  salonName: string;
  currentRate: number;
  referralRate: number;
  newRate?: number;
  newReferralRate?: number;
}

export function CommissionRateManager() {
  const { data: salons = [], isLoading: salonsLoading } = useSalons();
  const updateRatesMutation = useUpdateCommissionRates();

  const [editingSalon, setEditingSalon] = useState<string | null>(null);
  const [rates, setRates] = useState<Record<string, SalonRate>>({});

  const handleEditSalon = (salon: any) => {
    setEditingSalon(salon.id);
    setRates((prev) => ({
      ...prev,
      [salon.id]: {
        tenantId: salon.id,
        salonName: salon.name,
        currentRate: salon.commission_rate || 10,
        referralRate: salon.referral_commission_rate || 5,
      },
    }));
  };

  const handleRateChange = (
    salonId: string,
    field: "newRate" | "newReferralRate",
    value: number,
  ) => {
    setRates((prev) => ({
      ...prev,
      [salonId]: {
        ...prev[salonId],
        [field]: value,
      },
    }));
  };

  const handleSaveRates = async (salonId: string) => {
    const salonRates = rates[salonId];
    if (!salonRates) return;

    try {
      await updateRatesMutation.mutateAsync({
        tenantId: salonId,
        commissionRate: salonRates.newRate || salonRates.currentRate,
        referralCommissionRate:
          salonRates.newReferralRate || salonRates.referralRate,
      });
      setEditingSalon(null);
    } catch (error) {
      console.error("Error updating rates:", error);
    }
  };

  const handleCancel = () => {
    setEditingSalon(null);
    setRates({});
  };

  if (salonsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary)] mx-auto mb-4"></div>
          <p className="text-[var(--muted-foreground)]">Loading salons...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Info Box */}
      <motion.div
        className="bg-blue-50 border border-blue-200 p-4 rounded-lg"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <p className="text-sm text-blue-800">
          <span className="font-semibold">ℹ️ Commission Rates:</span> Set
          different commission rates for each salon. The marketplace commission
          is deducted from the booking amount before payment to the salon.
        </p>
      </motion.div>

      {/* Salons Grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, staggerChildren: 0.1 }}
      >
        {salons.map((salon: any, index: number) => {
          const isEditing = editingSalon === salon.id;
          const salonRates = rates[salon.id] || {
            tenantId: salon.id,
            salonName: salon.name,
            currentRate: salon.commission_rate || 10,
            referralRate: salon.referral_commission_rate || 5,
          };

          return (
            <motion.div
              key={salon.id}
              className="bg-white rounded-lg border border-[var(--border)] p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <div className="space-y-4">
                {/* Salon Name */}
                <div>
                  <h3 className="font-semibold text-[var(--foreground)]">
                    {salon.name}
                  </h3>
                  <p className="text-xs text-[var(--muted-foreground)] mt-1">
                    ID: {salon.id}
                  </p>
                </div>

                {/* Commission Rate */}
                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                    Marketplace Commission Rate
                  </label>
                  {isEditing ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.1"
                        value={salonRates.newRate || salonRates.currentRate}
                        onChange={(e) =>
                          handleRateChange(
                            salon.id,
                            "newRate",
                            parseFloat(e.target.value),
                          )
                        }
                        className="flex-1 px-3 py-2 rounded-lg border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none"
                      />
                      <span className="text-sm font-medium">%</span>
                    </div>
                  ) : (
                    <div className="bg-[var(--muted)] p-3 rounded-lg">
                      <p className="text-lg font-bold text-[var(--primary)]">
                        {salonRates.currentRate}%
                      </p>
                    </div>
                  )}
                </div>

                {/* Referral Rate */}
                <div>
                  <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                    Referral Commission Rate
                  </label>
                  {isEditing ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.1"
                        value={
                          salonRates.newReferralRate || salonRates.referralRate
                        }
                        onChange={(e) =>
                          handleRateChange(
                            salon.id,
                            "newReferralRate",
                            parseFloat(e.target.value),
                          )
                        }
                        className="flex-1 px-3 py-2 rounded-lg border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none"
                      />
                      <span className="text-sm font-medium">%</span>
                    </div>
                  ) : (
                    <div className="bg-[var(--muted)] p-3 rounded-lg">
                      <p className="text-lg font-bold text-[var(--primary)]">
                        {salonRates.referralRate}%
                      </p>
                    </div>
                  )}
                </div>

                {/* Example Calculation */}
                <div className="bg-[var(--muted)] p-3 rounded-lg text-xs text-[var(--muted-foreground)]">
                  <p className="mb-1">
                    <span className="font-semibold">Example:</span> ₦10,000
                    booking
                  </p>
                  <p>
                    Commission: ₦
                    {(
                      10000 *
                      ((salonRates.newRate || salonRates.currentRate) / 100)
                    ).toLocaleString()}
                  </p>
                  <p>
                    Salon receives: ₦
                    {(
                      10000 -
                      10000 *
                        ((salonRates.newRate || salonRates.currentRate) / 100)
                    ).toLocaleString()}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  {isEditing ? (
                    <>
                      <Button
                        onClick={() => handleSaveRates(salon.id)}
                        disabled={updateRatesMutation.isPending}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white flex items-center justify-center gap-2"
                      >
                        <CheckIcon size={16} />
                        Save
                      </Button>
                      <Button
                        onClick={handleCancel}
                        variant="outline"
                        className="flex-1 flex items-center justify-center gap-2"
                      >
                        <XIcon size={16} />
                        Cancel
                      </Button>
                    </>
                  ) : (
                    <Button
                      onClick={() => handleEditSalon(salon)}
                      variant="outline"
                      className="w-full flex items-center justify-center gap-2"
                    >
                      <EditIcon size={16} />
                      Edit Rates
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {salons.length === 0 && (
        <motion.div
          className="text-center py-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-[var(--muted-foreground)]">No salons found</p>
        </motion.div>
      )}
    </div>
  );
}
