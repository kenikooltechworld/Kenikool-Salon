import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  AlertTriangleIcon,
  UploadIcon,
  CheckCircleIcon,
} from "@/components/icons";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiClient } from "@/lib/api/client";

export interface ClientImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function ClientImportModal({
  isOpen,
  onClose,
  onSuccess,
}: ClientImportModalProps) {
  const [csvContent, setCsvContent] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [duplicateHandling, setDuplicateHandling] = useState<
    "skip" | "update" | "create"
  >("skip");
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);

  const previewImport = useMutation({
    mutationFn: async (content: string) => {
      const response = await apiClient.post("/clients/import/preview", {
        csv_content: content,
        duplicate_handling: duplicateHandling,
      });
      return response.data;
    },
    onSuccess: (data) => {
      setPreviewData(data);
      setError(null);
    },
    onError: (err: any) => {
      setError(err.response?.data?.error?.message || "Failed to preview import");
      setPreviewData(null);
    },
  });

  const importClients = useMutation({
    mutationFn: async () => {
      if (!csvContent) throw new Error("No CSV content");
      const response = await apiClient.post("/clients/import", {
        csv_content: csvContent,
        duplicate_handling: duplicateHandling,
      });
      return response.data;
    },
    onSuccess: () => {
      setCsvContent(null);
      setFileName(null);
      setPreviewData(null);
      onSuccess?.();
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.error?.message || "Failed to import clients");
    },
  });

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".csv")) {
      setError("Please select a CSV file");
      return;
    }

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setCsvContent(content);
      previewImport.mutate(content);
    };
    reader.onerror = () => {
      setError("Failed to read file");
    };
    reader.readAsText(file);
  };

  const handleImport = () => {
    if (!csvContent) {
      setError("Please select a CSV file");
      return;
    }
    setError(null);
    importClients.mutate();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Import Clients</DialogTitle>
          <DialogDescription>
            Upload a CSV file to import clients into the system
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Upload */}
          {!csvContent ? (
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <UploadIcon size={32} className="mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm font-medium mb-2">
                Drag and drop your CSV file here
              </p>
              <p className="text-xs text-muted-foreground mb-4">
                or click to select a file
              </p>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
                id="csv-upload"
              />
              <Button
                variant="outline"
                onClick={() => document.getElementById("csv-upload")?.click()}
              >
                Select CSV File
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* File Info */}
              <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                <CheckCircleIcon size={20} className="text-green-600" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-900 dark:text-green-100">
                    {fileName}
                  </p>
                  <p className="text-xs text-green-700 dark:text-green-200">
                    File loaded successfully
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setCsvContent(null);
                    setFileName(null);
                    setPreviewData(null);
                  }}
                >
                  Change
                </Button>
              </div>

              {/* Duplicate Handling */}
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  If duplicate clients found:
                </label>
                <Select
                  value={duplicateHandling}
                  onValueChange={(v: any) => {
                    setDuplicateHandling(v);
                    if (csvContent) {
                      previewImport.mutate(csvContent);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="skip">Skip duplicates</SelectItem>
                    <SelectItem value="update">Update existing clients</SelectItem>
                    <SelectItem value="create">Create new records</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Preview Data */}
              {previewData && (
                <div className="space-y-2">
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="rounded-lg bg-muted p-2">
                      <div className="text-lg font-bold">
                        {previewData.total_rows}
                      </div>
                      <div className="text-xs text-muted-foreground">Total Rows</div>
                    </div>
                    <div className="rounded-lg bg-green-50 dark:bg-green-950 p-2">
                      <div className="text-lg font-bold text-green-600 dark:text-green-400">
                        {previewData.valid_rows}
                      </div>
                      <div className="text-xs text-green-600 dark:text-green-400">
                        Valid
                      </div>
                    </div>
                    <div className="rounded-lg bg-red-50 dark:bg-red-950 p-2">
                      <div className="text-lg font-bold text-red-600 dark:text-red-400">
                        {previewData.invalid_rows}
                      </div>
                      <div className="text-xs text-red-600 dark:text-red-400">
                        Invalid
                      </div>
                    </div>
                  </div>

                  {/* Errors */}
                  {previewData.errors && previewData.errors.length > 0 && (
                    <div className="space-y-1 max-h-32 overflow-y-auto rounded-lg bg-red-50 dark:bg-red-950 p-2">
                      {previewData.errors.slice(0, 5).map((err: string, idx: number) => (
                        <p key={idx} className="text-xs text-red-600 dark:text-red-400">
                          {err}
                        </p>
                      ))}
                      {previewData.errors.length > 5 && (
                        <p className="text-xs text-red-600 dark:text-red-400">
                          ... and {previewData.errors.length - 5} more errors
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <Alert variant="error">
              <AlertTriangleIcon size={16} />
              <div>{error}</div>
            </Alert>
          )}

          {/* Loading State */}
          {(previewImport.isPending || importClients.isPending) && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Spinner size="sm" />
              <span className="text-sm text-muted-foreground">
                {previewImport.isPending ? "Previewing..." : "Importing..."}
              </span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={previewImport.isPending || importClients.isPending}
          >
            Cancel
          </Button>
          {csvContent && (
            <Button
              onClick={handleImport}
              disabled={
                previewImport.isPending ||
                importClients.isPending ||
                (previewData && previewData.valid_rows === 0)
              }
            >
              {importClients.isPending ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Importing...
                </>
              ) : (
                "Import Clients"
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
