import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckCircle2, Circle, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ChecklistItem {
  title: string;
  description: string;
  assigned_to: string;
  order: number;
  status: "pending" | "in_progress" | "completed";
  completed_at?: string;
  completed_by?: string;
  notes?: string;
}

interface OnboardingChecklistProps {
  staffId: string;
  staffName: string;
  onUpdateItem?: (
    itemIndex: number,
    status: string,
    notes?: string,
  ) => Promise<void>;
}

export const OnboardingChecklist: React.FC<OnboardingChecklistProps> = ({
  staffId,
  staffName,
  onUpdateItem,
}) => {
  const { showToast } = useToast();
  const [checklist, setChecklist] = useState<{
    items: ChecklistItem[];
    progress_percentage: number;
    status: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChecklist();
  }, [staffId]);

  const fetchChecklist = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/staff/onboarding/${staffId}`);
      const data = await response.json();
      setChecklist(data.checklist);
    } catch (error) {
      console.error("Failed to fetch checklist:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleItemStatusChange = async (
    itemIndex: number,
    newStatus: string,
  ) => {
    try {
      if (onUpdateItem) {
        await onUpdateItem(itemIndex, newStatus);
      }
      await fetchChecklist();
    } catch (error) {
      console.error("Failed to update item:", error);
      showToast({
        title: "Error",
        description: "Failed to update item",
        variant: "destructive",
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "in_progress":
        return <Circle className="w-5 h-5 text-blue-500" />;
      default:
        return <Circle className="w-5 h-5 text-slate-300" />;
    }
  };

  const getAssigneeLabel = (assignee: string) => {
    const labels: Record<string, string> = {
      manager: "Manager",
      staff: "Staff",
      owner: "Owner",
    };
    return labels[assignee] || assignee;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-slate-500">Loading checklist...</p>
        </CardContent>
      </Card>
    );
  }

  if (!checklist) {
    return (
      <Card>
        <CardContent className="py-8">
          <p className="text-center text-slate-500">
            No onboarding checklist found
          </p>
        </CardContent>
      </Card>
    );
  }

  const sortedItems = [...checklist.items].sort((a, b) => a.order - b.order);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Onboarding Checklist</CardTitle>
            <p className="text-sm text-slate-500 mt-1">{staffName}</p>
          </div>
          <Badge
            variant={checklist.status === "completed" ? "default" : "secondary"}
          >
            {checklist.status === "completed" ? "Completed" : "In Progress"}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Progress</span>
            <span className="text-sm text-slate-600">
              {checklist.progress_percentage}%
            </span>
          </div>
          <Progress value={checklist.progress_percentage} className="h-2" />
        </div>

        <ScrollArea className="h-96">
          <div className="space-y-2 pr-4">
            {sortedItems.map((item, index) => (
              <div
                key={index}
                className="border rounded-lg p-3 hover:bg-slate-50 transition"
              >
                <div className="flex items-start gap-3">
                  <button
                    onClick={() => {
                      const newStatus =
                        item.status === "completed" ? "pending" : "completed";
                      handleItemStatusChange(index, newStatus);
                    }}
                    className="mt-1 flex-shrink-0"
                  >
                    {getStatusIcon(item.status)}
                  </button>

                  <div className="flex-1">
                    <h3
                      className={`font-medium text-sm ${
                        item.status === "completed"
                          ? "line-through text-slate-500"
                          : ""
                      }`}
                    >
                      {item.title}
                    </h3>
                    <p className="text-xs text-slate-600 mt-1">
                      {item.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className="text-xs">
                        {getAssigneeLabel(item.assigned_to)}
                      </Badge>
                      {item.completed_at && (
                        <span className="text-xs text-slate-500">
                          Completed{" "}
                          {new Date(item.completed_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    {item.notes && (
                      <p className="text-xs text-slate-600 mt-2 italic">
                        {item.notes}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {checklist.status === "completed" && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-start gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-green-900">
                Onboarding Complete
              </p>
              <p className="text-xs text-green-700 mt-1">
                All items have been completed successfully.
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
