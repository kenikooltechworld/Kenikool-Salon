import { useRouter } from "next/router";
import { Spinner } from "@/components/ui/spinner";
import { RetentionDashboard } from "@/components/clients";

export default function RetentionPage() {
  const router = useRouter();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Client Retention
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor client retention metrics and manage win-back campaigns
          </p>
        </div>
      </div>

      {/* Retention Dashboard */}
      <RetentionDashboard
        onCampaignCreated={() => {
          // Refresh data or show success message
        }}
      />
    </div>
  );
}
