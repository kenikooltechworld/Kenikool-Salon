import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

interface CohortData {
  cohort: string;
  week0: number;
  week1: number;
  week2: number;
  week3: number;
  week4: number;
}

interface ClientCohortAnalysisProps {
  data?: CohortData[];
  width?: number;
  height?: number;
}

export const ClientCohortAnalysis: React.FC<ClientCohortAnalysisProps> = ({
  data,
  width = 900,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const defaultData: CohortData[] = [
      { cohort: 'Week 1', week0: 100, week1: 85, week2: 72, week3: 65, week4: 58 },
      { cohort: 'Week 2', week0: 110, week1: 92, week2: 78, week3: 70, week4: 0 },
      { cohort: 'Week 3', week0: 95, week1: 80, week2: 68, week3: 0, week4: 0 },
      { cohort: 'Week 4', week0: 105, week1: 88, week2: 0, week3: 0, week4: 0 },
      { cohort: 'Week 5', week0: 98, week1: 0, week2: 0, week3: 0, week4: 0 },
    ];

    const cohortData = data || defaultData;

    const z = cohortData.map((d) => [d.week0, d.week1, d.week2, d.week3, d.week4]);
    const cohorts = cohortData.map((d) => d.cohort);

    const trace = {
      z: z,
      x: ['Week 0', 'Week 1', 'Week 2', 'Week 3', 'Week 4'],
      y: cohorts,
      type: 'heatmap',
      colorscale: 'Viridis',
      hovertemplate: 'Cohort: %{y}<br>Period: %{x}<br>Retention: %{z}%<extra></extra>',
    };

    const layout = {
      title: 'Client Cohort Retention Analysis',
      xaxis: { title: 'Weeks Since First Visit' },
      yaxis: { title: 'Cohort' },
      width: width,
      height: height,
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
    };

    Plotly.newPlot(containerRef.current, [trace], layout, config);

    return () => {
      if (containerRef.current) {
        Plotly.purge(containerRef.current);
      }
    };
  }, [data, width, height]);

  return <div ref={containerRef} />;
};
