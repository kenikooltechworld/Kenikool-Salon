import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useOutstandingBalanceReport } from "@/hooks/useFinancialReport";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { AlertCircleIcon } from "@/components/icons";

export default function CustomerBalance() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const { data: report, isLoading } = useOutstandingBalanceReport();

  const filteredCustomers = (report?.customers || []).filter(
    (customer: any) =>
      !searchTerm ||
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.email.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Customer Balance</h1>
        <Button variant="outline" onClick={() => navigate("/reports")}>
          Back
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading customer balance data...</div>
      ) : report ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Total Outstanding</p>
              <p className="text-3xl font-bold text-destructive mt-2">
                {formatCurrency(report.totalOutstanding || 0)}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">
                Customers with Balance
              </p>
              <p className="text-3xl font-bold mt-2">
                {report.customersWithBalance || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Average Balance</p>
              <p className="text-3xl font-bold mt-2">
                {formatCurrency(
                  (report.totalOutstanding || 0) /
                    (report.customersWithBalance || 1),
                )}
              </p>
            </div>
          </div>

          {/* Warning */}
          {(report.totalOutstanding || 0) > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 flex gap-4">
              <AlertCircleIcon
                size={24}
                className="text-yellow-600 flex-shrink-0"
              />
              <div>
                <h3 className="font-semibold text-yellow-900 mb-1">
                  Outstanding Balances
                </h3>
                <p className="text-sm text-yellow-900">
                  There are {report.customersWithBalance} customers with
                  outstanding balances totaling{" "}
                  {formatCurrency(report.totalOutstanding || 0)}. Customers with
                  outstanding balances cannot book new appointments.
                </p>
              </div>
            </div>
          )}

          {/* Search */}
          <div className="bg-card border border-border rounded-lg p-6">
            <input
              type="text"
              placeholder="Search by customer name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg"
            />
          </div>

          {/* Customers with Balance */}
          <div className="bg-card border border-border rounded-lg p-6">
            <h3 className="font-semibold mb-4">
              Customers with Outstanding Balance
            </h3>

            {filteredCustomers.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted border-b border-border">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Customer
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Email
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Outstanding Balance
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Total Paid
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Last Payment
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {filteredCustomers.map((customer: any, index: number) => (
                      <tr key={index} className="hover:bg-muted/50">
                        <td className="px-4 py-3 text-sm font-medium">
                          {customer.name}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {customer.email}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium text-destructive">
                          {formatCurrency(customer.outstandingBalance)}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {formatCurrency(customer.totalPaid)}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">
                          {customer.lastPaymentDate
                            ? formatDate(customer.lastPaymentDate)
                            : "Never"}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              navigate(`/customers/${customer.customerId}`)
                            }
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-center py-8 text-muted-foreground">
                {searchTerm
                  ? "No customers found matching your search"
                  : "No customers with outstanding balance"}
              </p>
            )}
          </div>

          {/* Payment History */}
          {report.recentPayments && report.recentPayments.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Recent Payments</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted border-b border-border">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Customer
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Amount
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Date
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {report.recentPayments.map(
                      (payment: any, index: number) => (
                        <tr key={index} className="hover:bg-muted/50">
                          <td className="px-4 py-3 text-sm font-medium">
                            {payment.customerName}
                          </td>
                          <td className="px-4 py-3 text-sm font-medium">
                            {formatCurrency(payment.amount)}
                          </td>
                          <td className="px-4 py-3 text-sm text-muted-foreground">
                            {formatDate(payment.date)}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-medium ${
                                payment.status === "completed"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-yellow-100 text-yellow-800"
                              }`}
                            >
                              {payment.status}
                            </span>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          No data available
        </div>
      )}
    </div>
  );
}
