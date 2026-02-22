import { useState } from "react";
import { useGetFinancialReport } from "@/lib/api/hooks/useAccounting";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { ChartIcon } from "@/components/icons";

export function FinancialReports() {
  const [reportType, setReportType] = useState("balance_sheet");
  const [startDate, setStartDate] = useState(
    new Date(new Date().getFullYear(), 0, 1).toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [showReport, setShowReport] = useState(false);

  const { data: report, isLoading } = useGetFinancialReport(
    showReport ? reportType : "",
    startDate,
    endDate
  );

  const reportTypes = [
    { value: "balance_sheet", label: "Balance Sheet" },
    { value: "income_statement", label: "Income Statement" },
    { value: "trial_balance", label: "Trial Balance" },
  ];

  const handleGenerate = () => {
    setShowReport(true);
  };

  const renderBalanceSheet = (data: any) => {
    return (
      <div className="space-y-6">
        <div>
          <h4 className="font-semibold text-lg mb-3">Assets</h4>
          <div className="space-y-2">
            {data.assets?.map((account: any, index: number) => (
              <div
                key={index}
                className="flex justify-between p-2 hover:bg-[var(--muted)] rounded"
              >
                <span>{account.name}</span>
                <span className="font-semibold">
                  ₦{account.balance.toFixed(2)}
                </span>
              </div>
            ))}
            <div className="flex justify-between p-2 bg-[var(--muted)] rounded font-bold">
              <span>Total Assets</span>
              <span>₦{data.total_assets?.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="font-semibold text-lg mb-3">Liabilities</h4>
          <div className="space-y-2">
            {data.liabilities?.map((account: any, index: number) => (
              <div
                key={index}
                className="flex justify-between p-2 hover:bg-[var(--muted)] rounded"
              >
                <span>{account.name}</span>
                <span className="font-semibold">
                  ₦{account.balance.toFixed(2)}
                </span>
              </div>
            ))}
            <div className="flex justify-between p-2 bg-[var(--muted)] rounded font-bold">
              <span>Total Liabilities</span>
              <span>₦{data.total_liabilities?.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="font-semibold text-lg mb-3">Equity</h4>
          <div className="space-y-2">
            {data.equity?.map((account: any, index: number) => (
              <div
                key={index}
                className="flex justify-between p-2 hover:bg-[var(--muted)] rounded"
              >
                <span>{account.name}</span>
                <span className="font-semibold">
                  ₦{account.balance.toFixed(2)}
                </span>
              </div>
            ))}
            <div className="flex justify-between p-2 bg-[var(--muted)] rounded font-bold">
              <span>Total Equity</span>
              <span>₦{data.total_equity?.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderIncomeStatement = (data: any) => {
    return (
      <div className="space-y-6">
        <div>
          <h4 className="font-semibold text-lg mb-3">Revenue</h4>
          <div className="space-y-2">
            {data.revenue?.map((account: any, index: number) => (
              <div
                key={index}
                className="flex justify-between p-2 hover:bg-[var(--muted)] rounded"
              >
                <span>{account.name}</span>
                <span className="font-semibold">
                  ₦{account.balance.toFixed(2)}
                </span>
              </div>
            ))}
            <div className="flex justify-between p-2 bg-[var(--muted)] rounded font-bold">
              <span>Total Revenue</span>
              <span>₦{data.total_revenue?.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="font-semibold text-lg mb-3">Expenses</h4>
          <div className="space-y-2">
            {data.expenses?.map((account: any, index: number) => (
              <div
                key={index}
                className="flex justify-between p-2 hover:bg-[var(--muted)] rounded"
              >
                <span>{account.name}</span>
                <span className="font-semibold">
                  ₦{account.balance.toFixed(2)}
                </span>
              </div>
            ))}
            <div className="flex justify-between p-2 bg-[var(--muted)] rounded font-bold">
              <span>Total Expenses</span>
              <span>₦{data.total_expenses?.toFixed(2)}</span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
          <div className="flex justify-between items-center">
            <span className="text-lg font-bold">Net Income</span>
            <span
              className={`text-2xl font-bold`}
            >
              ₦{data.net_income?.toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const renderTrialBalance = (data: any) => {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4 p-3 bg-[var(--muted)] rounded font-semibold">
          <span>Account</span>
          <span className="text-right">Debit</span>
          <span className="text-right">Credit</span>
        </div>
        {data.accounts?.map((account: any, index: number) => (
          <div
            key={index}
            className="grid grid-cols-3 gap-4 p-2 hover:bg-[var(--muted)] rounded"
          >
            <span>{account.name}</span>
            <span className="text-right">
              {account.debit > 0 ? `₦${account.debit.toFixed(2)}` : "-"}
            </span>
            <span className="text-right">
              {account.credit > 0 ? `₦${account.credit.toFixed(2)}` : "-"}
            </span>
          </div>
        ))}
        <div className="grid grid-cols-3 gap-4 p-3 bg-[var(--muted)] rounded font-bold">
          <span>Total</span>
          <span className="text-right">₦{data.total_debit?.toFixed(2)}</span>
          <span className="text-right">₦{data.total_credit?.toFixed(2)}</span>
        </div>
      </div>
    );
  };

  return (
    <Card className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <ChartIcon size={24} className="text-[var(--primary)]" />
        <h3 className="text-lg font-semibold">Financial Reports</h3>
      </div>

      <div className="space-y-4 mb-6">
        <div>
          <Label htmlFor="reportType">Report Type</Label>
          <Select
            id="reportType"
            value={reportType}
            onChange={(e) => {
              setReportType(e.target.value);
              setShowReport(false);
            }}
          >
            {reportTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="startDate">Start Date</Label>
            <Input
              id="startDate"
              type="date"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setShowReport(false);
              }}
            />
          </div>
          <div>
            <Label htmlFor="endDate">End Date</Label>
            <Input
              id="endDate"
              type="date"
              value={endDate}
              onChange={(e) => {
                setEndDate(e.target.value);
                setShowReport(false);
              }}
            />
          </div>
        </div>

        <Button onClick={handleGenerate} className="w-full">
          Generate Report
        </Button>
      </div>

      {showReport && (
        <div className="border-t pt-6">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner size="lg" />
            </div>
          ) : report ? (
            <div>
              <div className="mb-4">
                <h3 className="text-xl font-bold">
                  {reportTypes.find((t) => t.value === reportType)?.label}
                </h3>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {new Date(startDate).toLocaleDateString()} -{" "}
                  {new Date(endDate).toLocaleDateString()}
                </p>
              </div>
              {reportType === "balance_sheet" &&
                renderBalanceSheet(report.data)}
              {reportType === "income_statement" &&
                renderIncomeStatement(report.data)}
              {reportType === "trial_balance" &&
                renderTrialBalance(report.data)}
            </div>
          ) : (
            <p className="text-center text-[var(--muted-foreground)]">
              No data available
            </p>
          )}
        </div>
      )}
    </Card>
  );
}
