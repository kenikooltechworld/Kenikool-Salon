import { useState } from "react";
import { useBackup } from "@/hooks/useBackup";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  DownloadIcon,
  RefreshCwIcon,
  PlusIcon,
  CheckCircleIcon,
  AlertCircleIcon,
} from "@/components/icons";

export default function Backups() {
  const {
    backups,
    backupsTotal,
    isLoadingBackups,
    createBackup,
    verifyBackup,
    skip,
    setSkip,
    limit,
  } = useBackup();

  const [isCreating, setIsCreating] = useState(false);

  const totalPages = Math.ceil(backupsTotal / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  const handleCreateBackup = async () => {
    setIsCreating(true);
    try {
      createBackup("full");
    } finally {
      setIsCreating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "in_progress":
        return "bg-blue-100 text-blue-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoadingBackups) {
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
          <h1 className="text-3xl font-bold">Backup Management</h1>
          <p className="text-gray-600 mt-1">
            Create and manage database backups
          </p>
        </div>
        <Button
          onClick={handleCreateBackup}
          disabled={isCreating}
          className="gap-2"
        >
          <PlusIcon size={20} />
          {isCreating ? "Creating..." : "Create Backup"}
        </Button>
      </div>

      {/* Backup Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-sm text-gray-600">Total Backups</p>
          <p className="text-3xl font-bold">{backupsTotal}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-600">Completed</p>
          <p className="text-3xl font-bold">
            {backups.filter((b: any) => b.status === "completed").length}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-600">Failed</p>
          <p className="text-3xl font-bold">
            {backups.filter((b: any) => b.status === "failed").length}
          </p>
        </Card>
      </div>

      {/* Backups List */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Backup ID
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Encryption
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {backups.map((backup: any) => (
                <tr key={backup.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">{backup.id}</td>
                  <td className="px-6 py-4 text-sm">
                    {new Date(backup.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {((backup.size_bytes || 0) / 1024 / 1024).toFixed(2)} MB
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <Badge className={getStatusColor(backup.status)}>
                      {backup.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {backup.encryption_key_id ? (
                      <div className="flex items-center gap-1 text-green-700">
                        <CheckCircleIcon size={16} />
                        Encrypted
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 text-yellow-700">
                        <AlertCircleIcon size={16} />
                        Not Encrypted
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => verifyBackup(backup.id)}
                      >
                        <RefreshCwIcon size={16} />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <DownloadIcon size={16} />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex justify-between items-center px-6 py-4 border-t bg-gray-50">
          <p className="text-sm text-gray-600">
            Page {currentPage} of {totalPages} ({backupsTotal} total backups)
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
