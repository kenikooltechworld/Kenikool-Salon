import { Card } from "@/components/ui/card";
import { useEffect, useRef } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ServiceData {
  service_name: string;
  total_bookings: number;
  total_revenue: number;
  average_rating?: number;
}

interface ServicePerformanceProps {
  services: ServiceData[];
}

export function ServicePerformance({ services }: ServicePerformanceProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstanceRef = useRef<ChartJS | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Destroy existing chart
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    // Format data for the chart - take top 10 services by revenue
    const chartData = services
      .sort((a, b) => b.total_revenue - a.total_revenue)
      .slice(0, 10)
      .map((service) => ({
        name:
          service.service_name.length > 15
            ? service.service_name.substring(0, 15) + "..."
            : service.service_name,
        revenue: service.total_revenue,
        bookings: service.total_bookings,
      }));

    if (chartData.length === 0) return;

    const ctx = chartRef.current.getContext("2d");
    if (!ctx) return;

    const options: ChartOptions<"bar"> = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "top" as const,
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
      type: "bar",
      data: {
        labels: chartData.map((d) => d.name),
        datasets: [
          {
            label: "Revenue",
            data: chartData.map((d) => d.revenue),
            backgroundColor: "rgba(99, 102, 241, 0.8)",
            borderColor: "rgb(99, 102, 241)",
            borderWidth: 1,
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
  }, [services]);

  const hasData = services.length > 0;

  return (
    <Card className="p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Service Performance
        </h2>
        <p className="text-sm text-muted-foreground">Top services by revenue</p>
      </div>

      {!hasData ? (
        <div className="flex items-center justify-center h-64 text-muted-foreground">
          No service data available
        </div>
      ) : (
        <div style={{ height: "300px" }}>
          <canvas ref={chartRef} />
        </div>
      )}
    </Card>
  );
}
