import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

interface ReportExporterProps {
  reportData: Record<string, any>;
  reportName: string;
  onExport?: (format: "csv" | "pdf") => Promise<void>;
}

export const ReportExporter: React.FC<ReportExporterProps> = ({
  reportData,
  reportName,
  onExport,
}) => {
  const [exporting, setExporting] = useState(false);
  const [format, setFormat] = useState<"csv" | "pdf">("csv");

  const handleExport = async () => {
    setExporting(true);

    try {
      if (onExport) {
        await onExport(format);
      } else {
        if (format === "csv") {
          exportAsCSV();
        } else {
          exportAsJSON();
        }
      }
    } finally {
      setExporting(false);
    }
  };

  const exportAsCSV = () => {
    const headers = Object.keys(reportData[0] || {});
    const rows = Object.values(reportData).map((item: any) =>
      headers.map((header) => {
        const value = item[header];
        return `"${String(value).replace(/"/g, '""')}"`;
      }),
    );

    const csv = [headers.join(","), ...rows.map((row) => row.join(","))].join(
      "\n",
    );

    downloadFile(csv, "text/csv", `${reportName}.csv`);
  };

  const exportAsJSON = () => {
    const json = JSON.stringify(reportData, null, 2);
    downloadFile(json, "application/json", `${reportName}.json`);
  };

  const downloadFile = (content: string, type: string, filename: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center gap-2">
      <select
        value={format}
        onChange={(e) => setFormat(e.target.value as "csv" | "pdf")}
        disabled={exporting}
        className="rounded border border-gray-300 px-2 py-1 text-sm"
      >
        <option value="csv">CSV</option>
        <option value="pdf">PDF</option>
      </select>
      <Button
        onClick={handleExport}
        disabled={
          exporting || !reportData || Object.keys(reportData).length === 0
        }
        size="sm"
        className="gap-2"
      >
        <Download className="h-4 w-4" />
        {exporting ? "Exporting..." : "Export"}
      </Button>
    </div>
  );
};
