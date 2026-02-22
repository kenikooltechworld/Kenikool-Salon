"use client";

import { useState } from "react";
import { useExportReviews } from "@/lib/api/hooks/useClientReviews";
import type { ReviewFiltersParams } from "@/lib/api/hooks/useClientReviews";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { showToast } from "@/lib/utils/toast";
import { ChevronDownIcon, DownloadIcon } from "@/components/icons";

interface ExportButtonProps {
  filters?: ReviewFiltersParams;
  disabled?: boolean;
}

export function ExportButton({ filters, disabled = false }: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const exportMutation = useExportReviews();

  const handleExport = async (format: "csv" | "pdf") => {
    try {
      await exportMutation.mutateAsync({ format, filters });
      showToast(`Reviews exported as ${format.toUpperCase()}`, "success");
      setIsOpen(false);
    } catch (error: any) {
      showToast(
        error.message || `Failed to export as ${format.toUpperCase()}`,
        "error"
      );
    }
  };

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled || exportMutation.isPending}
        className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {exportMutation.isPending ? (
          <>
            <Spinner size="sm" />
            Exporting...
          </>
        ) : (
          <>
            <DownloadIcon size={16} />
            Export
            <ChevronDownIcon size={16} />
          </>
        )}
      </button>

      {isOpen && !exportMutation.isPending && (
        <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-md shadow-lg z-50">
          <button
            onClick={() => handleExport("csv")}
            className="w-full text-left px-4 py-2 hover:bg-gray-100 first:rounded-t-md transition-colors"
          >
            <div className="font-medium">Export as CSV</div>
            <div className="text-sm text-gray-600">Spreadsheet format</div>
          </button>
          <button
            onClick={() => handleExport("pdf")}
            className="w-full text-left px-4 py-2 hover:bg-gray-100 last:rounded-b-md transition-colors border-t border-gray-200"
          >
            <div className="font-medium">Export as PDF</div>
            <div className="text-sm text-gray-600">With summary statistics</div>
          </button>
        </div>
      )}
    </div>
  );
}
