import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { DownloadIcon, CopyIcon } from "@/components/icons";
import {
  exportChartToPNG,
  exportChartToSVG,
  exportPlotlyChartToPNG,
  exportPlotlyChartToSVG,
  copyChartToClipboard,
} from "@/lib/utils/chart-export";

interface ChartExportButtonProps {
  chartRef: React.RefObject<SVGSVGElement | HTMLElement>;
  chartTitle?: string;
  chartType?: "d3" | "plotly" | "canvas";
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

export function ChartExportButton({
  chartRef,
  chartTitle = "chart",
  chartType = "d3",
  showLabel = true,
  size = "md",
}: ChartExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleExportPNG = async () => {
    setIsExporting(true);
    setError(null);
    try {
      if (chartType === "plotly") {
        await exportPlotlyChartToPNG(
          chartRef.current as HTMLElement,
          chartTitle
        );
      } else {
        await exportChartToPNG(
          chartRef.current as SVGSVGElement,
          chartTitle
        );
      }
      setIsOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export PNG");
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportSVG = async () => {
    setIsExporting(true);
    setError(null);
    try {
      if (chartType === "plotly") {
        await exportPlotlyChartToSVG(
          chartRef.current as HTMLElement,
          chartTitle
        );
      } else {
        exportChartToSVG(chartRef.current as SVGSVGElement, chartTitle);
      }
      setIsOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export SVG");
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopyToClipboard = async () => {
    setIsExporting(true);
    setError(null);
    try {
      await copyChartToClipboard(chartRef.current as SVGSVGElement);
      setIsOpen(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to copy to clipboard"
      );
    } finally {
      setIsExporting(false);
    }
  };

  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-2 text-sm",
    lg: "px-4 py-3 text-base",
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="outline"
        size={size}
        className={sizeClasses[size]}
        disabled={isExporting}
      >
        <DownloadIcon size={16} />
        {showLabel && <span className="ml-2">Export</span>}
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="py-1">
            <button
              onClick={handleExportPNG}
              disabled={isExporting}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <DownloadIcon size={16} />
              Export as PNG
            </button>
            <button
              onClick={handleExportSVG}
              disabled={isExporting}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <DownloadIcon size={16} />
              Export as SVG
            </button>
            <button
              onClick={handleCopyToClipboard}
              disabled={isExporting}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <CopyIcon size={16} />
              Copy to Clipboard
            </button>
          </div>
          {error && (
            <div className="px-4 py-2 text-xs text-red-600 bg-red-50 border-t border-gray-200">
              {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
