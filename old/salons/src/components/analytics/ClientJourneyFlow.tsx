import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface SankeyNode {
  name: string;
}

interface SankeyLink {
  source: number;
  target: number;
  value: number;
}

interface ClientJourneyFlowProps {
  data?: { nodes: SankeyNode[]; links: SankeyLink[] };
  width?: number;
  height?: number;
}

export const ClientJourneyFlow: React.FC<ClientJourneyFlowProps> = ({
  data,
  width = 900,
  height = 500,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const defaultData = {
      nodes: [
        { name: 'Website' },
        { name: 'Phone Call' },
        { name: 'First Booking' },
        { name: 'Repeat Booking' },
        { name: 'Loyal Customer' },
        { name: 'Churned' },
      ],
      links: [
        { source: 0, target: 2, value: 100 },
        { source: 1, target: 2, value: 80 },
        { source: 2, target: 3, value: 120 },
        { source: 3, target: 4, value: 90 },
        { source: 3, target: 5, value: 30 },
      ],
    };

    const flowData = data || defaultData;
    const margin = { top: 20, right: 160, bottom: 20, left: 160 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const g = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const sankey = d3
      .sankey()
      .nodeWidth(15)
      .nodePadding(50)
      .extent([[0, 0], [innerWidth, innerHeight]]);

    const { nodes, links } = sankey({
      nodes: flowData.nodes.map((d) => ({ ...d })),
      links: flowData.links.map((d) => ({ ...d })),
    });

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    g.append('g')
      .selectAll('rect')
      .data(nodes)
      .enter()
      .append('rect')
      .attr('x', (d) => d.x0 || 0)
      .attr('y', (d) => d.y0 || 0)
      .attr('height', (d) => (d.y1 || 0) - (d.y0 || 0))
      .attr('width', sankey.nodeWidth())
      .attr('fill', (d, i) => color(String(i)))
      .attr('stroke', '#000');

    g.append('g')
      .attr('fill', 'none')
      .selectAll('path')
      .data(links)
      .enter()
      .append('path')
      .attr('d', d3.sankeyLinkHorizontal())
      .attr('stroke', (d, i) => color(String(i)))
      .attr('stroke-opacity', 0.5)
      .attr('stroke-width', (d) => Math.max(1, (d.width || 0) / 10));

    g.append('g')
      .style('font', '12px sans-serif')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('x', (d) => ((d.x0 || 0) < innerWidth / 2 ? (d.x1 || 0) + 6 : (d.x0 || 0) - 6))
      .attr('y', (d) => ((d.y1 || 0) + (d.y0 || 0)) / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', (d) => ((d.x0 || 0) < innerWidth / 2 ? 'start' : 'end'))
      .text((d) => d.name);
  }, [data, width, height]);

  return <svg ref={svgRef} />;
};
