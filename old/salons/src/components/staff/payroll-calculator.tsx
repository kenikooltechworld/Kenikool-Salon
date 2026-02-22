import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { DollarSign, Calculator } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface PayrollRecord {
  _id: string;
  regular_hours: number;
  overtime_hours: number;
  hourly_rate: number;
  gross_pay_hours: number;
  commission_earnings: number;
  bonuses: number;
  gross_pay_total: number;
  tax_withholding: number;
  other_deductions: number;
  net_pay: number;
  payment_status: string;
  pay_period_start: string;
  pay_period_end: string;
}

interface PayrollCalculatorProps {
  staffId: string;
  staffName: string;
  onCalculate?: (payPeriodStart: string, payPeriodEnd: string) => Promise<void>;
}

export const PayrollCalculator: React.FC<PayrollCalculatorProps> = ({
  staffId,
  staffName,
  onCalculate,
}) => {
  const { showToast } = useToast();
  const [payPeriodStart, setPayPeriodStart] = useState("");
  const [payPeriodEnd, setPayPeriodEnd] = useState("");
  const [payroll, setPayroll] = useState<PayrollRecord | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    if (!payPeriodStart || !payPeriodEnd) {
      showToast({
        title: "Validation Error",
        description: "Please select both start and end dates",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      if (onCalculate) {
        await onCalculate(payPeriodStart, payPeriodEnd);
      }
      await fetchPayroll();
    } catch (error) {
      console.error("Failed to calculate payroll:", error);
      showToast({
        title: "Error",
        description: "Failed to calculate payroll",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchPayroll = async () => {
    try {
      const response = await fetch(`/api/staff/payroll/${staffId}`);
      const data = await response.json();
      if (data.payroll_records && data.payroll_records.length > 0) {
        setPayroll(data.payroll_records[0]);
      }
    } catch (error) {
      console.error("Failed to fetch payroll:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid":
        return "bg-green-100 text-green-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="w-5 h-5" />
          Payroll Calculator
        </CardTitle>
        <p className="text-sm text-slate-500 mt-1">{staffName}</p>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Pay Period Start
            </label>
            <Input
              type="date"
              value={payPeriodStart}
              onChange={(e) => setPayPeriodStart(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Pay Period End
            </label>
            <Input
              type="date"
              value={payPeriodEnd}
              onChange={(e) => setPayPeriodEnd(e.target.value)}
            />
          </div>
        </div>

        <Button onClick={handleCalculate} disabled={loading} className="w-full">
          <Calculator className="w-4 h-4 mr-2" />
          Calculate Payroll
        </Button>

        {payroll && (
          <div className="space-y-4 border-t pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Status</span>
              <Badge className={getStatusColor(payroll.payment_status)}>
                {payroll.payment_status.charAt(0).toUpperCase() +
                  payroll.payment_status.slice(1)}
              </Badge>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-600 mb-1">Regular Hours</p>
                <p className="text-lg font-semibold">
                  {payroll.regular_hours.toFixed(1)}h
                </p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-600 mb-1">Overtime Hours</p>
                <p className="text-lg font-semibold">
                  {payroll.overtime_hours.toFixed(1)}h
                </p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-600 mb-1">Hourly Rate</p>
                <p className="text-lg font-semibold">
                  ${payroll.hourly_rate.toFixed(2)}
                </p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-600 mb-1">Commission</p>
                <p className="text-lg font-semibold">
                  ${payroll.commission_earnings.toFixed(2)}
                </p>
              </div>
            </div>

            <div className="border-t pt-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Gross Pay (Hours)</span>
                <span className="font-medium">
                  ${payroll.gross_pay_hours.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Commission Earnings</span>
                <span className="font-medium">
                  ${payroll.commission_earnings.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Bonuses</span>
                <span className="font-medium">
                  ${payroll.bonuses.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between bg-blue-50 p-2 rounded">
                <span className="text-sm font-medium">Gross Total</span>
                <span className="font-semibold text-blue-900">
                  ${payroll.gross_pay_total.toFixed(2)}
                </span>
              </div>
            </div>

            <div className="border-t pt-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Tax Withholding</span>
                <span className="font-medium text-red-600">
                  -${payroll.tax_withholding.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Other Deductions</span>
                <span className="font-medium text-red-600">
                  -${payroll.other_deductions.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between bg-green-50 p-2 rounded">
                <span className="text-sm font-medium">Net Pay</span>
                <span className="font-semibold text-green-900 flex items-center gap-1">
                  <DollarSign className="w-4 h-4" />
                  {payroll.net_pay.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
