import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface BoxPlotData {
  category: string;
  values: number[];
}

interface InventoryBoxPlotProps {
  data?: BoxPlotData[];
  width?: number;
  height?: number;
}

export const InventoryBoxPlot: React.FC<InventoryBoxPlotProps> = ({
  data,
  width = 900,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const defaultData: BoxPlotData[] = [
      {
        category: 'Hair Care',
        values: [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
      },
      {
        category: 'Styling Products',
        values: [5, 8, 12, 15, 18, 22, 25, 28, 32, 35, 38, 42, 45],
      },
      {
        category: 'Accessories',
        values: [2, 3, 5, 7, 10, 12, 15, 18, 20, 22, 25, 28, 30],
      },
      {
        category: 'Treatments',
        values: [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56],
      },
    ];

    const boxData = data || defaultData;

    const traces = boxData.map((d) => ({
      y: d.values,
      name: d.category,
      type: 'box',
      boxmean: 'sd',
    }));

    const layout = {
      title: 'Inventory Distribution by Category',
      yaxis: { title: 'Stock Level' },
      width: width,
      height: height,
      showlegend: true,
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
    };

    Plotly.newPlot(containerRef.current, traces, layout, config);

    return () => {
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [data, width, height]);

  return <div ref={containerRef} />;
};
