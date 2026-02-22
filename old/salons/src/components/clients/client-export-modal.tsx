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
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon, DownloadIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";

export interface ClientExportModalProps {
  isOpen: boolean;
  selectedClientIds?: string[];
  onClose: () => void;
}

const DEFAULT_FIELDS = [
  { id: "id", label: "Client ID", checked: true },
  { id: "name", label: "Name", checked: true },
  { id: "phone", label: "Phone", checked: true },
  { id: "email", label: "Email", checked: true },
  { id: "address", label: "Address", checked: false },
  { id: "birthday", label: "Birthday", checked: false },
  { id: "segment", label: "Segment", checked: true },
  { id: "tags", label: "Tags", checked: false },
  { id: "total_visits", label: "Total Visits", checked: true },
  { id: "total_spent", label: "Total Spent", checked: true },
  { id: "last_visit_date", label: "Last Visit Date", checked: true },
  { id: "preferred_stylist_id", label: "Preferred Stylist", checked: false },
  { id: "notes", label: "Notes", checked: false },
];

export function ClientExportModal({
  isOpen,
  selectedClientIds,
  onClose,
}: ClientExportModalProps) {
  const [fields, setFields] = useState(DEFAULT_FIELDS);
  const [error, setError] = useState<string | null>(null);

  const exportClients = useMutation({
    mutationFn: async () => {
      const selectedFields = fields
        .filter((f) => f.checked)
        .map((f) => f.id);

      const response = await apiClient.get("/clients/export", {
        params: {
          client_ids: selectedClientIds,
          fields: selectedFields,
        },
        responseType: "blob",
      });

      return response.data;
    },
    onSuccess: (data) => {
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `clients-${new Date().toISOString().split("T")[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.error?.message || "Failed to export clients");
    },
  });

  const handleToggleField = (fieldId: string) => {
    setFields(
      fields.map((f) =>
        f.id === fieldId ? { ...f, checked: !f.checked } : f
      )
    );
  };

  const handleSelectAll = () => {
    const allChecked = fields.every((f) => f.checked);
    setFields(fields.map((f) => ({ ...f, checked: !allChecked })));
  };

  const checkedCount = fields.filter((f) => f.checked).length;
  const allChecked = checkedCount === fields.length;

  const handleExport = () => {
    if (checkedCount === 0) {
      setError("Please select at least one field to export");
      return;
    }
    setError(null);
    exportClients.mutate();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Export Clients</DialogTitle>
          <DialogDescription>
            Select fields to include in the CSV export
            {selectedClientIds && selectedClientIds.length > 0
              ? ` (${selectedClientIds.length} selected)`
              : " (all clients)"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Select All */}
          <div className="flex items-center gap-2 pb-2 border-b">
            <Checkbox
              checked={allChecked}
              onCheckedChange={handleSelectAll}
              id="select-all"
            />
            <Label htmlFor="select-all" className="font-medium cursor-pointer">
              Select All ({checkedCount}/{fields.length})
            </Label>
          </div>

          {/* Field Selection */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {fields.map((field) => (
              <div key={field.id} className="flex items-center gap-2">
                <Checkbox
                  checked={field.checked}
                  onCheckedChange={() => handleToggleField(field.id)}
                  id={field.id}
                />
                <Label htmlFor={field.id} className="cursor-pointer">
                  {field.label}
                </Label>
              </div>
            ))}
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="error">
              <AlertTriangleIcon size={16} />
              <div>{error}</div>
            </Alert>
          )}

          {/* Loading State */}
          {exportClients.isPending && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Spinner size="sm" />
              <span className="text-sm text-muted-foreground">
                Preparing export...
              </span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={exportClients.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={exportClients.isPending || checkedCount === 0}
            className="gap-2"
          >
            <DownloadIcon size={16} />
            {exportClients.isPending ? "Exporting..." : "Export CSV"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
