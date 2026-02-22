import { AuditLogTimeline } from "@/components/settings/audit-log-timeline";
import { AuditLogFilters } from "@/components/settings/audit-log-filters";

export default function AuditLogPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Audit Log</h1>
        <p className="text-muted-foreground">
          View all security events and account activity
        </p>
      </div>

      {/* Filters */}
      <AuditLogFilters />

      {/* Timeline */}
      <AuditLogTimeline />
    </div>
  );
}
