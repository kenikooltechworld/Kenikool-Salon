import { useState } from "react";
import { useAuditLogs } from "@/hooks/useAuditLogs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { DownloadIcon, FilterIcon } from "@/components/icons";

export default function AuditLogs() {
  const {
    logs,
    logsTotal,
    isLoadingLogs,
    skip,
    setSkip,
    limit,
    exportAuditLogs,
  } = useAuditLogs();

  const [searchTerm, setSearchTerm] = useState("");
  const [filterEventType, setFilterEventType] = useState("");
  const [filterResource, setFilterResource] = useState("");

  const filteredLogs = logs.filter((log: any) => {
    const matchesSearch =
      log.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesEventType =
      !filterEventType || log.event_type === filterEventType;
    const matchesResource = !filterResource || log.resource === filterResource;
    return matchesSearch && matchesEventType && matchesResource;
  });

  const totalPages = Math.ceil(logsTotal / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  const getEventTypeColor = (eventType: string) => {
    if (eventType.includes("CREATE")) return "bg-green-100 text-green-800";
    if (eventType.includes("UPDATE")) return "bg-blue-100 text-blue-800";
    if (eventType.includes("DELETE")) return "bg-red-100 text-red-800";
    return "bg-gray-100 text-gray-800";
  };

  if (isLoadingLogs) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Audit Logs</h1>
          <p className="text-gray-600 mt-1">
            Track all system activities and changes
          </p>
        </div>
        <Button
          onClick={() =>
            exportAuditLogs({
              startDate: new Date(
                Date.now() - 30 * 24 * 60 * 60 * 1000,
              ).toISOString(),
              endDate: new Date().toISOString(),
            })
          }
          className="gap-2"
        >
          <DownloadIcon size={20} />
          Export
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <FilterIcon size={18} />
          <h3 className="font-semibold">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search by event type or resource..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Input
            placeholder="Filter by event type..."
            value={filterEventType}
            onChange={(e) => setFilterEventType(e.target.value)}
          />
          <Input
            placeholder="Filter by resource..."
            value={filterResource}
            onChange={(e) => setFilterResource(e.target.value)}
          />
        </div>
      </Card>

      {/* Logs Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  User
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Event Type
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Resource
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  IP Address
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.map((log: any) => (
                <tr key={log.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    {log.user_id || "System"}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <Badge className={getEventTypeColor(log.event_type)}>
                      {log.event_type}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-sm">{log.resource}</td>
                  <td className="px-6 py-4 text-sm">
                    {log.status_code >= 200 && log.status_code < 300 ? (
                      <Badge variant="outline" className="text-green-700">
                        Success
                      </Badge>
                    ) : (
                      <Badge variant="destructive">Failed</Badge>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {log.ip_address}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex justify-between items-center px-6 py-4 border-t bg-gray-50">
          <p className="text-sm text-gray-600">
            Page {currentPage} of {totalPages} ({logsTotal} total logs)
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSkip(skip + limit)}
              disabled={currentPage >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
