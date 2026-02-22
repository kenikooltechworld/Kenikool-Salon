import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface ProductSalesData {
  product: string;
  sales: number;
  category: string;
}

interface ProductSalesChartProps {
  data?: ProductSalesData[];
  width?: number;
  height?: number;
}

export const ProductSalesChart: React.FC<ProductSalesChartProps> = ({
  data,
  width = 900,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const defaultData: ProductSalesData[] = [
      { product: 'Shampoo Pro', sales: 8500, category: 'Hair Care' },
      { product: 'Conditioner Plus', sales: 7200, category: 'Hair Care' },
      { product: 'Hair Gel', sales: 4500, category: 'Styling' },
      { product: 'Hair Spray', sales: 3800, category: 'Styling' },
      { product: 'Hair Mask', sales: 6200, category: 'Treatments' },
      { product: 'Hair Oil', sales: 5100, category: 'Treatments' },
      { product: 'Hair Clips', sales: 2300, category: 'Accessories' },
      { product: 'Hair Brush', sales: 3100, category: 'Accessories' },
    ];

    const salesData = data || defaultData;

    const categories = [...new Set(salesData.map((d) => d.category))];
    const colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12'];

    const traces = categories.map((category, idx) => ({
      x: salesData.filter((d) => d.category === category).map((d) => d.product),
      y: salesData.filter((d) => d.category === category).map((d) => d.sales),
      name: category,
      type: 'bar',
      marker: { color: colors[idx % colors.length] },
    }));

    const layout = {
      title: 'Product Sales by Category',
      xaxis: { title: 'Product' },
      yaxis: { title: 'Sales ($)' },
      barmode: 'group',
      width: width,
      height: height,
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
