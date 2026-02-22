import React from "react";
import { format } from "date-fns";
import { User, Clock } from "lucide-react";

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

interface AuditLogViewerProps {
  entries: AuditLogEntry[];
  loading?: boolean;
}

export const AuditLogViewer: React.FC<AuditLogViewerProps> = ({
  entries,
  loading = false,
}) => {
  if (loading) {
    return <div className="text-sm text-gray-500">Loading audit log...</div>;
  }

  if (!entries || entries.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
        No audit log entries found
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="font-medium text-gray-900">Audit Log</h3>
      <div className="space-y-2">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="rounded-lg border border-gray-200 bg-white p-3 space-y-2"
          >
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {entry.user}
                  </p>
                  <p className="text-xs text-gray-600">{entry.action}</p>
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <Clock className="h-3 w-3" />
                {format(new Date(entry.timestamp), "MMM dd, yyyy h:mm a")}
              </div>
            </div>

            {/* Changes */}
            {entry.changes.length > 0 && (
              <div className="space-y-1 pl-6 border-l-2 border-gray-200">
                {entry.changes.map((change, idx) => (
                  <div key={idx} className="text-xs">
                    <p className="font-medium text-gray-900">{change.field}</p>
                    <p className="text-gray-600">
                      {change.oldValue} → {change.newValue}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Reason */}
            {entry.reason && (
              <div className="text-xs text-gray-600 bg-gray-50 rounded p-2">
                <span className="font-medium">Reason:</span> {entry.reason}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
