import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/components/ui/toast";
import { CheckIcon } from "@/components/icons";
import { ProfileSetup } from "@/components/onboarding/profile-setup";
import { ServiceSetup } from "@/components/onboarding/service-setup";
import { StaffSetup } from "@/components/onboarding/staff-setup";
import { PreviewSetup } from "@/components/onboarding/preview-setup";

const STEPS = [
  {
    id: 1,
    title: "Profile Setup",
    description: "Customize your salon branding",
  },
  { id: 2, title: "Add Service", description: "Create your first service" },
  { id: 3, title: "Add Staff", description: "Add your first team member" },
  { id: 4, title: "Preview", description: "See your booking page" },
];

// Helper to get initial state from localStorage (only runs on client)
const getInitialState = () => {
  if (typeof window === "undefined") {
    return {
      currentStep: 1,
      completedSteps: [],
      onboardingData: { profile: null, service: null, staff: null },
    };
  }

  const savedProgress = localStorage.getItem("onboarding_progress");
  const userStr = localStorage.getItem("user");

  let user = null;
  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch {
      // Ignore parse errors
    }
  }

  if (savedProgress) {
    try {
      const progress = JSON.parse(savedProgress);
      return {
        currentStep: progress.currentStep || 1,
        completedSteps: progress.completedSteps || [],
        onboardingData: progress.data || {
          profile: user
            ? {
                businessName: "",
                description: "",
                phone: user.phone || "",
                email: user.email || "",
                address: "",
                primaryColor: "#6366f1",
                secondaryColor: "#8b5cf6",
                logo: null,
              }
            : null,
          service: null,
          staff: null,
        },
      };
    } catch {
      // If parsing fails, use default with user data
      if (user) {
        return {
          currentStep: 1,
          completedSteps: [],
          onboardingData: {
            profile: {
              businessName: "",
              description: "",
              phone: user.phone || "",
              email: user.email || "",
              address: "",
              primaryColor: "#6366f1",
              secondaryColor: "#8b5cf6",
              logo: null,
            },
            service: null,
            staff: null,
          },
        };
      }
    }
  } else if (user) {
    // No saved progress, but we have user data
    return {
      currentStep: 1,
      completedSteps: [],
      onboardingData: {
        profile: {
          businessName: "",
          description: "",
          phone: user.phone || "",
          email: user.email || "",
          address: "",
          primaryColor: "#6366f1",
          secondaryColor: "#8b5cf6",
          logo: null,
        },
        service: null,
        staff: null,
      },
    };
  }

  return {
    currentStep: 1,
    completedSteps: [],
    onboardingData: { profile: null, service: null, staff: null },
  };
};

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();

  // Initialize state with lazy initializer to avoid hydration mismatch
  const [currentStep, setCurrentStep] = useState(
    () => getInitialState().currentStep
  );
  const [completedSteps, setCompletedSteps] = useState<number[]>(
    () => getInitialState().completedSteps
  );
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [onboardingData, setOnboardingData] = useState<any>(
    () => getInitialState().onboardingData
  );

  const progress = (completedSteps.length / STEPS.length) * 100;

  const handleStepComplete = async (stepId: number, data: unknown) => {
    const updatedData = {
      ...onboardingData,
      [stepId === 1 ? "profile" : stepId === 2 ? "service" : "staff"]: data,
    };

    const updatedCompletedSteps = completedSteps.includes(stepId)
      ? completedSteps
      : [...completedSteps, stepId];

    const nextStep = stepId < STEPS.length ? stepId + 1 : stepId;

    // Save progress to localStorage
    if (typeof window !== "undefined") {
      localStorage.setItem(
        "onboarding_progress",
        JSON.stringify({
          currentStep: nextStep,
          completedSteps: updatedCompletedSteps,
          data: updatedData,
        })
      );
    }

    setOnboardingData(updatedData);
    setCompletedSteps(updatedCompletedSteps);

    if (stepId < STEPS.length) {
      setCurrentStep(nextStep);
    }
  };

  const handleSkip = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFinish = async () => {
    try {
      // Clear onboarding progress from localStorage
      if (typeof window !== "undefined") {
        localStorage.removeItem("onboarding_progress");
      }

      showToast({
        title: "Setup Complete!",
        description: "Your salon is ready to accept bookings",
        variant: "success",
      });
      navigate("/dashboard");
    } catch (error) {
      showToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "An error occurred",
        variant: "error",
      });
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)] p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--foreground)] mb-2">
            Welcome! Let&apos;s set up your salon
          </h1>
          <p className="text-[var(--muted-foreground)]">
            Complete these steps to get started
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <Progress value={progress} className="mb-4" />
          <div className="flex justify-between">
            {STEPS.map((step) => (
              <div
                key={step.id}
                className={`flex items-center gap-2 ${
                  step.id === currentStep
                    ? "text-[var(--primary)]"
                    : completedSteps.includes(step.id)
                    ? "text-[var(--success)]"
                    : "text-[var(--muted-foreground)]"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
                    completedSteps.includes(step.id)
                      ? "bg-[var(--success)] border-[var(--success)] text-white"
                      : step.id === currentStep
                      ? "border-[var(--primary)] text-[var(--primary)]"
                      : "border-[var(--border)]"
                  }`}
                >
                  {completedSteps.includes(step.id) ? (
                    <CheckIcon size={16} />
                  ) : (
                    step.id
                  )}
                </div>
                <div className="hidden md:block">
                  <p className="text-sm font-medium">{step.title}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <Card className="p-6 md:p-8 mb-6">
          {currentStep === 1 && (
            <ProfileSetup
              onComplete={(data) => handleStepComplete(1, data)}
              initialData={onboardingData.profile}
            />
          )}
          {currentStep === 2 && (
            <ServiceSetup
              onComplete={(data) => handleStepComplete(2, data)}
              initialData={onboardingData.service}
            />
          )}
          {currentStep === 3 && (
            <StaffSetup
              onComplete={(data) => handleStepComplete(3, data)}
              initialData={onboardingData.staff}
            />
          )}
          {currentStep === 4 && (
            <PreviewSetup data={onboardingData} onFinish={handleFinish} />
          )}
        </Card>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 1}
          >
            Back
          </Button>
          <div className="flex gap-3">
            {currentStep < STEPS.length && (
              <Button variant="ghost" onClick={handleSkip}>
                Skip for now
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
