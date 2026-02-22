import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { BarChartIcon, ChartIcon, TrendingUpIcon } from "@/components/icons";

export default function Reports() {
  const navigate = useNavigate();

  const reports = [
    {
      title: "Revenue Report",
      description: "View revenue by period, service, and staff member",
      icon: TrendingUpIcon,
      path: "/reports/revenue",
      color: "bg-blue-100 text-blue-600",
    },
    {
      title: "Payment Statistics",
      description: "Payment success rates, methods, and status breakdown",
      icon: BarChartIcon,
      path: "/reports/payments",
      color: "bg-green-100 text-green-600",
    },
    {
      title: "Customer Balance",
      description: "Outstanding balances and payment history",
      icon: ChartIcon,
      path: "/reports/balance",
      color: "bg-purple-100 text-purple-600",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Financial Reports</h1>
        <p className="text-muted-foreground mt-1">
          View detailed financial analytics and reports
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => {
          const Icon = report.icon;
          return (
            <div
              key={report.path}
              className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition cursor-pointer"
              onClick={() => navigate(report.path)}
            >
              <div
                className={`w-12 h-12 rounded-lg ${report.color} flex items-center justify-center mb-4`}
              >
                <Icon size={24} />
              </div>
              <h3 className="text-lg font-semibold mb-2">{report.title}</h3>
              <p className="text-sm text-muted-foreground mb-4">
                {report.description}
              </p>
              <Button variant="outline" className="w-full">
                View Report
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
