import { useMemo } from "react";
import { Alert } from "@/components/ui/alert";
import {
  AlertTriangleIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "@/components/icons";

export interface ValidationError {
  row: number;
  field: string;
  message: string;
}

export interface ImportValidationUIProps {
  totalRows: number;
  validRows: number;
  invalidRows: number;
  errors?: ValidationError[];
  maxErrorsToShow?: number;
}

export function ImportValidationUI({
  totalRows,
  validRows,
  invalidRows,
  errors = [],
  maxErrorsToShow = 10,
}: ImportValidationUIProps) {
  const displayErrors = useMemo(
    () => errors.slice(0, maxErrorsToShow),
    [errors, maxErrorsToShow]
  );

  const successRate = totalRows > 0 ? (validRows / totalRows) * 100 : 0;
  const isValid = invalidRows === 0;

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircleIcon size={16} className="text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">
              Total Rows
            </span>
          </div>
          <div className="text-2xl font-bold text-foreground">{totalRows}</div>
        </div>

        <div className="rounded-lg border border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950 p-3">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircleIcon size={16} className="text-green-600 dark:text-green-400" />
            <span className="text-xs font-medium text-green-600 dark:text-green-400">
              Valid
            </span>
          </div>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {validRows}
          </div>
        </div>

        <div className={`rounded-lg border p-3 ${
          invalidRows > 0
            ? "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950"
            : "border-muted bg-muted"
        }`}>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangleIcon
              size={16}
              className={
                invalidRows > 0
                  ? "text-red-600 dark:text-red-400"
                  : "text-muted-foreground"
              }
            />
            <span
              className={`text-xs font-medium ${
                invalidRows > 0
                  ? "text-red-600 dark:text-red-400"
                  : "text-muted-foreground"
              }`}
            >
              Invalid
            </span>
          </div>
          <div
            className={`text-2xl font-bold ${
              invalidRows > 0
                ? "text-red-600 dark:text-red-400"
                : "text-muted-foreground"
            }`}
          >
            {invalidRows}
          </div>
        </div>
      </div>

      {/* Success Rate Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-foreground">
            Success Rate
          </span>
          <span className="text-sm font-bold text-foreground">
            {successRate.toFixed(1)}%
          </span>
        </div>
        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              successRate >= 80
                ? "bg-green-500"
                : successRate >= 50
                ? "bg-yellow-500"
                : "bg-red-500"
            }`}
            style={{ width: `${successRate}%` }}
          />
        </div>
      </div>

      {/* Validation Status Alert */}
      {isValid ? (
        <Alert variant="success">
          <CheckCircleIcon size={16} />
          <div>
            <h4 className="font-semibold">All rows are valid</h4>
            <p className="text-sm">Ready to import {totalRows} clients</p>
          </div>
        </Alert>
      ) : (
        <Alert variant="warning">
          <AlertTriangleIcon size={16} />
          <div>
            <h4 className="font-semibold">
              {invalidRows} row{invalidRows !== 1 ? "s" : ""} have errors
            </h4>
            <p className="text-sm">
              {validRows} valid row{validRows !== 1 ? "s" : ""} will be imported
            </p>
          </div>
        </Alert>
      )}

      {/* Error Details */}
      {displayErrors.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-foreground">
            Validation Errors
          </h4>
          <div className="space-y-1 max-h-48 overflow-y-auto rounded-lg border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950 p-3">
            {displayErrors.map((error, idx) => (
              <div
                key={idx}
                className="text-xs text-red-600 dark:text-red-400 flex gap-2"
              >
                <span className="font-medium flex-shrink-0">
                  Row {error.row}:
                </span>
                <span>
                  {error.field} - {error.message}
                </span>
              </div>
            ))}
            {errors.length > maxErrorsToShow && (
              <div className="text-xs text-red-600 dark:text-red-400 font-medium pt-2 border-t border-red-200 dark:border-red-800">
                ... and {errors.length - maxErrorsToShow} more errors
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
