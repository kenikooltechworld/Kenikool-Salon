import { AgingReport as AgingReportType } from "@/lib/api/hooks/useAccounting";
import { Card } from "@/components/ui/card";
import { DollarSignIcon } from "@/components/icons";

interface AgingReportProps {
  data: AgingReportType[];
}

export function AgingReport({ data }: AgingReportProps) {
  const totals = data.reduce(
    (acc, row) => ({
      current: acc.current + row.current,
      days_30: acc.days_30 + row.days_30,
      days_60: acc.days_60 + row.days_60,
      days_90: acc.days_90 + row.days_90,
      over_90: acc.over_90 + row.over_90,
      total: acc.total + row.total,
    }),
    { current: 0, days_30: 0, days_60: 0, days_90: 0, over_90: 0, total: 0 }
  );

  if (data.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center py-12">
          <DollarSignIcon
            size={48}
            className="mx-auto text-[var(--muted-foreground)] mb-4"
          />
          <h3 className="text-lg font-semibold mb-2">
            No outstanding receivables
          </h3>
          <p className="text-[var(--muted-foreground)]">
            All invoices are paid
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Accounts Receivable Aging</h3>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-3 font-semibold">Client</th>
              <th className="text-right p-3 font-semibold">Current</th>
              <th className="text-right p-3 font-semibold">1-30 Days</th>
              <th className="text-right p-3 font-semibold">31-60 Days</th>
              <th className="text-right p-3 font-semibold">61-90 Days</th>
              <th className="text-right p-3 font-semibold">90+ Days</th>
              <th className="text-right p-3 font-semibold">Total</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr
                key={row.client_id}
                className="border-b hover:bg-[var(--muted)]"
              >
                <td className="p-3">{row.client_name}</td>
                <td className="text-right p-3">
                  {row.current > 0 ? `₦${row.current.toFixed(2)}` : "-"}
                </td>
                <td className="text-right p-3">
                  {row.days_30 > 0 ? `₦${row.days_30.toFixed(2)}` : "-"}
                </td>
                <td className="text-right p-3">
                  {row.days_60 > 0 ? `₦${row.days_60.toFixed(2)}` : "-"}
                </td>
                <td className="text-right p-3">
                  {row.days_90 > 0 ? `₦${row.days_90.toFixed(2)}` : "-"}
                </td>
                <td className="text-right p-3">
                  {row.over_90 > 0 ? `₦${row.over_90.toFixed(2)}` : "-"}
                </td>
                <td className="text-right p-3 font-semibold">
                  ₦{row.total.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="bg-[var(--muted)] font-bold">
              <td className="p-3">Total</td>
              <td className="text-right p-3">₦{totals.current.toFixed(2)}</td>
              <td className="text-right p-3">₦{totals.days_30.toFixed(2)}</td>
              <td className="text-right p-3">₦{totals.days_60.toFixed(2)}</td>
              <td className="text-right p-3">₦{totals.days_90.toFixed(2)}</td>
              <td className="text-right p-3">
                ₦{totals.over_90.toFixed(2)}
              </td>
              <td className="text-right p-3">₦{totals.total.toFixed(2)}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
        <div className="p-4 rounded-[var(--radius-md)]">
          <p className="text-sm mb-1">Current</p>
          <p className="text-xl font-bold">
            ₦{totals.current.toFixed(2)}
          </p>
        </div>
        <div className="p-4 rounded-[var(--radius-md)]">
          <p className="text-sm mb-1">1-30 Days</p>
          <p className="text-xl font-bold">
            ₦{totals.days_30.toFixed(2)}
          </p>
        </div>
        <div className="p-4 rounded-[var(--radius-md)]">
          <p className="text-sm mb-1">31-60 Days</p>
          <p className="text-xl font-bold">
            ₦{totals.days_60.toFixed(2)}
          </p>
        </div>
        <div className="p-4 rounded-[var(--radius-md)]">
          <p className="text-sm mb-1">61-90 Days</p>
          <p className="text-xl font-bold">
            ₦{totals.days_90.toFixed(2)}
          </p>
        </div>
        <div className="p-4 rounded-[var(--radius-md)]">
          <p className="text-sm mb-1">90+ Days</p>
          <p className="text-xl font-bold">
            ₦{totals.over_90.toFixed(2)}
          </p>
        </div>
        <div className="p-4 bg-[var(--primary)]/10 rounded-[var(--radius-md)]">
          <p className="text-sm text-[var(--primary)] mb-1">
            Total Outstanding
          </p>
          <p className="text-xl font-bold text-[var(--primary)]">
            ₦{totals.total.toFixed(2)}
          </p>
        </div>
      </div>
    </Card>
  );
}
