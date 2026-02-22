import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  PlusIcon,
  TrashIcon,
  EditIcon,
  PauseIcon,
  PlayIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
} from "@/components/icons";

interface ScheduledExport {
  export_id: string;
  name: string;
  format: "csv" | "json" | "excel" | "pdf";
  schedule: "daily" | "weekly" | "monthly";
  recipients: string[];
  status: "active" | "paused";
  created_at: string;
  next_run: string;
  last_run?: string;
  run_count: number;
}

interface ScheduledExportManagerProps {
  onExportCreated?: (exportId: string) => void;
  onExportDeleted?: (exportId: string) => void;
}

export function ScheduledExportManager({
  onExportCreated,
  onExportDeleted,
}: ScheduledExportManagerProps) {
  const [exports, setExports] = useState<ScheduledExport[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingExport, setEditingExport] = useState<ScheduledExport | null>(
    null
  );

  const [formData, setFormData] = useState({
    name: "",
    format: "csv" as const,
    schedule: "daily" as const,
    recipients: "",
  });

  useEffect(() => {
    loadExports();
  }, []);

  const loadExports = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/analytics/exports/scheduled');
      // const data = await response.json();
      // setExports(data);
      setExports([]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load exports"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateExport = async () => {
    try {
      if (!formData.name.trim()) {
        throw new Error("Export name is required");
      }
      if (!formData.recipients.trim()) {
        throw new Error("At least one recipient is required");
      }

      const recipients = formData.recipients
        .split(",")
        .map((r) => r.trim())
        .filter((r) => r);

      // TODO: Replace with actual API call
      // const response = await fetch('/api/analytics/exports/scheduled', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({
      //     name: formData.name,
      //     format: formData.format,
      //     schedule: formData.schedule,
      //     recipients
      //   })
      // });

      const newExport: ScheduledExport = {
        export_id: `export_${Date.now()}`,
        name: formData.name,
        format: formData.format,
        schedule: formData.schedule,
        recipients,
        status: "active",
        created_at: new Date().toISOString(),
        next_run: new Date().toISOString(),
        run_count: 0,
      };

      setExports([...exports, newExport]);
      setFormData({ name: "", format: "csv", schedule: "daily", recipients: "" });
      setShowCreateModal(false);

      if (onExportCreated) {
        onExportCreated(newExport.export_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create export");
    }
  };

  const handleDeleteExport = async (exportId: string) => {
    if (!confirm("Are you sure you want to delete this scheduled export?")) {
      return;
    }

    try {
      // TODO: Replace with actual API call
      // await fetch(`/api/analytics/exports/scheduled/${exportId}`, {
      //   method: 'DELETE'
      // });

      setExports(exports.filter((e) => e.export_id !== exportId));

      if (onExportDeleted) {
        onExportDeleted(exportId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete export");
    }
  };

  const handleToggleStatus = async (exportId: string) => {
    try {
      const exportToUpdate = exports.find((e) => e.export_id === exportId);
      if (!exportToUpdate) return;

      const newStatus = exportToUpdate.status === "active" ? "paused" : "active";

      // TODO: Replace with actual API call
      // await fetch(`/api/analytics/exports/scheduled/${exportId}`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ status: newStatus })
      // });

      setExports(
        exports.map((e) =>
          e.export_id === exportId ? { ...e, status: newStatus } : e
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update export");
    }
  };

  const formatSchedule = (schedule: string) => {
    const schedules: Record<string, string> = {
      daily: "Every day",
      weekly: "Every week",
      monthly: "Every month",
    };
    return schedules[schedule] || schedule;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-foreground">
          Scheduled Exports
        </h2>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="gap-2"
        >
          <PlusIcon size={20} />
          New Export
        </Button>
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Spinner />
        </div>
      ) : exports.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No scheduled exports yet</p>
          <p className="text-sm">Create one to automate your data exports</p>
        </div>
      ) : (
        <div className="space-y-2">
          {exports.map((exportItem) => (
            <div
              key={exportItem.export_id}
              className="flex items-center justify-between p-4 border border-[var(--border)] rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex-1">
                <h3 className="font-medium text-foreground">
                  {exportItem.name}
                </h3>
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <span className="inline-block w-2 h-2 rounded-full bg-blue-500"></span>
                    {exportItem.format.toUpperCase()}
                  </span>
                  <span>{formatSchedule(exportItem.schedule)}</span>
                  <span>Next: {formatDate(exportItem.next_run)}</span>
                  {exportItem.last_run && (
                    <span>Last: {formatDate(exportItem.last_run)}</span>
                  )}
                  <span>{exportItem.run_count} runs</span>
                </div>
                <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                  <span>Recipients:</span>
                  {exportItem.recipients.map((recipient, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-muted rounded"
                    >
                      {recipient}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleToggleStatus(exportItem.export_id)}
                  className={`p-2 rounded transition-colors ${
                    exportItem.status === "active"
                      ? "text-yellow-600 hover:bg-yellow-50"
                      : "text-green-600 hover:bg-green-50"
                  }`}
                  title={
                    exportItem.status === "active"
                      ? "Pause export"
                      : "Resume export"
                  }
                >
                  {exportItem.status === "active" ? (
                    <PauseIcon size={20} />
                  ) : (
                    <PlayIcon size={20} />
                  )}
                </button>

                <button
                  onClick={() => setEditingExport(exportItem)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  title="Edit export"
                >
                  <EditIcon size={20} />
                </button>

                <button
                  onClick={() => handleDeleteExport(exportItem.export_id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Delete export"
                >
                  <TrashIcon size={20} />
                </button>
              </div>

              <div className="ml-4">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    exportItem.status === "active"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {exportItem.status === "active" ? "Active" : "Paused"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        open={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setEditingExport(null);
        }}
        title="Create Scheduled Export"
        description="Set up automatic data exports"
        size="md"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Export Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Monthly Revenue Report"
              className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Format
            </label>
            <select
              value={formData.format}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  format: e.target.value as ExportFormat,
                })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
            >
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="excel">Excel</option>
              <option value="pdf">PDF</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Schedule
            </label>
            <select
              value={formData.schedule}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  schedule: e.target.value as ScheduleType,
                })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Recipients (comma-separated emails)
            </label>
            <textarea
              value={formData.recipients}
              onChange={(e) =>
                setFormData({ ...formData, recipients: e.target.value })
              }
              placeholder="user1@example.com, user2@example.com"
              rows={3}
              className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateModal(false);
                setEditingExport(null);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateExport}>
              <CheckCircleIcon size={20} />
              Create Export
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

type ExportFormat = "csv" | "json" | "excel" | "pdf";
type ScheduleType = "daily" | "weekly" | "monthly";
