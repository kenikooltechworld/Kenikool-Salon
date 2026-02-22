import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  AlertTriangleIcon,
  TrendingDownIcon,
  UsersIcon,
  PercentIcon,
} from "@/components/icons";
import { useRetentionMetrics, useAtRiskClients } from "@/lib/api/hooks/useClients";
import { useState } from "react";
import { WinbackCampaignModal } from "./winback-campaign-modal";

interface RetentionDashboardProps {
  onCampaignCreated?: () => void;
}

export function RetentionDashboard({ onCampaignCreated }: RetentionDashboardProps) {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useRetentionMetrics();
  const { data: atRiskData, isLoading: atRiskLoading } = useAtRiskClients(90, 0, 100);
  const [showWinbackModal, setShowWinbackModal] = useState(false);

  if (metricsLoading || atRiskLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  if (metricsError || !metrics) {
    return (
      <Card className="p-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading retention metrics</h3>
            <p className="text-sm">{metricsError?.message || "Metrics not available"}</p>
          </div>
        </Alert>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Retention Rate */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Retention Rate</p>
              <p className="text-2xl font-bold text-foreground">
                {(metrics.retention_rate * 100).toFixed(1)}%
              </p>
            </div>
            <PercentIcon size={32} className="text-green-600 dark:text-green-400" />
          </div>
        </Card>

        {/* Churn Rate */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Churn Rate</p>
              <p className="text-2xl font-bold text-foreground">
                {(metrics.churn_rate * 100).toFixed(1)}%
              </p>
            </div>
            <TrendingDownIcon size={32} className="text-red-600 dark:text-red-400" />
          </div>
        </Card>

        {/* At-Risk Clients */}
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">At-Risk Clients</p>
              <p className="text-2xl font-bold text-foreground">
                {metrics.at_risk_count}
              </p>
            </div>
            <AlertTriangleIcon size={32} className="text-yellow-600 dark:text-yellow-400" />
          </div>
        </Card>

        {/* Action Button */}
        <Card className="p-4 flex items-center justify-center">
          <Button
            onClick={() => setShowWinbackModal(true)}
            className="w-full"
            variant="primary"
          >
            Create Win-Back Campaign
          </Button>
        </Card>
      </div>

      {/* Retention Rate by Cohort */}
      {metrics.cohort_data && metrics.cohort_data.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Retention by Cohort
          </h3>
          <div className="space-y-3">
            {metrics.cohort_data.map((cohort, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">{cohort.cohort}</p>
                  <p className="text-xs text-muted-foreground">{cohort.size} clients</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-muted rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${cohort.retention_rate * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-foreground w-12 text-right">
                    {(cohort.retention_rate * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Churn Trends */}
      {metrics.churn_trends && metrics.churn_trends.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Churn Trends
          </h3>
          <div className="space-y-2">
            {metrics.churn_trends.slice(-12).map((trend, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{trend.date}</span>
                <span className="font-medium text-foreground">
                  {(trend.churn_rate * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* At-Risk Clients List */}
      {atRiskData && atRiskData.clients.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            At-Risk Clients ({atRiskData.total_count})
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {atRiskData.clients.map((client) => (
              <div
                key={client.id}
                className="p-3 bg-muted/50 rounded-lg flex items-center justify-between"
              >
                <div className="flex-1">
                  <p className="font-medium text-foreground">{client.name}</p>
                  <p className="text-sm text-muted-foreground">{client.phone}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {client.days_since_last_visit} days since last visit
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-foreground">
                    Risk: {(client.churn_risk_score * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    LTV: ₦{client.lifetime_value.toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Win-Back Campaign Modal */}
      {showWinbackModal && (
        <WinbackCampaignModal
          isOpen={showWinbackModal}
          onClose={() => setShowWinbackModal(false)}
          onSuccess={() => {
            setShowWinbackModal(false);
            onCampaignCreated?.();
          }}
        />
      )}
    </div>
  );
}
