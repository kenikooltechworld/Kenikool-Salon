import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function BulkOperations() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<"import" | "export" | "update">("import");

  // Import
  const [importFile, setImportFile] = useState<File | null>(null);
  const importMutation = useMutation({
    mutationFn: async () => {
      if (!importFile) throw new Error("No file selected");
      const formData = new FormData();
      formData.append("file", importFile);
      const res = await apiClient.post("/api/inventory/bulk/import", formData);
      return res.data;
    },
    onSuccess: (data) => {
      toast(`Imported ${data.success_count} products successfully`, "success");
      if (data.errors.length > 0) {
        toast(`${data.error_count} errors occurred`, "error");
      }
      setImportFile(null);
    },
    onError: (error: any) => {
      toast(error.response?.data?.detail || "Import failed", "error");
    },
  });

  // Export
  const exportMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post("/api/inventory/bulk/export");
      return res.data;
    },
    onSuccess: (data) => {
      const element = document.createElement("a");
      element.setAttribute(
        "href",
        "data:text/csv;charset=utf-8," + encodeURIComponent(data.csv)
      );
      element.setAttribute("download", data.filename);
      element.style.display = "none";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      toast("Products exported successfully", "success");
    },
    onError: (error: any) => {
      toast(error.response?.data?.detail || "Export failed", "error");
    },
  });

  // Update Prices
  const [priceAdjustmentType, setPriceAdjustmentType] = useState<"percentage" | "fixed">("percentage");
  const [priceAdjustmentValue, setPriceAdjustmentValue] = useState(0);
  const [priceCategory, setPriceCategory] = useState("");

  const updatePricesMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post("/api/inventory/bulk/update-prices", {
        adjustment_type: priceAdjustmentType,
        adjustment_value: priceAdjustmentValue,
        category: priceCategory || undefined,
      });
      return res.data;
    },
    onSuccess: (data) => {
      toast(`Updated prices for ${data.updated_count} products`, "success");
      setPriceAdjustmentValue(0);
      setPriceCategory("");
    },
    onError: (error: any) => {
      toast(error.response?.data?.detail || "Price update failed", "error");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex gap-2 border-b border-[var(--border)]">
        <Button
          variant={activeTab === "import" ? "primary" : "ghost"}
          onClick={() => setActiveTab("import")}
        >
          Import
        </Button>
        <Button
          variant={activeTab === "export" ? "primary" : "ghost"}
          onClick={() => setActiveTab("export")}
        >
          Export
        </Button>
        <Button
          variant={activeTab === "update" ? "primary" : "ghost"}
          onClick={() => setActiveTab("update")}
        >
          Update Prices
        </Button>
      </div>

      {/* Import Tab */}
      {activeTab === "import" && (
        <Card>
          <CardHeader>
            <CardTitle>Import Products from CSV</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>CSV File</Label>
              <Input
                type="file"
                accept=".csv"
                onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                className="mt-1"
              />
              <p className="text-xs text-[var(--muted-foreground)] mt-2">
                Required columns: name, sku, category, quantity, unit_price, cost_price
              </p>
            </div>
            <Button
              onClick={() => importMutation.mutate()}
              disabled={!importFile || importMutation.isPending}
            >
              {importMutation.isPending ? "Importing..." : "Import"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Export Tab */}
      {activeTab === "export" && (
        <Card>
          <CardHeader>
            <CardTitle>Export Products to CSV</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-[var(--muted-foreground)] mb-4">
              Download all products as a CSV file for backup or editing.
            </p>
            <Button
              onClick={() => exportMutation.mutate()}
              disabled={exportMutation.isPending}
            >
              {exportMutation.isPending ? "Exporting..." : "Export All Products"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Update Prices Tab */}
      {activeTab === "update" && (
        <Card>
          <CardHeader>
            <CardTitle>Bulk Update Prices</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Adjustment Type</Label>
              <select
                value={priceAdjustmentType}
                onChange={(e) =>
                  setPriceAdjustmentType(e.target.value as "percentage" | "fixed")
                }
                className="w-full mt-1 p-2 border border-[var(--border)] rounded"
              >
                <option value="percentage">Percentage (%)</option>
                <option value="fixed">Fixed Amount (₦)</option>
              </select>
            </div>

            <div>
              <Label>Adjustment Value</Label>
              <Input
                type="number"
                value={priceAdjustmentValue}
                onChange={(e) => setPriceAdjustmentValue(parseFloat(e.target.value) || 0)}
                placeholder={priceAdjustmentType === "percentage" ? "e.g., 10" : "e.g., 100"}
                className="mt-1"
              />
            </div>

            <div>
              <Label>Category (Optional)</Label>
              <Input
                value={priceCategory}
                onChange={(e) => setPriceCategory(e.target.value)}
                placeholder="Leave empty to update all products"
                className="mt-1"
              />
            </div>

            <Button
              onClick={() => updatePricesMutation.mutate()}
              disabled={updatePricesMutation.isPending}
            >
              {updatePricesMutation.isPending ? "Updating..." : "Update Prices"}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
