import React, { useState } from "react";
import { AuditLogViewer } from "@/components/booking/audit-log-viewer";
import { AuditLogFilters } from "@/components/booking/audit-log-filters";
import { AuditLogExporter } from "@/components/booking/audit-log-exporter";
import { useAuditLog } from "@/lib/api/hooks/useAuditLog";

export default function AuditLogPage() {
  const [filters, setFilters] = useState({
    dateFrom: "",
    dateTo: "",
    action: "",
    userId: "",
  });

  const { auditLogs, loading } = useAuditLog(filters);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Booking Audit Log</h1>
        <AuditLogExporter logs={auditLogs} />
      </div>

      <AuditLogFilters filters={filters} onFiltersChange={setFilters} />

      <AuditLogViewer logs={auditLogs} loading={loading} />
    </div>
  );
}
