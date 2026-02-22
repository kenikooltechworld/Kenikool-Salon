import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  useGetStaffChecklist,
  useUpdateChecklistItem,
} from "@/lib/api/hooks/useOnboarding";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CheckCircle2, Circle } from "lucide-react";

export default function StaffOnboardingPage() {
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    department: "",
    position: "",
    start_date: "",
    manager_id: "",
    notes: "",
  });

  // Get current user ID from API
  const { data: userData } = useQuery({
    queryKey: ["current-user"],
    queryFn: async () => {
      const response = await apiClient.get("/api/auth/me");
      return response.data;
    },
  });

  const staffId = userData?.id || "";

  // Get onboarding checklist
  const { data: checklist, isLoading } = useGetStaffChecklist(staffId);
  const updateItemMutation = useUpdateChecklistItem();

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCompleteStep = async () => {
    if (checklist && checklist.items && checklist.items[currentStep]) {
      try {
        await updateItemMutation.mutateAsync({
          checklistId: checklist._id,
          itemIndex: currentStep,
          status: "completed",
          notes: formData.notes,
        });
        toast("Step completed successfully", "success");
        if (currentStep < checklist.items.length - 1) {
          setCurrentStep(currentStep + 1);
        }
      } catch (error) {
        toast("Failed to complete step", "error");
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        Loading...
      </div>
    );
  }

  if (!checklist || !checklist.items) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Staff Onboarding
          </h1>
          <p className="text-muted-foreground mt-2">
            No onboarding checklist found
          </p>
        </div>
      </div>
    );
  }

  const steps = checklist.items || [];
  const completedCount = steps.filter(
    (s: any) => s.status === "completed",
  ).length;
  const progressPercent =
    steps.length > 0 ? (completedCount / steps.length) * 100 : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Staff Onboarding</h1>
        <p className="text-muted-foreground mt-2">
          Complete your onboarding process
        </p>
      </div>

      {/* Progress Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Onboarding Progress</CardTitle>
          <CardDescription>
            {completedCount} of {steps.length} steps completed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Steps Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Steps</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {steps.map((step: any, index: number) => (
                <button
                  key={index}
                  onClick={() => setCurrentStep(index)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                    currentStep === index
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                >
                  {step.status === "completed" ? (
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                  ) : (
                    <Circle className="w-5 h-5 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate">
                      {step.title}
                    </div>
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2">
          {steps.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{steps[currentStep]?.title}</CardTitle>
                <CardDescription>
                  {steps[currentStep]?.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Department</Label>
                    <Input
                      value={formData.department}
                      onChange={(e) =>
                        handleInputChange("department", e.target.value)
                      }
                      placeholder="Enter department"
                    />
                  </div>
                  <div>
                    <Label>Position</Label>
                    <Input
                      value={formData.position}
                      onChange={(e) =>
                        handleInputChange("position", e.target.value)
                      }
                      placeholder="Enter position"
                    />
                  </div>
                  <div>
                    <Label>Start Date</Label>
                    <Input
                      type="date"
                      value={formData.start_date}
                      onChange={(e) =>
                        handleInputChange("start_date", e.target.value)
                      }
                    />
                  </div>
                  <div>
                    <Label>Manager ID</Label>
                    <Input
                      value={formData.manager_id}
                      onChange={(e) =>
                        handleInputChange("manager_id", e.target.value)
                      }
                      placeholder="Enter manager ID"
                    />
                  </div>
                </div>
                <div>
                  <Label>Notes</Label>
                  <textarea
                    value={formData.notes}
                    onChange={(e) => handleInputChange("notes", e.target.value)}
                    placeholder="Add any notes"
                    className="w-full p-2 border rounded-md"
                    rows={4}
                  />
                </div>

                <div className="flex gap-2 pt-4">
                  <Button
                    onClick={handleCompleteStep}
                    disabled={
                      updateItemMutation.isPending ||
                      steps[currentStep]?.status === "completed"
                    }
                  >
                    {steps[currentStep]?.status === "completed"
                      ? "Completed"
                      : "Complete Step"}
                  </Button>
                  {currentStep > 0 && (
                    <Button
                      variant="outline"
                      onClick={() => setCurrentStep(currentStep - 1)}
                    >
                      Previous
                    </Button>
                  )}
                  {currentStep < steps.length - 1 && (
                    <Button
                      variant="outline"
                      onClick={() => setCurrentStep(currentStep + 1)}
                    >
                      Next
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
