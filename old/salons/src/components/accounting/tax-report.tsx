import { useState } from "react";
import {
  useGenerateTaxReport,
  useGetTaxRates,
  TaxReport as TaxReportType,
} from "@/lib/api/hooks/useAccounting";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { PercentIcon, ImageIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

export function TaxReport() {
  const generateReportMutation = useGenerateTaxReport();
  const { data: taxRates = [] } = useGetTaxRates();
  const [reportData, setReportData] = useState<TaxReportType | null>(null);
  const [formData, setFormData] = useState({
    start_date: new Date(new Date().getFullYear(), 0, 1)
      .toISOString()
      .split("T")[0], // Start of year
    end_date: new Date().toISOString().split("T")[0], // Today
    tax_rate_id: "",
  });

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const report = await generateReportMutation.mutateAsync({
        start_date: formData.start_date,
        end_date: formData.end_date,
        tax_rate_id: formData.tax_rate_id || undefined,
      });
      setReportData(report);
      showToast("Tax report generated successfully", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to generate tax report",
        "error",
      );
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ImageIcon size={20} />
          Generate Tax Report
        </h3>

        <form onSubmit={handleGenerateReport} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date">Start Date</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="end_date">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date}
                onChange={(e) =>
                  setFormData({ ...formData, end_date: e.target.value })
                }
                required
              />
            </div>
          </div>

          <div>
            <Label htmlFor="tax_rate_id">Tax Rate (Optional)</Label>
            <Select
              id="tax_rate_id"
              value={formData.tax_rate_id}
              onChange={(e) =>
                setFormData({ ...formData, tax_rate_id: e.target.value })
              }
            >
              <option value="">All Tax Rates</option>
              {taxRates.map((taxRate) => (
                <option key={taxRate.id} value={taxRate.id}>
                  {taxRate.name} ({taxRate.rate}%)
                </option>
              ))}
            </Select>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={generateReportMutation.isPending}
          >
            {generateReportMutation.isPending ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Generating Report...
              </>
            ) : (
              "Generate Report"
            )}
          </Button>
        </form>
      </Card>

      {reportData && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <PercentIcon size={20} />
            Tax Report Results
          </h3>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 p-4 bg-[var(--muted)] rounded-[var(--radius-md)]">
              <div>
                <p className="text-sm text-[var(--muted-foreground)]">Period</p>
                <p className="font-semibold">
                  {new Date(reportData.period_start).toLocaleDateString()} -{" "}
                  {new Date(reportData.period_end).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-[var(--muted-foreground)]">
                  Total Invoices
                </p>
                <p className="font-semibold">{reportData.invoice_count}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Card className="p-4">
                <p className="text-sm text-[var(--muted-foreground)]">
                  Total Taxable Amount
                </p>
                <p className="text-2xl font-bold text-[var(--primary)]">
                  ₦{reportData.total_taxable_amount.toFixed(2)}
                </p>
              </Card>
              <Card className="p-4">
                <p className="text-sm text-[var(--muted-foreground)]">
                  Total Tax Collected
                </p>
                <p className="text-2xl font-bold">
                  ₦{reportData.total_tax_collected.toFixed(2)}
                </p>
              </Card>
            </div>

            {reportData.breakdown.length > 0 && (
              <div>
                <h4 className="font-semibold mb-3">Breakdown by Tax Rate</h4>
                <div className="space-y-2">
                  {reportData.breakdown.map((item, index) => (
                    <Card key={index} className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold">{item.tax_rate_name}</p>
                          <p className="text-sm text-[var(--muted-foreground)]">
                            {item.invoice_count} invoices
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold">
                            ₦{item.taxable_amount.toFixed(2)}
                          </p>
                          <p className="text-sm">
                            Tax: ₦{item.tax_collected.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
