import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Download, Printer, DollarSign } from "lucide-react";

interface PayStub {
  _id: string;
  staff_id: string;
  pay_period_start: string;
  pay_period_end: string;
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
  payment_date?: string;
  payment_method?: string;
  payment_status: string;
}

interface PayStubViewerProps {
  staffId: string;
  staffName: string;
}

export const PayStubViewer: React.FC<PayStubViewerProps> = ({
  staffId,
  staffName,
}) => {
  const [payStubs, setPayStubs] = useState<PayStub[]>([]);
  const [selectedStub, setSelectedStub] = useState<PayStub | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayStubs();
  }, [staffId]);

  const fetchPayStubs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/staff/payroll/${staffId}`);
      const data = await response.json();
      setPayStubs(data.payroll_records || []);
      if (data.payroll_records && data.payroll_records.length > 0) {
        setSelectedStub(data.payroll_records[0]);
      }
    } catch (error) {
      console.error("Failed to fetch pay stubs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    if (!selectedStub) return;
    window.print();
  };

  const handleDownload = () => {
    if (!selectedStub) return;
    const csv = generateCSV(selectedStub);
    const element = document.createElement("a");
    element.setAttribute(
      "href",
      "data:text/plain;charset=utf-8," + encodeURIComponent(csv),
    );
    element.setAttribute(
      "download",
      `pay-stub-${selectedStub.pay_period_start}.csv`,
    );
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const generateCSV = (stub: PayStub): string => {
    return `Pay Stub
Staff: ${staffName}
Pay Period: ${new Date(stub.pay_period_start).toLocaleDateString()} - ${new Date(stub.pay_period_end).toLocaleDateString()}

EARNINGS
Regular Hours,${stub.regular_hours.toFixed(1)}
Overtime Hours,${stub.overtime_hours.toFixed(1)}
Hourly Rate,$${stub.hourly_rate.toFixed(2)}
Gross Pay (Hours),$${stub.gross_pay_hours.toFixed(2)}
Commission Earnings,$${stub.commission_earnings.toFixed(2)}
Bonuses,$${stub.bonuses.toFixed(2)}
Gross Total,$${stub.gross_pay_total.toFixed(2)}

DEDUCTIONS
Tax Withholding,$${stub.tax_withholding.toFixed(2)}
Other Deductions,$${stub.other_deductions.toFixed(2)}

NET PAY
Net Pay,$${stub.net_pay.toFixed(2)}

PAYMENT INFO
Status,${stub.payment_status}
Payment Date,${stub.payment_date || "Pending"}
Payment Method,${stub.payment_method || "N/A"}`;
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

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-slate-500">Loading pay stubs...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle className="text-lg">Pay Stubs</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-96">
            <div className="space-y-2 pr-4">
              {payStubs.length === 0 ? (
                <p className="text-center text-slate-500 py-8">
                  No pay stubs found
                </p>
              ) : (
                payStubs.map((stub) => (
                  <button
                    key={stub._id}
                    onClick={() => setSelectedStub(stub)}
                    className={`w-full text-left p-2 rounded-lg transition ${
                      selectedStub?._id === stub._id
                        ? "bg-blue-100 border border-blue-300"
                        : "hover:bg-slate-100 border border-slate-200"
                    }`}
                  >
                    <p className="text-sm font-medium">
                      {new Date(stub.pay_period_start).toLocaleDateString()} -{" "}
                      {new Date(stub.pay_period_end).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-slate-600 mt-1">
                      ${stub.net_pay.toFixed(2)}
                    </p>
                    <Badge variant="outline" className="text-xs mt-1">
                      {stub.payment_status}
                    </Badge>
                  </button>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Pay Stub Details</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrint}
              disabled={!selectedStub}
            >
              <Printer className="w-4 h-4 mr-1" />
              Print
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              disabled={!selectedStub}
            >
              <Download className="w-4 h-4 mr-1" />
              Download
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          {selectedStub ? (
            <div className="space-y-6">
              <div className="border-b pb-4">
                <h3 className="font-semibold text-lg">{staffName}</h3>
                <p className="text-sm text-slate-600">
                  Pay Period:{" "}
                  {new Date(selectedStub.pay_period_start).toLocaleDateString()}{" "}
                  - {new Date(selectedStub.pay_period_end).toLocaleDateString()}
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-sm mb-3">Earnings</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Regular Hours</span>
                      <span>{selectedStub.regular_hours.toFixed(1)} hrs</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Overtime Hours</span>
                      <span>{selectedStub.overtime_hours.toFixed(1)} hrs</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Hourly Rate</span>
                      <span>${selectedStub.hourly_rate.toFixed(2)}</span>
                    </div>
                    <div className="border-t pt-2 flex justify-between font-medium">
                      <span>Gross Pay (Hours)</span>
                      <span>${selectedStub.gross_pay_hours.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Commission Earnings</span>
                      <span>
                        ${selectedStub.commission_earnings.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Bonuses</span>
                      <span>${selectedStub.bonuses.toFixed(2)}</span>
                    </div>
                    <div className="bg-blue-50 p-2 rounded flex justify-between font-semibold">
                      <span>Gross Total</span>
                      <span>${selectedStub.gross_pay_total.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-sm mb-3">Deductions</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between text-red-600">
                      <span>Tax Withholding</span>
                      <span>-${selectedStub.tax_withholding.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-red-600">
                      <span>Other Deductions</span>
                      <span>-${selectedStub.other_deductions.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-700">Net Pay</p>
                      <p className="text-2xl font-bold text-green-900 flex items-center gap-1 mt-1">
                        <DollarSign className="w-6 h-6" />
                        {selectedStub.net_pay.toFixed(2)}
                      </p>
                    </div>
                    <Badge
                      className={getStatusColor(selectedStub.payment_status)}
                    >
                      {selectedStub.payment_status.charAt(0).toUpperCase() +
                        selectedStub.payment_status.slice(1)}
                    </Badge>
                  </div>
                </div>

                {selectedStub.payment_date && (
                  <div className="border-t pt-4 text-sm">
                    <p className="text-slate-600">
                      Payment Date:{" "}
                      {new Date(selectedStub.payment_date).toLocaleDateString()}
                    </p>
                    {selectedStub.payment_method && (
                      <p className="text-slate-600">
                        Payment Method: {selectedStub.payment_method}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <p className="text-center text-slate-500 py-8">
              Select a pay stub to view details
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
