import { useState } from "react";
import { useGetTaxRates } from "@/lib/api/hooks/useAccounting";
import {
  TaxRateList,
  TaxRateFormModal,
  TaxReport,
} from "@/components/accounting";
import { PercentIcon, PlusIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { TaxRate } from "@/lib/api/hooks/useAccounting";

export default function TaxConfigurationPage() {
  const { data: taxRates = [], isLoading } = useGetTaxRates(false); // Include inactive rates
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedTaxRate, setSelectedTaxRate] = useState<TaxRate | null>(null);

  const handleEdit = (taxRate: TaxRate) => {
    setSelectedTaxRate(taxRate);
    setIsFormOpen(true);
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
            <PercentIcon size={32} className="text-[var(--primary)]" />
            Tax Configuration
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Manage tax rates and generate tax reports
          </p>
        </div>
      </div>

      <Tabs defaultValue="tax-rates" className="space-y-6">
        <TabsList>
          <TabsTrigger value="tax-rates">Tax Rates</TabsTrigger>
          <TabsTrigger value="reports">Tax Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="tax-rates" className="space-y-4">
          <div className="flex justify-end">
            <Button
              onClick={() => {
                setSelectedTaxRate(null);
                setIsFormOpen(true);
              }}
            >
              <PlusIcon size={20} />
              Add Tax Rate
            </Button>
          </div>
          <Card className="p-6">
            <TaxRateList taxRates={taxRates} onEdit={handleEdit} />
          </Card>
        </TabsContent>

        <TabsContent value="reports">
          <TaxReport />
        </TabsContent>
      </Tabs>

      <TaxRateFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedTaxRate(null);
        }}
        taxRate={selectedTaxRate}
      />
    </div>
  );
}