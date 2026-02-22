import { useMemo } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AlertTriangleIcon, CheckCircleIcon } from "@/components/icons";

export interface CsvPreviewTableProps {
  data: any[];
  errors?: Record<number, string[]>;
  maxRows?: number;
}

export function CsvPreviewTable({
  data,
  errors = {},
  maxRows = 10,
}: CsvPreviewTableProps) {
  const displayData = useMemo(() => data.slice(0, maxRows), [data, maxRows]);
  const columns = useMemo(() => {
    if (displayData.length === 0) return [];
    return Object.keys(displayData[0]);
  }, [displayData]);

  if (displayData.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No data to preview</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="text-sm text-muted-foreground">
        Showing {displayData.length} of {data.length} rows
      </div>
      <div className="border rounded-lg overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted">
              <TableHead className="w-12">Status</TableHead>
              {columns.map((col) => (
                <TableHead key={col} className="whitespace-nowrap">
                  {col}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayData.map((row, rowIdx) => {
              const rowErrors = errors[rowIdx] || [];
              const hasError = rowErrors.length > 0;

              return (
                <TableRow
                  key={rowIdx}
                  className={hasError ? "bg-red-50 dark:bg-red-950" : ""}
                >
                  <TableCell className="w-12">
                    {hasError ? (
                      <div
                        className="flex items-center justify-center"
                        title={rowErrors.join(", ")}
                      >
                        <AlertTriangleIcon
                          size={16}
                          className="text-red-600 dark:text-red-400"
                        />
                      </div>
                    ) : (
                      <CheckCircleIcon
                        size={16}
                        className="text-green-600 dark:text-green-400"
                      />
                    )}
                  </TableCell>
                  {columns.map((col) => (
                    <TableCell
                      key={`${rowIdx}-${col}`}
                      className="whitespace-nowrap text-sm"
                    >
                      <span className="text-foreground">
                        {String(row[col] || "").substring(0, 50)}
                      </span>
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
