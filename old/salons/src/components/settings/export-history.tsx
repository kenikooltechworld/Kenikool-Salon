import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  DownloadIcon,
  ClockIcon,
  CheckIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useDataExports } from "@/lib/api/hooks/useSettings";

export function ExportHistory() {
  const { data: exports = [], isLoading } = useDataExports();

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100";
      case "processing":
        return "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100";
      case "failed":
        return "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100";
      default:
        return "bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckIcon size={16} />;
      case "processing":
        return <Spinner size="sm" />;
      case "failed":
        return <AlertTriangleIcon size={16} />;
      default:
        return <ClockIcon size={16} />;
    }
  };

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Export History
      </h2>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : exports.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No exports yet. Request one to get started.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {exports.map((exp) => (
            <div
              key={exp.id}
              className={`flex items-start justify-between p-4 rounded-lg border ${
                isExpired(exp.expires_at)
                  ? "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800"
                  : "bg-muted border-border"
              }`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      exp.status
                    )}`}
                  >
                    {getStatusIcon(exp.status)}
                    {exp.status.charAt(0).toUpperCase() + exp.status.slice(1)}
                  </span>
                </div>

                <div className="space-y-1 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <ClockIcon size={14} />
                    <span>Requested: {formatDate(exp.requested_at)}</span>
                  </div>
                  {exp.completed_at && (
                    <div className="flex items-center gap-2">
                      <CheckIcon size={14} />
                      <span>Completed: {formatDate(exp.completed_at)}</span>
                    </div>
                  )}
                  {exp.file_size && (
                    <div className="flex items-center gap-2">
                      <span>
                        Size: {(exp.file_size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </div>
                  )}
                  {exp.expires_at && (
                    <div className="flex items-center gap-2">
                      <span>
                        Expires: {formatDate(exp.expires_at)}
                        {isExpired(exp.expires_at) && " (Expired)"}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {exp.status === "completed" && exp.file_url && !isExpired(exp.expires_at) && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open(exp.file_url, "_blank")}
                  className="ml-4"
                >
                  <DownloadIcon size={16} className="mr-2" />
                  Download
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
