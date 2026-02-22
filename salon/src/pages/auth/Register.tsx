import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { RegistrationForm } from "@/components/RegistrationForm";
import {
  useRegisterSalon,
  type RegistrationData,
} from "@/hooks/useRegistration";
import { useToast } from "@/components/ui/toast";

export function Register() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [error, setError] = useState<string>("");
  const registerMutation = useRegisterSalon();

  const handleSubmit = async (data: RegistrationData) => {
    setError("");
    try {
      const response = await registerMutation.mutateAsync(data);
      if (response.success) {
        // Show success toast
        showToast({
          title: "Registration Submitted!",
          description: "Check your email for the verification code.",
          variant: "success",
          duration: 5000,
        });
        // Navigate to verification page with email as query param
        navigate(`/auth/verify?email=${encodeURIComponent(data.email)}`);
      }
    } catch (err: any) {
      // Handle Pydantic validation errors (422)
      if (err.response?.status === 422 && err.response?.data?.detail) {
        const details = err.response.data.detail;
        if (Array.isArray(details)) {
          // Pydantic validation error format: array of error objects
          const errorMessages = details
            .map((e: any) => {
              const fieldName =
                Array.isArray(e.loc) && e.loc.length > 1 ? e.loc[1] : "Field";
              return `${fieldName}: ${e.msg}`;
            })
            .join(", ");
          setError(errorMessages);
          showToast({
            title: "Validation Error",
            description: errorMessages,
            variant: "error",
            duration: 5000,
          });
        } else if (typeof details === "string") {
          setError(details);
          showToast({
            title: "Validation Error",
            description: details,
            variant: "error",
            duration: 5000,
          });
        } else {
          setError("Validation error. Please check your input.");
          showToast({
            title: "Validation Error",
            description: "Please check your input.",
            variant: "error",
            duration: 5000,
          });
        }
      } else {
        const errorMessage =
          err.response?.data?.detail ||
          err.message ||
          "Failed to register. Please try again.";
        setError(errorMessage);
        showToast({
          title: "Registration Failed",
          description: errorMessage,
          variant: "error",
          duration: 5000,
        });
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Create Your Salon Account
            </h1>
            <p className="text-muted-foreground">
              Join thousands of salon owners managing their business with
              Kenikool
            </p>
          </div>

          <RegistrationForm
            onSubmit={handleSubmit}
            isLoading={registerMutation.isPending}
            error={error}
          />

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link
                to="/auth/login"
                className="text-primary hover:underline font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>

          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-muted-foreground text-center">
              By creating an account, you agree to our{" "}
              <a href="#" className="text-primary hover:underline">
                Terms of Service
              </a>{" "}
              and{" "}
              <a href="#" className="text-primary hover:underline">
                Privacy Policy
              </a>
            </p>
          </div>
        </Card>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>Get 30 days free trial with all Enterprise features included</p>
        </div>
      </div>
    </div>
  );
}
