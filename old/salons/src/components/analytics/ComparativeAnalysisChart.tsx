import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ComparisonData {
  period: string;
  current: number;
  previous: number;
}

interface ComparativeAnalysisChartProps {
  data?: ComparisonData[];
  width?: number;
  height?: number;
  title?: string;
}

export const ComparativeAnalysisChart: React.FC<ComparativeAnalysisChartProps> = ({
  data,
  width = 900,
  height = 400,
  title = 'Year-over-Year Comparison',
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const defaultData: ComparisonData[] = [
      { period: 'Jan', current: 4500, previous: 4000 },
      { period: 'Feb', current: 5200, previous: 4800 },
      { period: 'Mar', current: 5800, previous: 5200 },
      { period: 'Apr', current: 6200, previous: 5500 },
      { period: 'May', current: 6800, previous: 6000 },
      { period: 'Jun', current: 7200, previous: 6500 },
    ];

    const chartData = data || defaultData;
    const margin = { top: 40, right: 30, bottom: 30, left: 60 };
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
      .scaleBand()
      .domain(chartData.map((d) => d.period))
      .range([0, innerWidth])
      .padding(0.2);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(chartData, (d) => Math.max(d.current, d.previous)) || 8000])
      .range([innerHeight, 0]);

    const xSubScale = d3
      .scaleBand()
      .domain(['current', 'previous'])
      .range([0, xScale.bandwidth()])
      .padding(0.05);

    g.selectAll('g.group')
      .data(chartData)
      .enter()
      .append('g')
      .attr('class', 'group')
      .attr('transform', (d) => `translate(${xScale(d.period)},0)`)
      .selectAll('rect')
      .data((d) => [
        { key: 'current', value: d.current },
        { key: 'previous', value: d.previous },
      ])
      .enter()
      .append('rect')
      .attr('x', (d) => xSubScale(d.key) || 0)
      .attr('y', (d) => yScale(d.value))
      .attr('width', xSubScale.bandwidth())
      .attr('height', (d) => innerHeight - yScale(d.value))
      .attr('fill', (d) => (d.key === 'current' ? '#3498db' : '#95a5a6'));

    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale));

    g.append('g').call(d3.axisLeft(yScale));

    g.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', -20)
      .attr('text-anchor', 'middle')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text(title);

    const legend = g
      .append('g')
      .attr('transform', `translate(${innerWidth - 150}, -30)`);

    legend
      .append('rect')
      .attr('width', 20)
      .attr('height', 20)
      .attr('fill', '#3498db');

    legend
      .append('text')
      .attr('x', 30)
      .attr('y', 15)
      .attr('font-size', '12px')
      .text('Current');

    legend
      .append('rect')
      .attr('y', 25)
      .attr('width', 20)
      .attr('height', 20)
      .attr('fill', '#95a5a6');

    legend
      .append('text')
      .attr('x', 30)
      .attr('y', 40)
      .attr('font-size', '12px')
      .text('Previous');
  }, [data, width, height, title]);

  return <svg ref={svgRef} />;
};
