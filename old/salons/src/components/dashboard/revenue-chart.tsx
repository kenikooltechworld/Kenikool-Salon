import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useEffect, useRef } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface RevenueDataPoint {
  date: string;
  revenue: number;
}

interface RevenueChartProps {
  data: RevenueDataPoint[];
  loading?: boolean;
  period: "day" | "week" | "month";
}

export function RevenueChart({
  data,
  loading = false,
  period,
}: RevenueChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstanceRef = useRef<ChartJS | null>(null);

  const periodLabels = {
    day: "Last 7 Days",
    week: "Last 8 Weeks",
    month: "Last 12 Months",
  };

  useEffect(() => {
    if (!chartRef.current || loading || data.length === 0) return;

    // Destroy existing chart
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    const ctx = chartRef.current.getContext("2d");
    if (!ctx) return;

    const options: ChartOptions<"line"> = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed.y ?? 0;
              return `Revenue: ₦${value.toLocaleString()}`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `₦${Number(value).toLocaleString()}`,
          },
        },
      },
    };

    chartInstanceRef.current = new ChartJS(ctx, {
      type: "line",
      data: {
        labels: data.map((d) => d.date),
        datasets: [
          {
            label: "Revenue",
            data: data.map((d) => d.revenue),
            borderColor: "rgb(99, 102, 241)",
            backgroundColor: "rgba(99, 102, 241, 0.1)",
            tension: 0.4,
          },
        ],
      },
      options,
    });

    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, [data, loading]);

  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-bottom-4 duration-500"
      role="region"
      aria-label="Revenue Trend Chart"
    >
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">Revenue Trend</h2>
        <p className="text-sm text-muted-foreground">{periodLabels[period]}</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : data.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No revenue data available</p>
        </div>
      ) : (
        <div
          className="h-[300px]"
          role="img"
          aria-label={`Revenue trend chart showing ${data.length} data points for ${periodLabels[period]}`}
        >
          <canvas ref={chartRef} />
        </div>
      )}
    </Card>
  );
}
