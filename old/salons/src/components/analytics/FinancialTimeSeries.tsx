import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface FinancialMetric {
  date: string;
  revenue: number;
  expenses: number;
  profit: number;
  margin_percentage: number;
}

interface FinancialTimeSeriesProps {
  data: FinancialMetric[];
  width?: number;
  height?: number;
  title?: string;
}

export const FinancialTimeSeries: React.FC<FinancialTimeSeriesProps> = ({
  data,
  width = 900,
  height = 500,
  title = 'Financial Trends',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !data || data.length === 0) return;

    const dates = data.map((d) => d.date);
    const revenue = data.map((d) => d.revenue);
    const expenses = data.map((d) => d.expenses);
    const profit = data.map((d) => d.profit);

    const trace1 = {
      x: dates,
      y: revenue,
      name: 'Revenue',
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: '#2ecc71', width: 2 },
      yaxis: 'y1',
    };

    const trace2 = {
      x: dates,
      y: expenses,
      name: 'Expenses',
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: '#e74c3c', width: 2 },
      yaxis: 'y1',
    };

    const trace3 = {
      x: dates,
      y: profit,
      name: 'Profit',
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: '#3498db', width: 2 },
      yaxis: 'y2',
    };

    const layout = {
      title: title,
      xaxis: {
        title: 'Date',
        type: 'date',
      },
      yaxis: {
        title: 'Revenue & Expenses ($)',
        side: 'left',
      },
      yaxis2: {
        title: 'Profit ($)',
        overlaying: 'y',
        side: 'right',
      },
      hovermode: 'x unified',
      width: width,
      height: height,
      margin: { l: 60, r: 60, t: 60, b: 60 },
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    };

    Plotly.newPlot(containerRef.current, [trace1, trace2, trace3], layout, config);

    return () => {
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [data, width, height, title]);

  return <div ref={containerRef} />;
};
