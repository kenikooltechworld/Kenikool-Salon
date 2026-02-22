import { useAuth } from "@/lib/hooks/useAuth";
import { AISuggestionsComponent } from "@/components/ai/ai-suggestions";
import { Card } from "@/components/ui/card";
import { SparklesIcon } from "@/components/icons";

export default function AIInsightsPage() {
  const { user } = useAuth();

  if (!user?.tenant_id) {
    return (
      <div className="p-8">
        <Card className="p-8 text-center">
          <p className="text-gray-600">Loading...</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div className="flex items-center space-x-3">
        <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg">
          <SparklesIcon className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">AI Insights</h1>
          <p className="text-gray-600">
            Smart recommendations and insights powered by your salon data
          </p>
        </div>
      </div>

      {/* AI Suggestions Component */}
      <AISuggestionsComponent
        salonId={user.tenant_id}
        onAcceptSuggestion={(id) => {
          console.log("Accepted suggestion:", id);
          // You can add additional logic here
        }}
        onRejectSuggestion={(id, feedback) => {
          console.log("Rejected suggestion:", id, feedback);
          // You can add additional logic here
        }}
        onAcknowledgeAlert={(id) => {
          console.log("Acknowledged alert:", id);
          // You can add additional logic here
        }}
      />
    </div>
  );
}
