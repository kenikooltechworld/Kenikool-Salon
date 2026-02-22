import { DataExportRequest } from "@/components/settings/data-export-request";
import { ExportHistory } from "@/components/settings/export-history";
import { AccountDeletionFlow } from "@/components/settings/account-deletion-flow";

export default function DataManagementPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Data Management</h1>
        <p className="text-muted-foreground">
          Export your data, manage account deletion, and control data retention
        </p>
      </div>

      {/* Data Export */}
      <DataExportRequest />

      {/* Export History */}
      <ExportHistory />

      {/* Account Deletion */}
      <AccountDeletionFlow />
    </div>
  );
}
