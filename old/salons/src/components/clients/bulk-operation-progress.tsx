import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckCircleIcon, AlertTriangleIcon, XCircleIcon } from "@/components/icons";

export interface BulkOperationProgressProps {
  isOpen: boolean;
  title: string;
  description?: string;
  status: "pending" | "in_progress" | "completed" | "error";
  progress?: number; // 0-100
  successCount?: number;
  failureCount?: number;
  totalCount?: number;
  errors?: Array<{ clientId: string; error: string }>;
}

/**
 * Modal showing progress of bulk operations
 * Displays real-time progress and results
 * 
 * Requirements: REQ-CM-011 (Task 27.3)
 */
export function BulkOperationProgress({
  isOpen,
  title,
  description,
  status,
  progress = 0,
  successCount = 0,
  failureCount = 0,
  totalCount = 0,
  errors = [],
}: BulkOperationProgressProps) {
  const isComplete = status === "completed" || status === "error";

  return (
    <Dialog open={isOpen}>
      <DialogContent className="max-w-md" showCloseButton={isComplete}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {status === "in_progress" && (
              <>
                <Spinner size="sm" />
                {title}
              </>
            )}
            {status === "completed" && (
              <>
                <CheckCircleIcon size={20} className="text-green-500" />
                {title}
              </>
            )}
            {status === "error" && (
              <>
                <XCircleIcon size={20} className="text-red-500" />
                {title}
              </>
            )}
            {status === "pending" && (
              <>
                <Spinner size="sm" />
                {title}
              </>
            )}
          </DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>

        <div className="space-y-4">
          {/* Progress Bar */}
          {status === "in_progress" && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}

          {/* Results Summary */}
          {isComplete && totalCount > 0 && (
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="rounded-lg bg-muted p-3">
                <div className="text-2xl font-bold text-foreground">
                  {totalCount}
                </div>
                <div className="text-xs text-muted-foreground">Total</div>
              </div>
              <div className="rounded-lg bg-green-50 dark:bg-green-950 p-3">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {successCount}
                </div>
                <div className="text-xs text-green-600 dark:text-green-400">
                  Success
                </div>
              </div>
              <div className="rounded-lg bg-red-50 dark:bg-red-950 p-3">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {failureCount}
                </div>
                <div className="text-xs text-red-600 dark:text-red-400">
                  Failed
                </div>
              </div>
            </div>
          )}

          {/* Status Messages */}
          {status === "pending" && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Spinner size="sm" />
              <span className="text-sm text-muted-foreground">
                Preparing operation...
              </span>
            </div>
          )}

          {status === "in_progress" && (
            <div className="flex items-center justify-center gap-2 py-2">
              <span className="text-sm text-muted-foreground">
                Processing {successCount + failureCount} of {totalCount}...
              </span>
            </div>
          )}

          {status === "completed" && (
            <Alert variant="success">
              <CheckCircleIcon size={16} />
              <div>
                Operation completed successfully. {successCount} client
                {successCount !== 1 ? "s" : ""} processed.
              </div>
            </Alert>
          )}

          {status === "error" && (
            <Alert variant="error">
              <AlertTriangleIcon size={16} />
              <div>
                Operation completed with errors. {failureCount} client
                {failureCount !== 1 ? "s" : ""} failed.
              </div>
            </Alert>
          )}

          {/* Error Details */}
          {errors.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-foreground">
                Failed Items ({errors.length})
              </div>
              <div className="max-h-40 space-y-1 overflow-y-auto rounded-lg bg-muted p-2">
                {errors.slice(0, 5).map((error, idx) => (
                  <div key={idx} className="text-xs text-muted-foreground">
                    <span className="font-mono">{error.clientId}:</span>{" "}
                    {error.error}
                  </div>
                ))}
                {errors.length > 5 && (
                  <div className="text-xs text-muted-foreground">
                    ... and {errors.length - 5} more
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
