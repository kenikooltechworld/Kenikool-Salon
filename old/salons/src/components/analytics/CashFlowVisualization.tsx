import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface CashFlowData {
  date: string;
  inflow: number;
  outflow: number;
  net: number;
}

interface CashFlowVisualizationProps {
  data?: CashFlowData[];
  width?: number;
  height?: number;
}

export const CashFlowVisualization: React.FC<CashFlowVisualizationProps> = ({
  data,
  width = 900,
  height = 400,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const defaultData: CashFlowData[] = Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (30 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      inflow: 5000 + Math.random() * 2000,
      outflow: 3000 + Math.random() * 1500,
      net: 0,
    })).map((d) => ({ ...d, net: d.inflow - d.outflow }));

    const chartData = data || defaultData;
    const margin = { top: 20, right: 30, bottom: 30, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const g = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3
      .scaleTime()
      .domain([new Date(chartData[0].date), new Date(chartData[chartData.length - 1].date)])
      .range([0, innerWidth]);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(chartData, (d) => d.inflow) || 7000])
      .range([innerHeight, 0]);

    const line = d3
      .line<CashFlowData>()
      .x((d) => xScale(new Date(d.date)))
      .y((d) => yScale(d.inflow));

    const area = d3
      .area<CashFlowData>()
      .x((d) => xScale(new Date(d.date)))
      .y0(innerHeight)
      .y1((d) => yScale(d.net));

    g.append('path')
      .datum(chartData)
      .attr('fill', '#e8f5e9')
      .attr('d', area);

    g.append('path')
      .datum(chartData)
      .attr('fill', 'none')
      .attr('stroke', '#2ecc71')
      .attr('stroke-width', 2)
      .attr('d', line);

    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale).ticks(5));

    g.append('g').call(d3.axisLeft(yScale));

    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - innerHeight / 2)
      .attr('dy', '1em')
      .attr('text-anchor', 'middle')
      .text('Cash Flow ($)');
  }, [data, width, height]);

  return <svg ref={svgRef} />;
};
