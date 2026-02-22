import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, AlertCircle, Loader } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ValidationResult {
  feature: string;
  tests: Array<{
    name: string;
    status: "passed" | "failed";
    error?: string;
    count?: number;
  }>;
  passed: number;
  failed: number;
}

interface ValidationDashboardProps {
  userRole: string;
}

export const ValidationDashboard: React.FC<ValidationDashboardProps> = ({
  userRole,
}) => {
  const { showToast } = useToast();
  const [results, setResults] = useState<ValidationResult[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [totalPassed, setTotalPassed] = useState(0);
  const [totalFailed, setTotalFailed] = useState(0);

  const runValidation = async () => {
    if (userRole !== "owner") {
      showToast({
        title: "Permission Denied",
        description: "Only owners can run validation",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/staff/validation/checkpoint-13");
      const data = await response.json();
      setResults(data.features);
      setTotalPassed(data.total_passed);
      setTotalFailed(data.total_failed);
    } catch (error) {
      console.error("Validation failed:", error);
      showToast({
        title: "Error",
        description: "Validation failed",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getProgressPercentage = () => {
    const total = totalPassed + totalFailed;
    return total > 0 ? (totalPassed / total) * 100 : 0;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Checkpoint 13: Advanced Features Validation</CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="flex gap-4">
          <Button
            onClick={runValidation}
            disabled={loading || userRole !== "owner"}
            className="flex-1"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Running Validation...
              </>
            ) : (
              "Run Full Validation"
            )}
          </Button>
        </div>

        {results && (
          <div className="space-y-4">
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Overall Progress</span>
                <span className="text-sm text-slate-600">
                  {totalPassed} / {totalPassed + totalFailed} passed
                </span>
              </div>
              <Progress value={getProgressPercentage()} className="h-2" />
              <div className="flex gap-4 mt-3 text-sm">
                <div className="flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  <span>{totalPassed} Passed</span>
                </div>
                {totalFailed > 0 && (
                  <div className="flex items-center gap-1">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span>{totalFailed} Failed</span>
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-3">
              {results.map((feature) => (
                <div
                  key={feature.feature}
                  className="border rounded-lg p-4 hover:bg-slate-50 transition"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold">{feature.feature}</h3>
                    <Badge
                      variant={feature.failed === 0 ? "default" : "destructive"}
                    >
                      {feature.passed}/{feature.passed + feature.failed}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    {feature.tests.map((test, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between text-sm"
                      >
                        <div className="flex items-center gap-2">
                          {test.status === "passed" ? (
                            <CheckCircle2 className="w-4 h-4 text-green-600" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-red-600" />
                          )}
                          <span>{test.name}</span>
                        </div>
                        <div className="text-slate-600">
                          {test.count !== undefined && (
                            <span className="text-xs">Count: {test.count}</span>
                          )}
                          {test.error && (
                            <span className="text-xs text-red-600">
                              {test.error}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {totalFailed === 0 && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-green-900">
                    All Validations Passed!
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    All staff management features are working correctly.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
