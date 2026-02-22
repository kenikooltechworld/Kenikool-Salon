import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TreemapData {
  name: string;
  value: number;
  profitability: number;
  children?: TreemapData[];
}

interface RevenueTreemapProps {
  data?: TreemapData;
  width?: number;
  height?: number;
}

export const RevenueTreemap: React.FC<RevenueTreemapProps> = ({
  data,
  width = 900,
  height = 500,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const defaultData: TreemapData = {
      name: 'Revenue',
      value: 0,
      profitability: 0,
      children: [
        {
          name: 'Hair Services',
          value: 50000,
          profitability: 0.45,
          children: [
            { name: 'Cuts', value: 20000, profitability: 0.5 },
            { name: 'Color', value: 20000, profitability: 0.4 },
            { name: 'Styling', value: 10000, profitability: 0.45 },
          ],
        },
        {
          name: 'Retail Products',
          value: 15000,
          profitability: 0.35,
          children: [
            { name: 'Shampoo', value: 8000, profitability: 0.4 },
            { name: 'Conditioner', value: 7000, profitability: 0.3 },
          ],
        },
      ],
    };

    const treeData = data || defaultData;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    svg.attr('width', width).attr('height', height);

    const treemap = d3.treemap().size([width, height]).paddingTop(0).paddingRight(2).paddingBottom(2).paddingLeft(2);

    const root = d3
      .hierarchy(treeData)
      .sum((d) => d.value)
      .sort((a, b) => (b.value || 0) - (a.value || 0));

    treemap(root);

    const colorScale = d3
      .scaleLinear<string>()
      .domain([0, 1])
      .range(['#ff6b6b', '#51cf66']);

    const cells = svg
      .selectAll('g')
      .data(root.leaves())
      .enter()
      .append('g')
      .attr('transform', (d) => `translate(${d.x0},${d.y0})`);

    cells
      .append('rect')
      .attr('width', (d) => d.x1 - d.x0)
      .attr('height', (d) => d.y1 - d.y0)
      .attr('fill', (d) => colorScale(d.data.profitability))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    cells
      .append('text')
      .attr('x', 4)
      .attr('y', 20)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#000')
      .text((d) => d.data.name);

    cells
      .append('text')
      .attr('x', 4)
      .attr('y', 35)
      .attr('font-size', '11px')
      .attr('fill', '#666')
      .text((d) => `$${(d.value || 0).toLocaleString()}`);
  }, [data, width, height]);

  return <svg ref={svgRef} />;
};
