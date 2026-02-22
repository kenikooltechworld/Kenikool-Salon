import { useState } from "react";
import {
  useSalesReport,
  useRevenueReport,
  useInventoryReport,
  usePaymentReport,
  useExportReport,
} from "@/hooks/usePOSReports";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";

export default function POSReports() {
  const [activeTab, setActiveTab] = useState("sales");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const { data: salesReport, isLoading: salesLoading } = useSalesReport({
    startDate,
    endDate,
  });
  const { data: revenueReport, isLoading: revenueLoading } = useRevenueReport({
    startDate,
    endDate,
  });
  const { data: inventoryReport, isLoading: inventoryLoading } =
    useInventoryReport();
  const { data: paymentReport, isLoading: paymentLoading } = usePaymentReport({
    startDate,
    endDate,
  });
  const { mutate: exportReport } = useExportReport();

  const handleExport = (format: "pdf" | "csv" | "excel") => {
    exportReport({
      reportType: activeTab as any,
      format,
    });
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Date Filters */}
      <Card className="p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold mb-4">Filters</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
          <div>
            <Label htmlFor="start-date" className="text-sm">
              Start Date
            </Label>
            <Input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="text-sm"
            />
          </div>
          <div>
            <Label htmlFor="end-date" className="text-sm">
              End Date
            </Label>
            <Input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="text-sm"
            />
          </div>
          <div className="flex items-end">
            <Button
              onClick={() => {
                setStartDate("");
                setEndDate("");
              }}
              className="w-full text-sm"
            >
              Clear
            </Button>
          </div>
        </div>
      </Card>

      {/* Reports Tabs */}
      <div className="flex gap-1 md:gap-2 mb-6 border-b border-border overflow-x-auto">
        <Button
          variant={activeTab === "sales" ? "primary" : "ghost"}
          onClick={() => setActiveTab("sales")}
          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary whitespace-nowrap text-sm md:text-base"
        >
          Sales
        </Button>
        <Button
          variant={activeTab === "revenue" ? "primary" : "ghost"}
          onClick={() => setActiveTab("revenue")}
          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary whitespace-nowrap text-sm md:text-base"
        >
          Revenue
        </Button>
        <Button
          variant={activeTab === "inventory" ? "primary" : "ghost"}
          onClick={() => setActiveTab("inventory")}
          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary whitespace-nowrap text-sm md:text-base"
        >
          Inventory
        </Button>
        <Button
          variant={activeTab === "payments" ? "primary" : "ghost"}
          onClick={() => setActiveTab("payments")}
          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary whitespace-nowrap text-sm md:text-base"
        >
          Payments
        </Button>
      </div>

      {/* Sales Report */}
      {activeTab === "sales" && (
        <Card className="p-4 md:p-6">
          {salesLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : salesReport ? (
            <div className="space-y-4">
              <h3 className="text-base md:text-lg font-semibold text-foreground">
                Sales Report
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Total Sales
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    ₦{(salesReport.totalSales || 0).toLocaleString("en-NG")}
                  </p>
                </div>
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Transactions
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    {salesReport.totalTransactions || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Average
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    ₦
                    {(salesReport.averageTransaction || 0).toLocaleString(
                      "en-NG",
                    )}
                  </p>
                </div>
              </div>
              <div className="flex gap-2 mt-4 flex-col sm:flex-row">
                <Button
                  onClick={() => handleExport("pdf")}
                  className="flex-1 text-sm"
                >
                  Export PDF
                </Button>
                <Button
                  onClick={() => handleExport("csv")}
                  className="flex-1 text-sm"
                >
                  Export CSV
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No sales data available</p>
          )}
        </Card>
      )}

      {/* Revenue Report */}
      {activeTab === "revenue" && (
        <Card className="p-4 md:p-6">
          {revenueLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : revenueReport ? (
            <div className="space-y-4">
              <h3 className="text-base md:text-lg font-semibold text-foreground">
                Revenue Report
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Total Revenue
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    ₦{(revenueReport.totalRevenue || 0).toLocaleString("en-NG")}
                  </p>
                </div>
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Discounts
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    ₦
                    {(revenueReport.totalDiscount || 0).toLocaleString("en-NG")}
                  </p>
                </div>
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Net Revenue
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    ₦{(revenueReport.netRevenue || 0).toLocaleString("en-NG")}
                  </p>
                </div>
              </div>
              <div className="flex gap-2 mt-4 flex-col sm:flex-row">
                <Button
                  onClick={() => handleExport("pdf")}
                  className="flex-1 text-sm"
                >
                  Export PDF
                </Button>
                <Button
                  onClick={() => handleExport("csv")}
                  className="flex-1 text-sm"
                >
                  Export CSV
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No revenue data available</p>
          )}
        </Card>
      )}

      {/* Inventory Report */}
      {activeTab === "inventory" && (
        <Card className="p-4 md:p-6">
          {inventoryLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : inventoryReport ? (
            <div className="space-y-4">
              <h3 className="text-base md:text-lg font-semibold text-foreground">
                Inventory Report
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Total Items
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    {inventoryReport.totalItems || 0}
                  </p>
                </div>
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Low Stock Items
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-warning">
                    {inventoryReport.lowStockCount || 0}
                  </p>
                </div>
              </div>
              {inventoryReport.lowStockItems &&
                inventoryReport.lowStockItems.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2 text-foreground text-sm md:text-base">
                      Low Stock Details
                    </h4>
                    <div className="space-y-2">
                      {inventoryReport.lowStockItems.map((item) => (
                        <div
                          key={item.productId}
                          className="text-xs md:text-sm text-muted-foreground"
                        >
                          <p>Product: {item.productId}</p>
                          <p>
                            On Hand: {item.quantityOnHand} | Reorder Point:{" "}
                            {item.reorderPoint}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              <div className="flex gap-2 mt-4 flex-col sm:flex-row">
                <Button
                  onClick={() => handleExport("pdf")}
                  className="flex-1 text-sm"
                >
                  Export PDF
                </Button>
                <Button
                  onClick={() => handleExport("csv")}
                  className="flex-1 text-sm"
                >
                  Export CSV
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No inventory data available</p>
          )}
        </Card>
      )}

      {/* Payments Report */}
      {activeTab === "payments" && (
        <Card className="p-4 md:p-6">
          {paymentLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : paymentReport ? (
            <div className="space-y-4">
              <h3 className="text-base md:text-lg font-semibold text-foreground">
                Payments Report
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
                <div>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    Total Transactions
                  </p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">
                    {paymentReport.totalTransactions || 0}
                  </p>
                </div>
              </div>
              {paymentReport.paymentMethods &&
                Object.keys(paymentReport.paymentMethods).length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2 text-foreground text-sm md:text-base">
                      Payment Methods
                    </h4>
                    <div className="space-y-2">
                      {Object.entries(paymentReport.paymentMethods).map(
                        ([method, data]) => (
                          <div
                            key={method}
                            className="text-xs md:text-sm text-muted-foreground"
                          >
                            <p className="font-medium text-foreground">
                              {method}
                            </p>
                            <p>
                              Count: {data.count} | Total: ₦
                              {data.total.toLocaleString("en-NG")}
                            </p>
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                )}
              <div className="flex gap-2 mt-4 flex-col sm:flex-row">
                <Button
                  onClick={() => handleExport("pdf")}
                  className="flex-1 text-sm"
                >
                  Export PDF
                </Button>
                <Button
                  onClick={() => handleExport("csv")}
                  className="flex-1 text-sm"
                >
                  Export CSV
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">No payment data available</p>
          )}
        </Card>
      )}
    </div>
  );
}
