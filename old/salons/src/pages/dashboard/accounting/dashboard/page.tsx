import {
  useGetDashboardKPIs,
  useGetDashboardTrends,
  useGetFinancialRatios,
  useGetDashboardAlerts,
} from '@/lib/api/hooks/useAccounting';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle } from '@/components/icons';

export default function AccountingDashboardPage() {
  const kpisQuery = useGetDashboardKPIs();
  const trendsQuery = useGetDashboardTrends();
  const ratiosQuery = useGetFinancialRatios();
  const alertsQuery = useGetDashboardAlerts();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Accounting Dashboard</h1>
        <p className="text-muted-foreground mt-2">Financial overview and key metrics</p>
      </div>

      {/* Alerts */}
      {alertsQuery.data?.alerts && alertsQuery.data.alerts.length > 0 && (
        <div className="space-y-2">
          {alertsQuery.data.alerts.map((alert: any, idx: number) => (
            <Card key={idx}>
              <CardContent className="pt-6 flex gap-3">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-medium">{alert.title}</h3>
                  <p className="text-sm">{alert.message}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* KPI Cards */}
      {kpisQuery.data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Cash Balance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${kpisQuery.data.cash_balance.toFixed(2)}</div>
              <p className="text-xs mt-1">Current cash on hand</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Accounts Receivable</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${kpisQuery.data.accounts_receivable.toFixed(2)}</div>
              <p className="text-xs mt-1">Outstanding invoices</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Accounts Payable</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${kpisQuery.data.accounts_payable.toFixed(2)}</div>
              <p className="text-xs mt-1">Outstanding bills</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Working Capital</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${kpisQuery.data.working_capital.toFixed(2)}
              </div>
              <p className="text-xs mt-1">Current assets - liabilities</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Current Month Performance */}
      {kpisQuery.data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Current Revenue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${kpisQuery.data.current_revenue.toFixed(2)}</div>
              <p className="text-xs mt-1">This month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Current Expenses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${kpisQuery.data.current_expenses.toFixed(2)}</div>
              <p className="text-xs mt-1">This month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Current Profit</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${kpisQuery.data.current_profit.toFixed(2)}
              </div>
              <p className="text-xs mt-1">
                {kpisQuery.data.profit_margin.toFixed(1)}% margin
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Overdue Items */}
      {kpisQuery.data && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Overdue Invoices</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {kpisQuery.data.overdue_invoices_count}
              </div>
              <p className="text-xs mt-1">
                ${kpisQuery.data.overdue_invoices_amount.toFixed(2)} outstanding
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Overdue Bills</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {kpisQuery.data.overdue_bills_count}
              </div>
              <p className="text-xs mt-1">
                ${kpisQuery.data.overdue_bills_amount.toFixed(2)} due
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Financial Ratios */}
      {ratiosQuery.data && (
        <Card>
          <CardHeader>
            <CardTitle>Financial Ratios</CardTitle>
            <CardDescription>Key financial metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium mb-1">Current Ratio</p>
                <p className="text-2xl font-bold">{ratiosQuery.data.current_ratio.toFixed(2)}</p>
                <p className="text-xs mt-1">Assets / Liabilities</p>
              </div>

              <div>
                <p className="text-sm font-medium mb-1">Debt-to-Equity</p>
                <p className="text-2xl font-bold">{ratiosQuery.data.debt_to_equity.toFixed(2)}</p>
                <p className="text-xs mt-1">Liabilities / Equity</p>
              </div>

              <div>
                <p className="text-sm font-medium mb-1">Return on Assets</p>
                <p className="text-2xl font-bold">{(ratiosQuery.data.return_on_assets * 100).toFixed(2)}%</p>
                <p className="text-xs mt-1">Revenue / Assets</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trends */}
      {trendsQuery.data?.trends && (
        <Card>
          <CardHeader>
            <CardTitle>12-Month Trends</CardTitle>
            <CardDescription>Revenue, expenses, and profit trends</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr>
                    <th className="text-left py-2 px-4">Month</th>
                    <th className="text-right py-2 px-4">Revenue</th>
                    <th className="text-right py-2 px-4">Expenses</th>
                    <th className="text-right py-2 px-4">Profit</th>
                  </tr>
                </thead>
                <tbody>
                  {trendsQuery.data.trends.map((trend: any) => (
                    <tr key={trend.month} className="border-b hover:bg-muted">
                      <td className="py-2 px-4 text-xs font-medium">{trend.month}</td>
                      <td className="py-2 px-4 text-right text-xs">
                        ${trend.revenue.toFixed(2)}
                      </td>
                      <td className="py-2 px-4 text-right text-xs">
                        ${trend.expenses.toFixed(2)}
                      </td>
                      <td className="py-2 px-4 text-right text-xs font-medium">
                        ${trend.profit.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
