import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  LightbulbIcon,
  AlertTriangleIcon,
  TrendingUpIcon,
  ChevronRightIcon,
} from "@/components/icons";

export interface AIInsight {
  type: "opportunity" | "warning" | "recommendation";
  title: string;
  description: string;
  action?: string;
}

interface AIInsightsProps {
  insights: AIInsight[];
}

export function AIInsights({ insights }: AIInsightsProps) {
  const getInsightIcon = (type: AIInsight["type"]) => {
    switch (type) {
      case "opportunity":
        return <TrendingUpIcon size={20} className="text-[var(--success)]" />;
      case "warning":
        return (
          <AlertTriangleIcon size={20} className="text-[var(--warning)]" />
        );
      case "recommendation":
        return <LightbulbIcon size={20} className="text-[var(--info)]" />;
    }
  };

  const getInsightBadgeVariant = (type: AIInsight["type"]) => {
    switch (type) {
      case "opportunity":
        return "success";
      case "warning":
        return "warning";
      case "recommendation":
        return "info";
    }
  };

  const getInsightBadgeText = (type: AIInsight["type"]) => {
    switch (type) {
      case "opportunity":
        return "Opportunity";
      case "warning":
        return "Warning";
      case "recommendation":
        return "Recommendation";
    }
  };

  return (
    <Card className="p-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-foreground">AI Insights</h2>
        <p className="text-sm text-muted-foreground">
          Actionable recommendations to grow your business
        </p>
      </div>

      {insights.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <LightbulbIcon size={48} className="text-muted-foreground mb-3" />
          <p className="text-muted-foreground">
            No insights available yet. Keep growing your business and we'll
            provide personalized recommendations.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <div
              key={index}
              className="flex items-start gap-4 p-4 rounded-lg border border-[var(--border)] hover:bg-muted/50 transition-colors"
            >
              {/* Icon */}
              <div className="flex-shrink-0 mt-1">
                {getInsightIcon(insight.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium text-foreground">
                    {insight.title}
                  </h3>
                  <Badge variant={getInsightBadgeVariant(insight.type)}>
                    {getInsightBadgeText(insight.type)}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {insight.description}
                </p>
                {insight.action && (
                  <Button variant="outline" size="sm">
                    {insight.action}
                    <ChevronRightIcon size={16} />
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
