import { useState } from "react";
import {
  useGetPayrollRecords,
  useGetPayrollExpenseReport,
  useGetTaxWithholdingReport,
} from "@/lib/api/hooks/useAccounting";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";

export default function PayrollIntegrationPage() {
  const [activeTab, setActiveTab] = useState("payroll");
  const [reportDates, setReportDates] = useState({
    start_date: "",
    end_date: "",
  });

  const payrollQuery = useGetPayrollRecords();
  const expenseReportQuery = useGetPayrollExpenseReport(
    reportDates.start_date,
    reportDates.end_date,
  );
  const taxReportQuery = useGetTaxWithholdingReport(
    reportDates.start_date,
    reportDates.end_date,
  );

  const handleLoadReport = () => {
    if (!reportDates.start_date || !reportDates.end_date) {
      showToast("Please select both start and end dates", "warning");
      return;
    }
    expenseReportQuery.refetch();
    taxReportQuery.refetch();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Payroll Integration
        </h1>
        <p className="mt-2">Manage payroll and tax withholding</p>
      </div>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="payroll"
      >
        <TabsList>
          <TabsTrigger value="payroll">Payroll Records</TabsTrigger>
          <TabsTrigger value="expense">Expense Report</TabsTrigger>
          <TabsTrigger value="taxes">Tax Withholding</TabsTrigger>
        </TabsList>

        <TabsContent value="payroll" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Payroll Records</CardTitle>
              <CardDescription>View all payroll records</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-4">Period</th>
                      <th className="text-left py-2 px-4">Date</th>
                      <th className="text-right py-2 px-4">Gross Pay</th>
                      <th className="text-right py-2 px-4">Net Pay</th>
                      <th className="text-right py-2 px-4">Taxes</th>
                      <th className="text-left py-2 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payrollQuery.data?.map((record: any) => (
                      <tr key={record.id} className="border-b">
                        <td className="py-2 px-4 text-xs font-medium">
                          {record.payroll_period}
                        </td>
                        <td className="py-2 px-4 text-xs">
                          {format(
                            new Date(record.payroll_date),
                            "MMM dd, yyyy",
                          )}
                        </td>
                        <td className="py-2 px-4 text-right text-xs font-medium">
                          ${record.total_gross.toFixed(2)}
                        </td>
                        <td className="py-2 px-4 text-right text-xs font-medium">
                          ${record.total_net.toFixed(2)}
                        </td>
                        <td className="py-2 px-4 text-right text-xs font-medium">
                          ${record.total_taxes.toFixed(2)}
                        </td>
                        <td className="py-2 px-4">
                          <Badge
                            variant={record.synced ? "default" : "secondary"}
                          >
                            {record.synced ? "Synced" : "Pending"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {payrollQuery.isLoading && (
                <div className="text-center py-8">
                  Loading payroll records...
                </div>
              )}

              {!payrollQuery.isLoading && payrollQuery.data?.length === 0 && (
                <div className="text-center py-8">No payroll records found</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="expense" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Payroll Expense Report</CardTitle>
              <CardDescription>View payroll expenses by period</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Start Date
                  </label>
                  <Input
                    type="date"
                    value={reportDates.start_date}
                    onChange={(e) =>
                      setReportDates((prev) => ({
                        ...prev,
                        start_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    End Date
                  </label>
                  <Input
                    type="date"
                    value={reportDates.end_date}
                    onChange={(e) =>
                      setReportDates((prev) => ({
                        ...prev,
                        end_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={handleLoadReport}
                    disabled={expenseReportQuery.isLoading}
                    className="w-full"
                  >
                    Load Report
                  </Button>
                </div>
              </div>

              {expenseReportQuery.data && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Total Gross
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          ${expenseReportQuery.data.total_gross.toFixed(2)}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Total Net
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          ${expenseReportQuery.data.total_net.toFixed(2)}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium">
                          Total Taxes
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          ${expenseReportQuery.data.total_taxes.toFixed(2)}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="border-b">
                        <tr>
                          <th className="text-left py-2 px-4">Employee</th>
                          <th className="text-right py-2 px-4">Gross</th>
                          <th className="text-right py-2 px-4">Net</th>
                          <th className="text-right py-2 px-4">Taxes</th>
                          <th className="text-right py-2 px-4">Periods</th>
                        </tr>
                      </thead>
                      <tbody>
                        {expenseReportQuery.data.employee_summary?.map(
                          (emp: any) => (
                            <tr key={emp.employee_id} className="border-b">
                              <td className="py-2 px-4 text-xs font-medium">
                                {emp.employee_name}
                              </td>
                              <td className="py-2 px-4 text-right text-xs">
                                ${emp.total_gross.toFixed(2)}
                              </td>
                              <td className="py-2 px-4 text-right text-xs">
                                ${emp.total_net.toFixed(2)}
                              </td>
                              <td className="py-2 px-4 text-right text-xs">
                                ${emp.total_taxes.toFixed(2)}
                              </td>
                              <td className="py-2 px-4 text-right text-xs">
                                {emp.pay_periods}
                              </td>
                            </tr>
                          ),
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {expenseReportQuery.isLoading && (
                <div className="text-center py-8">Loading report...</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="taxes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Tax Withholding Report</CardTitle>
              <CardDescription>View tax withholding by type</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Start Date
                  </label>
                  <Input
                    type="date"
                    value={reportDates.start_date}
                    onChange={(e) =>
                      setReportDates((prev) => ({
                        ...prev,
                        start_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    End Date
                  </label>
                  <Input
                    type="date"
                    value={reportDates.end_date}
                    onChange={(e) =>
                      setReportDates((prev) => ({
                        ...prev,
                        end_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={handleLoadReport}
                    disabled={taxReportQuery.isLoading}
                    className="w-full"
                  >
                    Load Report
                  </Button>
                </div>
              </div>

              {taxReportQuery.data && (
                <div className="space-y-4">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium">
                        Total Taxes
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">
                        ${taxReportQuery.data.total_taxes.toFixed(2)}
                      </div>
                    </CardContent>
                  </Card>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(taxReportQuery.data.tax_breakdown).map(
                      ([type, amount]) => (
                        <Card key={type}>
                          <CardHeader className="pb-2">
                            <CardTitle className="text-xs font-medium capitalize">
                              {type.replace(/_/g, " ")}
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="text-lg font-bold">
                              ${(amount as number).toFixed(2)}
                            </div>
                          </CardContent>
                        </Card>
                      ),
                    )}
                  </div>
                </div>
              )}

              {taxReportQuery.isLoading && (
                <div className="text-center py-8">Loading report...</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
