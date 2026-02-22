import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { X, Plus, Trash2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ReviewFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  staffId: string;
  staffName: string;
  onSubmit?: (data: any) => Promise<void>;
}

export const ReviewFormModal: React.FC<ReviewFormModalProps> = ({
  isOpen,
  onClose,
  staffId,
  staffName,
  onSubmit,
}) => {
  const { showToast } = useToast();
  const [reviewDate, setReviewDate] = useState(
    new Date().toISOString().split("T")[0],
  );
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [criteria, setCriteria] = useState<Record<string, number>>({});
  const [criteriaOptions, setCriteriaOptions] = useState<Record<string, any>>(
    {},
  );
  const [strengths, setStrengths] = useState("");
  const [improvements, setImprovements] = useState("");
  const [goals, setGoals] = useState<
    Array<{ goal: string; target_date: string }>
  >([{ goal: "", target_date: "" }]);
  const [followUpDate, setFollowUpDate] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchCriteriaOptions();
    }
  }, [isOpen]);

  const fetchCriteriaOptions = async () => {
    try {
      const response = await fetch("/api/staff/reviews/criteria-options");
      const data = await response.json();
      setCriteriaOptions(data);
      const initialRatings: Record<string, number> = {};
      Object.keys(data).forEach((key) => {
        initialRatings[key] = 3;
      });
      setCriteria(initialRatings);
    } catch (error) {
      console.error("Failed to fetch criteria:", error);
    }
  };

  const handleRatingChange = (key: string, value: number) => {
    setCriteria({ ...criteria, [key]: value });
  };

  const handleAddGoal = () => {
    setGoals([...goals, { goal: "", target_date: "" }]);
  };

  const handleRemoveGoal = (index: number) => {
    setGoals(goals.filter((_, i) => i !== index));
  };

  const handleGoalChange = (index: number, field: string, value: string) => {
    const newGoals = [...goals];
    newGoals[index] = { ...newGoals[index], [field]: value };
    setGoals(newGoals);
  };

  const handleSubmit = async () => {
    if (
      !reviewDate ||
      !periodStart ||
      !periodEnd ||
      !strengths ||
      !improvements
    ) {
      showToast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      if (onSubmit) {
        await onSubmit({
          staff_id: staffId,
          review_date: reviewDate,
          review_period_start: periodStart,
          review_period_end: periodEnd,
          ratings: criteria,
          strengths,
          areas_for_improvement: improvements,
          goals: goals.filter((g) => g.goal.trim()),
          follow_up_date: followUpDate || null,
        });
      }
      onClose();
    } catch (error) {
      console.error("Failed to submit review:", error);
      showToast({
        title: "Error",
        description: "Failed to submit review",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle>Performance Review - {staffName}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Review Date *
              </label>
              <Input
                type="date"
                value={reviewDate}
                onChange={(e) => setReviewDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Period Start *
              </label>
              <Input
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Period End *
              </label>
              <Input
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-3 bg-slate-50 p-3 rounded-lg">
            <h3 className="font-semibold text-sm">Ratings (1-5)</h3>
            {Object.entries(criteriaOptions).map(
              ([key, option]: [string, any]) => (
                <div key={key}>
                  <div className="flex items-center justify-between mb-1">
                    <div>
                      <label className="text-sm font-medium">
                        {option.label}
                      </label>
                      <p className="text-xs text-slate-500">
                        {option.description}
                      </p>
                    </div>
                    <span className="text-sm font-medium">
                      {criteria[key] || 3}
                    </span>
                  </div>
                  <Slider
                    value={[criteria[key] || 3]}
                    onValueChange={(v) => handleRatingChange(key, v[0])}
                    min={1}
                    max={5}
                    step={1}
                    className="w-full"
                  />
                </div>
              ),
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Strengths *
            </label>
            <Textarea
              placeholder="What are this staff member's key strengths?"
              value={strengths}
              onChange={(e) => setStrengths(e.target.value)}
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Areas for Improvement *
            </label>
            <Textarea
              placeholder="What areas could this staff member improve?"
              value={improvements}
              onChange={(e) => setImprovements(e.target.value)}
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium">
                Improvement Goals
              </label>
              <Button onClick={handleAddGoal} variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-1" />
                Add Goal
              </Button>
            </div>
            {goals.map((goal, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  placeholder="Goal"
                  value={goal.goal}
                  onChange={(e) =>
                    handleGoalChange(index, "goal", e.target.value)
                  }
                  className="flex-1"
                />
                <Input
                  type="date"
                  value={goal.target_date}
                  onChange={(e) =>
                    handleGoalChange(index, "target_date", e.target.value)
                  }
                  className="w-32"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveGoal(index)}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </Button>
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Follow-up Review Date
            </label>
            <Input
              type="date"
              value={followUpDate}
              onChange={(e) => setFollowUpDate(e.target.value)}
            />
          </div>

          <div className="flex gap-2 border-t pt-4">
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1"
            >
              Submit Review
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
