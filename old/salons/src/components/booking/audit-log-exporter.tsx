import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

interface AuditLogEntry {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  changes: Array<{
    field: string;
    oldValue: any;
    newValue: any;
  }>;
  reason?: string;
}

interface AuditLogExporterProps {
  entries: AuditLogEntry[];
  bookingId?: string;
}

export const AuditLogExporter: React.FC<AuditLogExporterProps> = ({
  entries,
  bookingId,
}) => {
  const [exporting, setExporting] = useState(false);
  const [format, setFormat] = useState<"csv" | "json">("csv");

  const handleExport = async () => {
    setExporting(true);

    try {
      if (format === "csv") {
        exportAsCSV();
      } else {
        exportAsJSON();
      }
    } finally {
      setExporting(false);
    }
  };

  const exportAsCSV = () => {
    const headers = [
      "Timestamp",
      "User",
      "Action",
      "Field",
      "Old Value",
      "New Value",
      "Reason",
    ];
    const rows: string[][] = [];

    entries.forEach((entry) => {
      if (entry.changes.length === 0) {
        rows.push([
          entry.timestamp,
          entry.user,
          entry.action,
          "",
          "",
          "",
          entry.reason || "",
        ]);
      } else {
        entry.changes.forEach((change) => {
          rows.push([
            entry.timestamp,
            entry.user,
            entry.action,
            change.field,
            String(change.oldValue),
            String(change.newValue),
            entry.reason || "",
          ]);
        });
      }
    });

    const csv = [
      headers.join(","),
      ...rows.map((row) =>
        row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(","),
      ),
    ].join("\n");

    downloadFile(csv, "text/csv", "audit-log.csv");
  };

  const exportAsJSON = () => {
    const json = JSON.stringify(entries, null, 2);
    downloadFile(json, "application/json", "audit-log.json");
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
        onChange={(e) => setFormat(e.target.value as "csv" | "json")}
        disabled={exporting}
        className="rounded border border-gray-300 px-2 py-1 text-sm"
      >
        <option value="csv">CSV</option>
        <option value="json">JSON</option>
      </select>
      <Button
        onClick={handleExport}
        disabled={exporting || entries.length === 0}
        size="sm"
        className="gap-2"
      >
        <Download className="h-4 w-4" />
        {exporting ? "Exporting..." : "Export"}
      </Button>
    </div>
  );
};
