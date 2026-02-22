import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface LTVDistributionChartProps {
  width?: number;
  height?: number;
}

export const LTVDistributionChart: React.FC<LTVDistributionChartProps> = ({
  width = 900,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const ltv = Array.from({ length: 500 }, () => Math.random() * 10000 + 500);

    const trace1 = {
      x: ltv,
      type: 'histogram',
      name: 'All Clients',
      nbinsx: 30,
      marker: { color: '#3498db', opacity: 0.7 },
    };

    const highValue = ltv.filter((v) => v > 5000);
    const trace2 = {
      x: highValue,
      type: 'histogram',
      name: 'High Value (>$5000)',
      nbinsx: 20,
      marker: { color: '#2ecc71', opacity: 0.7 },
    };

    const layout = {
      title: 'Client Lifetime Value Distribution',
      xaxis: { title: 'LTV ($)' },
      yaxis: { title: 'Number of Clients' },
      barmode: 'overlay',
      width: width,
      height: height,
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
    };

    Plotly.newPlot(containerRef.current, [trace1, trace2], layout, config);

    return () => {
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [width, height]);

  return <div ref={containerRef} />;
};
