import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckCircleIcon,
  XIcon,
  ClockIcon,
  GiftIcon,
  UsersIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";

interface AutomationHistoryRecord {
  _id: string;
  automation_type: "birthday" | "winback" | "post_visit";
  campaign_id: string;
  recipients_count: number;
  sent_count: number;
  failed_count: number;
  status: "pending" | "completed" | "failed";
  executed_at: string;
  completed_at?: string;
}

export function AutomationHistory() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState<AutomationHistoryRecord[]>([]);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);

  const limit = 10;

  useEffect(() => {
    loadHistory();
  }, [skip]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get("/api/campaign-automation/history", {
        params: { skip, limit },
      });
      if (response.data) {
        setHistory(response.data.history || []);
        setTotal(response.data.total || 0);
      }
    } catch (error) {
      console.error("Failed to load automation history:", error);
      toast({
        title: "Error",
        description: "Failed to load automation history",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getAutomationIcon = (type: string) => {
    switch (type) {
      case "birthday":
        return <GiftIcon size={20} className="text-primary" />;
      case "winback":
        return <UsersIcon size={20} className="text-primary" />;
      case "post_visit":
        return <ClockIcon size={20} className="text-primary" />;
      default:
        return <ClockIcon size={20} className="text-primary" />;
    }
  };

  const getAutomationLabel = (type: string) => {
    switch (type) {
      case "birthday":
        return "Birthday Campaign";
      case "winback":
        return "Win-Back Campaign";
      case "post_visit":
        return "Post-Visit Campaign";
      default:
        return "Campaign";
    }
  };

  const getStatusBadge = (status: string, sentCount: number, failedCount: number) => {
    if (status === "completed") {
      if (failedCount === 0) {
        return (
          <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
            <CheckCircleIcon size={14} className="mr-1" />
            Success
          </Badge>
        );
      } else if (sentCount > 0) {
        return (
          <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">
            <ClockIcon size={14} className="mr-1" />
            Partial
          </Badge>
        );
      } else {
        return (
          <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
            <XIcon size={14} className="mr-1" />
            Failed
          </Badge>
        );
      }
    } else if (status === "pending") {
      return (
        <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">
          <Spinner size="sm" className="mr-1" />
          Pending
        </Badge>
      );
    } else {
      return (
        <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
          <XIcon size={14} className="mr-1" />
          Failed
        </Badge>
      );
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const successRate = (sent: number, total: number) => {
    if (total === 0) return "0%";
    return `${((sent / total) * 100).toFixed(1)}%`;
  };

  if (loading && history.length === 0) {
    return (
      <Card className="p-12 text-center">
        <Spinner size="lg" />
        <p className="text-muted-foreground mt-4">Loading automation history...</p>
      </Card>
    );
  }

  if (history.length === 0) {
    return (
      <Card className="p-12 text-center">
        <ClockIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">
          No automation history yet
        </h3>
        <p className="text-muted-foreground">
          Automation campaigns will appear here once they run
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* History List */}
      <div className="space-y-3">
        {history.map((record) => (
          <Card key={record._id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className="p-2 bg-primary/10 rounded-lg mt-1">
                    {getAutomationIcon(record.automation_type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold text-foreground">
                        {getAutomationLabel(record.automation_type)}
                      </h4>
                      {getStatusBadge(
                        record.status,
                        record.sent_count,
                        record.failed_count
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      Executed: {formatDate(record.executed_at)}
                    </p>

                    {/* Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="bg-muted/50 rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-1">
                          Total Recipients
                        </p>
                        <p className="text-lg font-semibold text-foreground">
                          {record.recipients_count}
                        </p>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-1">
                          Sent
                        </p>
                        <p className="text-lg font-semibold text-green-600">
                          {record.sent_count}
                        </p>
                      </div>
                      <div className="bg-red-50 rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-1">
                          Failed
                        </p>
                        <p className="text-lg font-semibold text-red-600">
                          {record.failed_count}
                        </p>
                      </div>
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs text-muted-foreground mb-1">
                          Success Rate
                        </p>
                        <p className="text-lg font-semibold text-blue-600">
                          {successRate(record.sent_count, record.recipients_count)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {total > limit && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sm text-muted-foreground">
            Showing {skip + 1} to {Math.min(skip + limit, total)} of {total}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
              className="px-4 py-2 rounded-lg border border-input hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={() => setSkip(skip + limit)}
              disabled={skip + limit >= total}
              className="px-4 py-2 rounded-lg border border-input hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
