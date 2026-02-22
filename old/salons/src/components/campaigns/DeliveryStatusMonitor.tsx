import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckCircleIcon,
  XIcon,
  ClockIcon,
  AlertCircleIcon,
  RefreshCwIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";

interface DeliveryStatusMonitorProps {
  campaignId: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface DeliveryStatus {
  campaign_id: string;
  total_messages: number;
  status_breakdown: {
    pending: number;
    sending: number;
    delivered: number;
    failed: number;
  };
  failures: Array<{
    recipient_id: string;
    recipient_name: string;
    recipient_contact: string;
    channel: string;
    error_code: string;
    error_message: string;
    timestamp: string;
    retryable: boolean;
  }>;
  progress_percentage: number;
  estimated_completion: string;
}

export function DeliveryStatusMonitor({
  campaignId,
  autoRefresh = true,
  refreshInterval = 5000,
}: DeliveryStatusMonitorProps) {
  const { toast } = useToast();
  const [status, setStatus] = useState<DeliveryStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [showFailures, setShowFailures] = useState(false);

  useEffect(() => {
    loadStatus();

    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadStatus();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [campaignId, autoRefresh, refreshInterval]);

  const loadStatus = async () => {
    try {
      if (!loading) setRefreshing(true);
      const response = await apiClient.get(
        `/api/campaigns/${campaignId}/delivery-status`
      );
      setStatus(response.data);
    } catch (error) {
      console.error("Failed to load delivery status:", error);
      if (loading) {
        toast({
          title: "Error",
          description: "Failed to load delivery status",
          variant: "destructive",
        });
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRetryFailed = async () => {
    try {
      setRetrying(true);
      await apiClient.post(`/api/campaigns/${campaignId}/retry-failed`);
      toast({
        title: "Success",
        description: "Retry initiated for failed messages",
      });
      await loadStatus();
    } catch (error) {
      console.error("Failed to retry messages:", error);
      toast({
        title: "Error",
        description: "Failed to retry messages",
        variant: "destructive",
      });
    } finally {
      setRetrying(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-12 text-center">
        <Spinner size="lg" />
        <p className="text-muted-foreground mt-4">Loading delivery status...</p>
      </Card>
    );
  }

  if (!status) {
    return (
      <Card className="p-12 text-center">
        <XIcon size={48} className="mx-auto text-red-500 mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Failed to load delivery status
        </h3>
      </Card>
    );
  }

  const { status_breakdown, failures, progress_percentage } = status;
  const totalProcessed =
    status_breakdown.delivered + status_breakdown.failed + status_breakdown.sending;
  const isComplete = status_breakdown.pending === 0 && status_breakdown.sending === 0;

  return (
    <div className="space-y-6">
      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Delivery Progress</CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={loadStatus}
              disabled={refreshing}
            >
              <RefreshCwIcon
                size={16}
                className={refreshing ? "animate-spin" : ""}
              />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium text-foreground">
                Overall Progress
              </span>
              <span className="text-sm font-semibold text-foreground">
                {progress_percentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-green-500 h-full transition-all duration-500"
                style={{ width: `${progress_percentage}%` }}
              />
            </div>
          </div>

          {/* Status Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <ClockIcon size={18} className="text-blue-600" />
                <p className="text-sm text-muted-foreground">Pending</p>
              </div>
              <p className="text-2xl font-bold text-blue-600">
                {status_breakdown.pending}
              </p>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Spinner size="sm" className="text-yellow-600" />
                <p className="text-sm text-muted-foreground">Sending</p>
              </div>
              <p className="text-2xl font-bold text-yellow-600">
                {status_breakdown.sending}
              </p>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircleIcon size={18} className="text-green-600" />
                <p className="text-sm text-muted-foreground">Delivered</p>
              </div>
              <p className="text-2xl font-bold text-green-600">
                {status_breakdown.delivered}
              </p>
            </div>

            <div className="bg-red-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <XIcon size={18} className="text-red-600" />
                <p className="text-sm text-muted-foreground">Failed</p>
              </div>
              <p className="text-2xl font-bold text-red-600">
                {status_breakdown.failed}
              </p>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-muted/50 rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-2">
              <strong>{totalProcessed}</strong> of{" "}
              <strong>{status.total_messages}</strong> messages processed
            </p>
            {isComplete ? (
              <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
                <CheckCircleIcon size={14} className="mr-1" />
                Delivery Complete
              </Badge>
            ) : (
              <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">
                <Spinner size="sm" className="mr-1" />
                In Progress
              </Badge>
            )}
          </div>

          {/* Estimated Completion */}
          {!isComplete && status.estimated_completion && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-900">
                <strong>Estimated Completion:</strong>{" "}
                {new Date(status.estimated_completion).toLocaleString()}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Failures Section */}
      {failures && failures.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircleIcon size={20} className="text-red-600" />
                <CardTitle>Failed Messages ({failures.length})</CardTitle>
              </div>
              <Button
                onClick={() => setShowFailures(!showFailures)}
                variant="outline"
                size="sm"
              >
                {showFailures ? "Hide" : "Show"} Details
              </Button>
            </div>
          </CardHeader>
          {showFailures && (
            <CardContent className="space-y-4">
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {failures.map((failure, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-3 bg-red-50 border-red-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-semibold text-foreground">
                          {failure.recipient_name}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {failure.recipient_contact}
                        </p>
                      </div>
                      <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
                        {failure.channel}
                      </Badge>
                    </div>
                    <div className="bg-white rounded p-2 mb-2">
                      <p className="text-xs text-muted-foreground mb-1">
                        <strong>Error Code:</strong> {failure.error_code}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        <strong>Message:</strong> {failure.error_message}
                      </p>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">
                        {new Date(failure.timestamp).toLocaleString()}
                      </span>
                      {failure.retryable && (
                        <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">
                          Retryable
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Retry Button */}
              {failures.some((f) => f.retryable) && (
                <Button
                  onClick={handleRetryFailed}
                  disabled={retrying}
                  className="w-full"
                >
                  {retrying ? (
                    <>
                      <Spinner size="sm" className="mr-2" />
                      Retrying...
                    </>
                  ) : (
                    <>
                      <RefreshCwIcon size={16} className="mr-2" />
                      Retry Failed Messages
                    </>
                  )}
                </Button>
              )}
            </CardContent>
          )}
        </Card>
      )}

      {/* Success Message */}
      {isComplete && failures.length === 0 && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <CheckCircleIcon size={24} className="text-green-600" />
              <div>
                <p className="font-semibold text-green-900">
                  All messages delivered successfully!
                </p>
                <p className="text-sm text-green-700">
                  {status.total_messages} messages were sent without any failures.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info Card */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <ClockIcon size={20} className="text-blue-600 mt-1" />
            <div>
              <p className="font-medium text-blue-900 mb-1">
                Real-Time Tracking
              </p>
              <p className="text-sm text-blue-700">
                This page automatically updates every 5 seconds. You can manually
                refresh to see the latest status. Failed messages can be retried
                if they are marked as retryable.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
