import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  PlusIcon,
  TagIcon,
  AlertTriangleIcon,
  EditIcon,
  TrashIcon,
  DollarIcon,
  ClockIcon,
  CalendarIcon,
  TrendingUpIcon,
} from "@/components/icons";
import { PricingRuleFormModal } from "@/components/pricing/pricing-rule-form-modal";
import { PriceCalculator } from "@/components/pricing/price-calculator";
import { apiClient } from "@/lib/api/client";

interface PricingRule {
  id: string;
  name: string;
  rule_type: string;
  multiplier: number;
  service_ids: string[];
  start_time?: string;
  end_time?: string;
  days_of_week: number[];
  min_bookings?: number;
  max_bookings?: number;
  start_date?: string;
  end_date?: string;
  enabled: boolean;
}

const RULE_TYPE_LABELS: Record<string, string> = {
  time_of_day: "Time of Day",
  day_of_week: "Day of Week",
  demand: "Demand-Based",
  seasonal: "Seasonal",
};

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function PricingPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rules, setRules] = useState<PricingRule[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<PricingRule | undefined>();

  const fetchRules = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get("/api/pricing");
      setRules(response.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleEnabled = async (ruleId: string, enabled: boolean) => {
    try {
      await apiClient.patch(`/api/pricing/${ruleId}`, { enabled });
      fetchRules();
    } catch (err: any) {
      showToast("Failed to update rule: " + err.message, "error");
    }
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm("Are you sure you want to delete this pricing rule?")) return;

    try {
      await apiClient.delete(`/api/pricing/${ruleId}`);
      fetchRules();
    } catch (err: any) {
      showToast("Failed to delete rule: " + err.message, "error");
    }
  };

  const getRuleIcon = (ruleType: string) => {
    switch (ruleType) {
      case "time_of_day":
        return <ClockIcon size={20} className="text-primary" />;
      case "day_of_week":
        return <CalendarIcon size={20} className="text-primary" />;
      case "demand":
        return <TrendingUpIcon size={20} className="text-primary" />;
      case "seasonal":
        return <CalendarIcon size={20} className="text-primary" />;
      default:
        return <TagIcon size={20} className="text-primary" />;
    }
  };

  const getMultiplierBadge = (multiplier: number) => {
    const percentage = ((multiplier - 1) * 100).toFixed(0);
    const isIncrease = multiplier > 1;

    return (
      <Badge variant={isIncrease ? "default" : "secondary"}>
        {isIncrease ? "+" : ""}
        {percentage}%
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Dynamic Pricing
          </h1>
          <p className="text-muted-foreground">
            Configure pricing rules based on time, demand, and seasonality
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={fetchRules}>
            Refresh
          </Button>
          <Button onClick={() => setIsModalOpen(true)}>
            <PlusIcon size={20} />
            Create Rule
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pricing Rules List */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pricing Rules</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-12">
                  <Spinner />
                </div>
              ) : rules.length === 0 ? (
                <div className="text-center py-12">
                  <DollarIcon
                    size={48}
                    className="mx-auto text-muted-foreground mb-4"
                  />
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    No pricing rules yet
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Create your first pricing rule to enable dynamic pricing
                  </p>
                  <Button onClick={() => setIsModalOpen(true)}>
                    <PlusIcon size={20} />
                    Create Rule
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {rules.map((rule) => (
                    <div
                      key={rule.id}
                      className="flex items-center justify-between p-4 bg-muted/50 rounded-lg"
                    >
                      <div className="flex items-center gap-4 flex-1">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          {getRuleIcon(rule.rule_type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-semibold text-foreground">
                              {rule.name}
                            </p>
                            {getMultiplierBadge(rule.multiplier)}
                            <Badge variant="outline">
                              {RULE_TYPE_LABELS[rule.rule_type]}
                            </Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {rule.rule_type === "time_of_day" &&
                              rule.start_time &&
                              rule.end_time && (
                                <span>
                                  {rule.start_time} - {rule.end_time}
                                </span>
                              )}
                            {rule.rule_type === "day_of_week" &&
                              rule.days_of_week.length > 0 && (
                                <span>
                                  {rule.days_of_week
                                    .map((d) => DAY_NAMES[d])
                                    .join(", ")}
                                </span>
                              )}
                            {rule.rule_type === "demand" && (
                              <span>
                                {rule.min_bookings &&
                                  `Min: ${rule.min_bookings}`}
                                {rule.min_bookings &&
                                  rule.max_bookings &&
                                  " • "}
                                {rule.max_bookings &&
                                  `Max: ${rule.max_bookings}`}
                              </span>
                            )}
                            {rule.rule_type === "seasonal" &&
                              rule.start_date &&
                              rule.end_date && (
                                <span>
                                  {rule.start_date} to {rule.end_date}
                                </span>
                              )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={rule.enabled}
                          onCheckedChange={(checked) =>
                            handleToggleEnabled(rule.id, checked)
                          }
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingRule(rule);
                            setIsModalOpen(true);
                          }}
                        >
                          <EditIcon size={16} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(rule.id)}
                        >
                          <TrashIcon size={16} />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Price Calculator */}
        <div className="lg:col-span-1">
          <PriceCalculator />
        </div>
      </div>

      {/* Pricing Rule Form Modal */}
      <PricingRuleFormModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingRule(undefined);
        }}
        onSuccess={() => {
          fetchRules();
          setIsModalOpen(false);
          setEditingRule(undefined);
        }}
        rule={editingRule}
      />
    </div>
  );
}
