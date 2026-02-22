import { useState } from "react";
import {
  useGetAuditLogs,
  useGetAccessLogs,
  useGetAuditSummary,
  useGenerateComplianceReport,
} from "@/lib/api/hooks/useAccounting";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import { AlertCircle, DownloadIcon, Filter } from "@/components/icons";

export default function AuditTrailPage() {
  const [activeTab, setActiveTab] = useState("audit-logs");
  const [filters, setFilters] = useState({
    entity_type: "",
    user_id: "",
    action: "",
    start_date: "",
    end_date: "",
  });
  const [complianceFilters, setComplianceFilters] = useState({
    start_date: "",
    end_date: "",
  });

  // Queries
  const auditLogsQuery = useGetAuditLogs(filters);
  const accessLogsQuery = useGetAccessLogs(filters);
  const auditSummaryQuery = useGetAuditSummary();
  const complianceReportMutation = useGenerateComplianceReport();

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleGenerateComplianceReport = async () => {
    if (!complianceFilters.start_date || !complianceFilters.end_date) {
      showToast("Please select both start and end dates", "warning");
      return;
    }

    try {
      const report =
        await complianceReportMutation.mutateAsync(complianceFilters);
      // Download report as JSON
      const element = document.createElement("a");
      element.setAttribute(
        "href",
        "data:text/json;charset=utf-8," +
          encodeURIComponent(JSON.stringify(report, null, 2)),
      );
      element.setAttribute(
        "download",
        `compliance-report-${complianceFilters.start_date}-${complianceFilters.end_date}.json`,
      );
      element.style.display = "none";
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    } catch (error) {
      console.error("Error generating compliance report:", error);
      showToast("Failed to generate compliance report", "error");
    }
  };

  const getActionBadgeVariant = (action: string) => {
    switch (action.toLowerCase()) {
      case "create":
        return "success";
      case "update":
        return "default";
      case "delete":
        return "destructive";
      case "view":
        return "secondary";
      default:
        return "secondary";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Audit Trail & Compliance
        </h1>
        <p className="text-muted-foreground mt-2">
          Track all changes and access to accounting data
        </p>
      </div>

      {/* Summary Cards */}
      {auditSummaryQuery.data && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Audit Logs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {auditSummaryQuery.data.total_audit_logs}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Access Logs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {auditSummaryQuery.data.total_access_logs}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Users
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {auditSummaryQuery.data.active_users.length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Recent Changes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {auditSummaryQuery.data.recent_changes.length}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="audit-logs"
      >
        <TabsList>
          <TabsTrigger value="audit-logs">Audit Logs</TabsTrigger>
          <TabsTrigger value="access-logs">Access Logs</TabsTrigger>
          <TabsTrigger value="compliance">Compliance Report</TabsTrigger>
        </TabsList>

        {/* Audit Logs Tab */}
        <TabsContent value="audit-logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Logs</CardTitle>
              <CardDescription>
                View all changes made to accounting data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <Input
                  placeholder="Entity Type"
                  value={filters.entity_type}
                  onChange={(e) =>
                    handleFilterChange("entity_type", e.target.value)
                  }
                />
                <Input
                  placeholder="User ID"
                  value={filters.user_id}
                  onChange={(e) =>
                    handleFilterChange("user_id", e.target.value)
                  }
                />
                <Input
                  placeholder="Action"
                  value={filters.action}
                  onChange={(e) => handleFilterChange("action", e.target.value)}
                />
                <Input
                  placeholder="Start Date"
                  type="date"
                  value={filters.start_date}
                  onChange={(e) =>
                    handleFilterChange("start_date", e.target.value)
                  }
                />
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
              </div>

              {/* Logs Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-4">Timestamp</th>
                      <th className="text-left py-2 px-4">Entity</th>
                      <th className="text-left py-2 px-4">Action</th>
                      <th className="text-left py-2 px-4">User</th>
                      <th className="text-left py-2 px-4">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogsQuery.data?.map((log) => (
                      <tr key={log.id} className="border-b hover:bg-muted">
                        <td className="py-2 px-4 text-xs">
                          {format(
                            new Date(log.timestamp),
                            "MMM dd, yyyy HH:mm:ss",
                          )}
                        </td>
                        <td className="py-2 px-4">
                          <div className="text-xs">
                            <div className="font-medium">{log.entity_type}</div>
                            <div className="text-muted-foreground">
                              {log.entity_id}
                            </div>
                          </div>
                        </td>
                        <td className="py-2 px-4">
                          <Badge variant={getActionBadgeVariant(log.action)}>
                            {log.action}
                          </Badge>
                        </td>
                        <td className="py-2 px-4 text-xs">{log.user_id}</td>
                        <td className="py-2 px-4 text-xs text-muted-foreground">
                          {log.description}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {auditLogsQuery.isLoading && (
                <div className="text-center py-8 text-muted-foreground">
                  Loading audit logs...
                </div>
              )}

              {!auditLogsQuery.isLoading &&
                auditLogsQuery.data?.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No audit logs found
                  </div>
                )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Access Logs Tab */}
        <TabsContent value="access-logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Access Logs</CardTitle>
              <CardDescription>
                View all access to sensitive accounting data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <Input
                  placeholder="Entity Type"
                  value={filters.entity_type}
                  onChange={(e) =>
                    handleFilterChange("entity_type", e.target.value)
                  }
                />
                <Input
                  placeholder="User ID"
                  value={filters.user_id}
                  onChange={(e) =>
                    handleFilterChange("user_id", e.target.value)
                  }
                />
                <Input
                  placeholder="Start Date"
                  type="date"
                  value={filters.start_date}
                  onChange={(e) =>
                    handleFilterChange("start_date", e.target.value)
                  }
                />
                <Input
                  placeholder="End Date"
                  type="date"
                  value={filters.end_date}
                  onChange={(e) =>
                    handleFilterChange("end_date", e.target.value)
                  }
                />
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
              </div>

              {/* Logs Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left py-2 px-4">Timestamp</th>
                      <th className="text-left py-2 px-4">Entity</th>
                      <th className="text-left py-2 px-4">Access Type</th>
                      <th className="text-left py-2 px-4">User</th>
                      <th className="text-left py-2 px-4">IP Address</th>
                    </tr>
                  </thead>
                  <tbody>
                    {accessLogsQuery.data?.map((log) => (
                      <tr key={log.id} className="border-b hover:bg-muted">
                        <td className="py-2 px-4 text-xs">
                          {format(
                            new Date(log.timestamp),
                            "MMM dd, yyyy HH:mm:ss",
                          )}
                        </td>
                        <td className="py-2 px-4">
                          <div className="text-xs">
                            <div className="font-medium">{log.entity_type}</div>
                            <div className="text-muted-foreground">
                              {log.entity_id}
                            </div>
                          </div>
                        </td>
                        <td className="py-2 px-4">
                          <Badge variant="outline">{log.access_type}</Badge>
                        </td>
                        <td className="py-2 px-4 text-xs">{log.user_id}</td>
                        <td className="py-2 px-4 text-xs text-muted-foreground">
                          {log.ip_address || "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {accessLogsQuery.isLoading && (
                <div className="text-center py-8 text-muted-foreground">
                  Loading access logs...
                </div>
              )}

              {!accessLogsQuery.isLoading &&
                accessLogsQuery.data?.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No access logs found
                  </div>
                )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Report Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Report</CardTitle>
              <CardDescription>
                Generate compliance reports for audit periods
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Start Date
                  </label>
                  <Input
                    type="date"
                    value={complianceFilters.start_date}
                    onChange={(e) =>
                      setComplianceFilters((prev) => ({
                        ...prev,
                        start_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    End Date
                  </label>
                  <Input
                    type="date"
                    value={complianceFilters.end_date}
                    onChange={(e) =>
                      setComplianceFilters((prev) => ({
                        ...prev,
                        end_date: e.target.value,
                      }))
                    }
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={handleGenerateComplianceReport}
                    disabled={complianceReportMutation.isPending}
                    className="w-full"
                  >
                    <DownloadIcon className="w-4 h-4 mr-2" />
                    {complianceReportMutation.isPending
                      ? "Generating..."
                      : "Generate Report"}
                  </Button>
                </div>
              </div>

              {complianceReportMutation.error && (
                <Alert variant="error">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>
                    {complianceReportMutation.error.message}
                  </AlertDescription>
                </Alert>
              )}

              <Alert variant="info">
                <p className="text-sm">
                  Compliance reports include all audit logs, access logs, and
                  entity changes for the selected period. The report will be
                  downloaded as a JSON file.
                </p>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
