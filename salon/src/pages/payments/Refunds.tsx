import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useRefunds } from "@/hooks/useRefunds";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import {
  CheckCircleIcon,
  AlertCircleIcon,
  ClockIcon,
  ChevronRightIcon,
} from "@/components/icons";

export default function RefundsPage() {
  const navigate = useNavigate();
  const [selectedStatus, setSelectedStatus] = useState<
    "pending" | "success" | "failed" | undefined
  >();

  const { data: refunds = [], isLoading } = useRefunds({
    status: selectedStatus,
    limit: 50,
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircleIcon size={20} className="text-green-600" />;
      case "failed":
        return <AlertCircleIcon size={20} className="text-destructive" />;
      case "pending":
        return <ClockIcon size={20} className="text-yellow-600" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "success":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case "failed":
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const statuses = [
    { value: undefined, label: "All", count: refunds.length },
    {
      value: "pending" as const,
      label: "Pending",
      count: refunds.filter((r) => r.status === "pending").length,
    },
    {
      value: "success" as const,
      label: "Completed",
      count: refunds.filter((r) => r.status === "success").length,
    },
    {
      value: "failed" as const,
      label: "Failed",
      count: refunds.filter((r) => r.status === "failed").length,
    },
  ];

  const totalRefunded = refunds
    .filter((r) => r.status === "success")
    .reduce((sum, r) => sum + r.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Refunds</h1>
          <p className="text-muted-foreground mt-1">
            View and track your refund requests
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate("/payments")}
          className="gap-2"
        >
          Back to Payments
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Refunds</p>
              <p className="text-2xl font-bold text-foreground mt-2">
                {refunds.length}
              </p>
            </div>
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <CheckCircleIcon size={24} className="text-primary" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Refunded</p>
              <p className="text-2xl font-bold text-green-600 mt-2">
                {formatCurrency(totalRefunded)}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircleIcon size={24} className="text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Pending</p>
              <p className="text-2xl font-bold text-yellow-600 mt-2">
                {refunds.filter((r) => r.status === "pending").length}
              </p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <ClockIcon size={24} className="text-yellow-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Status Filter */}
      <div className="flex flex-wrap gap-2">
        {statuses.map((status) => (
          <Button
            key={status.value || "all"}
            variant={selectedStatus === status.value ? "primary" : "outline"}
            onClick={() => setSelectedStatus(status.value)}
            className="gap-2"
          >
            {status.label}
            <Badge variant="secondary">{status.count}</Badge>
          </Button>
        ))}
      </div>

      {/* Refunds List */}
      <div>
        <h2 className="text-lg font-semibold text-foreground mb-4">
          {selectedStatus
            ? `${selectedStatus.charAt(0).toUpperCase() + selectedStatus.slice(1)} Refunds`
            : "All Refunds"}
        </h2>

        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading refunds...
          </div>
        ) : refunds.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-muted-foreground">No refunds found</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {refunds.map((refund) => (
              <Card
                key={refund.id}
                className="p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/payments/refunds/${refund.id}`)}
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="flex-shrink-0">
                      {getStatusIcon(refund.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium truncate">
                          Refund {refund.id.slice(0, 8)}...
                        </p>
                        {getStatusBadge(refund.status)}
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {refund.reason}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {formatDate(refund.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div className="text-right">
                      <p className="font-semibold">
                        {formatCurrency(refund.amount)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Payment: {refund.payment_id.slice(0, 8)}...
                      </p>
                    </div>
                    <ChevronRightIcon
                      size={20}
                      className="text-muted-foreground"
                    />
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
