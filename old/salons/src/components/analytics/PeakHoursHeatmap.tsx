import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface PeakHourData {
  hour: number;
  day_of_week: number;
  bookings_count: number;
  revenue: number;
  capacity_utilization: number;
  staff_count: number;
}

interface PeakHoursHeatmapProps {
  data: PeakHourData[];
  width?: number;
  height?: number;
  onCellClick?: (hour: number, day: number) => void;
}

export const PeakHoursHeatmap: React.FC<PeakHoursHeatmapProps> = ({
  data,
  width = 800,
  height = 400,
  onCellClick,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    const margin = { top: 20, right: 20, bottom: 60, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const g = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Create scales
    const xScale = d3
      .scaleBand()
      .domain(d3.range(0, 24).map(String))
      .range([0, innerWidth])
      .padding(0.05);

    const yScale = d3
      .scaleBand()
      .domain(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
      .range([0, innerHeight])
      .padding(0.05);

    const colorScale = d3
      .scaleLinear<string>()
      .domain([0, d3.max(data, (d) => d.bookings_count) || 100])
      .range(['#f7fbff', '#08519c']);

    // Draw cells
    g.selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', (d) => xScale(String(d.hour)) || 0)
      .attr('y', (d) => yScale(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][d.day_of_week]) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', (d) => colorScale(d.bookings_count))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1)
      .on('click', (event, d) => {
        if (onCellClick) {
          onCellClick(d.hour, d.day_of_week);
        }
      })
      .on('mouseover', function (event, d) {
        d3.select(this).attr('stroke', '#000').attr('stroke-width', 2);
        
        // Show tooltip
        const tooltip = d3.select('body')
          .append('div')
          .attr('class', 'tooltip')
          .style('position', 'absolute')
          .style('background', 'rgba(0,0,0,0.8)')
          .style('color', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('pointer-events', 'none')
          .style('left', `${event.pageX + 10}px`)
          .style('top', `${event.pageY + 10}px`)
          .html(`
            <strong>Hour ${d.hour}:00</strong><br/>
            Bookings: ${d.bookings_count}<br/>
            Revenue: $${d.revenue.toFixed(2)}<br/>
            Utilization: ${(d.capacity_utilization * 100).toFixed(1)}%<br/>
            Staff: ${d.staff_count}
          `);

        setTimeout(() => tooltip.remove(), 3000);
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke', '#fff').attr('stroke-width', 1);
      });

    // Add X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', 40)
      .attr('fill', 'black')
      .attr('text-anchor', 'middle')
      .text('Hour of Day');

    // Add Y axis
    g.append('g')
      .call(d3.axisLeft(yScale))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - innerHeight / 2)
      .attr('dy', '1em')
      .attr('fill', 'black')
      .attr('text-anchor', 'middle')
      .text('Day of Week');

    // Add color legend
    const legendWidth = 20;
    const legendHeight = 200;
    const legend = g
      .append('g')
      .attr('transform', `translate(${innerWidth + 20}, 0)`);

    const legendScale = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.bookings_count) || 100])
      .range([legendHeight, 0]);

    const legendAxis = d3.axisRight(legendScale).ticks(5);

    legend
      .append('defs')
      .append('linearGradient')
      .attr('id', 'legend-gradient')
      .attr('x1', '0%')
      .attr('x2', '0%')
      .attr('y1', '100%')
      .attr('y2', '0%')
      .selectAll('stop')
      .data(
        d3.range(0, 1.01, 0.1).map((d) => ({
          offset: `${d * 100}%`,
          color: colorScale(d * (d3.max(data, (d) => d.bookings_count) || 100)),
        }))
      )
      .enter()
      .append('stop')
      .attr('offset', (d) => d.offset)
      .attr('stop-color', (d) => d.color);

    legend
      .append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .attr('fill', 'url(#legend-gradient)');

    legend.append('g').attr('transform', `translate(${legendWidth}, 0)`).call(legendAxis);
  }, [data, width, height]);

  return <svg ref={svgRef} />;
};
