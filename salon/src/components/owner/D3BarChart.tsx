import { useEffect, useRef } from "react";
import * as d3 from "d3";

interface DataPoint {
  date: string;
  revenue: number;
}

interface D3BarChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  currency?: string;
}

export function D3BarChart({
  data,
  width = 800,
  height = 380,
  currency = "USD",
}: D3BarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove();

    // Get container width for responsiveness
    const containerWidth = containerRef.current?.clientWidth || width;
    const margin = { top: 30, right: 40, bottom: 70, left: 80 };
    const chartWidth = containerWidth - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    // Create SVG
    const svg = d3
      .select(svgRef.current)
      .attr("width", containerWidth)
      .attr("height", height)
      .attr("viewBox", `0 0 ${containerWidth} ${height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Parse dates and get revenue values
    const parseDate = d3.timeParse("%Y-%m-%d");
    const formattedData = data.map((d) => ({
      date: parseDate(d.date) || new Date(),
      revenue: d.revenue,
    }));

    // Create scales
    const xScale = d3
      .scaleBand()
      .domain(formattedData.map((d) => d.date.toISOString()))
      .range([0, chartWidth])
      .padding(0.2);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(formattedData, (d) => d.revenue) || 0])
      .nice()
      .range([chartHeight, 0]);

    // Get theme colors from CSS variables
    const primaryColor =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--primary")
        .trim() || "#3b82f6";
    const mutedColor =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--muted-foreground")
        .trim() || "#9ca3af";
    const borderColor =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--border")
        .trim() || "#e5e7eb";

    // Create axes
    const xAxis = d3
      .axisBottom(xScale)
      .tickFormat((d: d3.AxisDomain) => {
        const date = new Date(d as string);
        return d3.timeFormat("%b %d")(date);
      })
      .tickSizeOuter(0);

    const yAxis = d3
      .axisLeft(yScale)
      .ticks(5)
      .tickFormat((d: d3.NumberValue) => {
        const formatter = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: currency,
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        });
        return formatter.format(d as number);
      });

    // Add horizontal grid lines
    g.append("g")
      .attr("class", "grid")
      .selectAll("line")
      .data(yScale.ticks(5))
      .enter()
      .append("line")
      .attr("x1", 0)
      .attr("x2", chartWidth)
      .attr("y1", (d: number) => yScale(d))
      .attr("y2", (d: number) => yScale(d))
      .style("stroke", borderColor)
      .style("stroke-width", "1")
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.5);

    // Add X axis
    const xAxisGroup = g
      .append("g")
      .attr("class", "x-axis")
      .attr("transform", `translate(0,${chartHeight})`)
      .call(xAxis);

    xAxisGroup
      .selectAll("text")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end")
      .style("fill", mutedColor)
      .style("font-size", "11px")
      .style("font-weight", "500");

    xAxisGroup.select(".domain").style("stroke", borderColor);
    xAxisGroup.selectAll(".tick line").style("stroke", borderColor);

    // Add Y axis
    const yAxisGroup = g.append("g").attr("class", "y-axis").call(yAxis);

    yAxisGroup
      .selectAll("text")
      .style("fill", mutedColor)
      .style("font-size", "11px")
      .style("font-weight", "500");

    yAxisGroup.select(".domain").style("stroke", borderColor);
    yAxisGroup.selectAll(".tick line").style("stroke", borderColor);

    // Create tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "d3-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background-color", "rgba(15, 23, 42, 0.95)")
      .style("color", "white")
      .style("padding", "12px 16px")
      .style("border-radius", "8px")
      .style("font-size", "13px")
      .style("font-weight", "500")
      .style("pointer-events", "none")
      .style("z-index", "1000")
      .style("box-shadow", "0 10px 25px rgba(0, 0, 0, 0.2)")
      .style("backdrop-filter", "blur(8px)");

    // Add bars with gradient
    const defs = svg.append("defs");
    const gradient = defs
      .append("linearGradient")
      .attr("id", "bar-gradient")
      .attr("x1", "0%")
      .attr("y1", "0%")
      .attr("x2", "0%")
      .attr("y2", "100%");

    gradient
      .append("stop")
      .attr("offset", "0%")
      .attr("stop-color", primaryColor)
      .attr("stop-opacity", 1);

    gradient
      .append("stop")
      .attr("offset", "100%")
      .attr("stop-color", primaryColor)
      .attr("stop-opacity", 0.7);

    // Add bars
    g.selectAll(".bar")
      .data(formattedData)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr(
        "x",
        (d: { date: Date; revenue: number }) =>
          xScale(d.date.toISOString()) || 0,
      )
      .attr("y", chartHeight)
      .attr("width", xScale.bandwidth())
      .attr("height", 0)
      .attr("fill", "url(#bar-gradient)")
      .attr("rx", 6)
      .style("cursor", "pointer")
      .style("transition", "all 0.2s ease")
      .on(
        "mouseover",
        function (_event: MouseEvent, d: { date: Date; revenue: number }) {
          d3.select(this as SVGRectElement)
            .transition()
            .duration(200)
            .attr("opacity", 0.85)
            .attr("transform", "translateY(-2)");

          const formatter = new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: currency,
          });
          tooltip.style("visibility", "visible").html(
            `<div style="line-height: 1.6;">
                <div style="font-size: 11px; opacity: 0.8; margin-bottom: 4px;">${d3.timeFormat("%b %d, %Y")(d.date)}</div>
                <div style="font-size: 16px; font-weight: 600;">${formatter.format(d.revenue)}</div>
              </div>`,
          );
        },
      )
      .on("mousemove", function (event: MouseEvent) {
        tooltip
          .style("top", event.pageY - 70 + "px")
          .style("left", event.pageX - 60 + "px");
      })
      .on("mouseout", function () {
        d3.select(this as SVGRectElement)
          .transition()
          .duration(200)
          .attr("opacity", 1)
          .attr("transform", "translateY(0)");
        tooltip.style("visibility", "hidden");
      })
      .transition()
      .duration(800)
      .delay((_d: { date: Date; revenue: number }, i: number) => i * 50)
      .ease(d3.easeCubicOut)
      .attr("y", (d: { date: Date; revenue: number }) => yScale(d.revenue))
      .attr(
        "height",
        (d: { date: Date; revenue: number }) => chartHeight - yScale(d.revenue),
      );

    // Cleanup tooltip on unmount
    return () => {
      tooltip.remove();
    };
  }, [data, width, height, currency]);

  if (!data || data.length === 0) {
    return (
      <div
        className="h-64 rounded-lg flex items-center justify-center"
        style={{ backgroundColor: "var(--muted)" }}
      >
        <p style={{ color: "var(--muted-foreground)" }}>No data available</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="w-full rounded-lg"
      style={{ backgroundColor: "var(--card)" }}
    >
      <svg ref={svgRef} className="w-full" style={{ overflow: "visible" }} />
    </div>
  );
}
