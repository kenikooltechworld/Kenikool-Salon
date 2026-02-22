import { useParams, useNavigate } from "react-router-dom";
import { useRefund } from "@/hooks/useRefunds";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import {
  CheckCircleIcon,
  AlertCircleIcon,
  ClockIcon,
} from "@/components/icons";

export default function RefundStatus() {
  const { refundId } = useParams<{ refundId: string }>();
  const navigate = useNavigate();
  const { data: refund, isLoading } = useRefund(refundId || "");

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircleIcon size={24} className="text-green-600" />;
      case "failed":
        return <AlertCircleIcon size={24} className="text-destructive" />;
      case "pending":
        return <ClockIcon size={24} className="text-yellow-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusMessage = (status: string) => {
    switch (status) {
      case "success":
        return "Your refund has been successfully processed.";
      case "failed":
        return "The refund request failed. Please contact support.";
      case "pending":
        return "Your refund is being processed. This typically takes 3-5 business days.";
      default:
        return "Unknown status";
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading refund details...</div>;
  }

  if (!refund) {
    return <div className="text-center py-8">Refund not found</div>;
  }

  const refundData = refund as any;

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Refund Status</h1>
        <Button variant="outline" onClick={() => navigate("/payments")}>
          Back
        </Button>
      </div>

      {/* Status Card */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-start gap-4 mb-6">
          {getStatusIcon(refundData.status)}
          <div className="flex-1">
            <h2 className="text-lg font-semibold mb-2">Refund Status</h2>
            <p
              className={`px-3 py-1 rounded-full text-sm font-medium w-fit ${getStatusColor(refundData.status)}`}
            >
              {refundData.status.charAt(0).toUpperCase() +
                refundData.status.slice(1)}
            </p>
            <p className="text-sm text-muted-foreground mt-3">
              {getStatusMessage(refundData.status)}
            </p>
          </div>
        </div>
      </div>

      {/* Refund Details */}
      <div className="bg-card border border-border rounded-lg p-6 space-y-4">
        <h3 className="font-semibold">Refund Details</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Refund ID</p>
            <p className="font-medium">{refundData.id}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Amount</p>
            <p className="font-medium text-lg">
              {formatCurrency(refundData.amount)}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Payment ID</p>
            <p className="font-medium">{refundData.payment_id}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Requested Date</p>
            <p className="font-medium">{formatDate(refundData.created_at)}</p>
          </div>
        </div>
      </div>

      {/* Reason */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="font-semibold mb-3">Reason for Refund</h3>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
          {refundData.reason}
        </p>
      </div>

      {/* Timeline */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="font-semibold mb-4">Timeline</h3>
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="w-3 h-3 rounded-full bg-primary mt-1.5"></div>
              <div className="w-0.5 h-12 bg-border"></div>
            </div>
            <div>
              <p className="font-medium">Refund Requested</p>
              <p className="text-sm text-muted-foreground">
                {formatDate(refundData.created_at)}
              </p>
            </div>
          </div>

          {refundData.status !== "pending" && (
            <div className="flex gap-4">
              <div className="flex flex-col items-center">
                <div
                  className={`w-3 h-3 rounded-full ${
                    refundData.status === "success"
                      ? "bg-green-600"
                      : "bg-destructive"
                  }`}
                ></div>
              </div>
              <div>
                <p className="font-medium">
                  {refundData.status === "success"
                    ? "Refund Completed"
                    : "Refund Failed"}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Support Info */}
      {refundData.status === "failed" && (
        <div className="bg-destructive/10 border border-destructive rounded-lg p-6">
          <h3 className="font-semibold text-destructive mb-3">Need Help?</h3>
          <p className="text-sm mb-3">
            Your refund request failed. Please contact our support team for
            assistance.
          </p>
          <div className="space-y-2">
            <p className="text-sm font-medium">Support Contact:</p>
            <p className="text-sm text-muted-foreground">
              Email: support@kenikool.com
            </p>
            <p className="text-sm text-muted-foreground">
              Phone: +234 (0) XXX XXX XXXX
            </p>
            <p className="text-sm text-muted-foreground">
              Reference: {refundData.id}
            </p>
          </div>
        </div>
      )}

      {refundData.status === "pending" && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">Processing</h3>
          <p className="text-sm text-blue-900">
            Your refund is being processed. Most refunds are completed within
            3-5 business days. You will receive an email notification once the
            refund is completed.
          </p>
        </div>
      )}

      <Button
        variant="outline"
        onClick={() => navigate("/payments")}
        className="w-full"
      >
        Back to Payments
      </Button>
    </div>
  );
}
