import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { RegistrationForm } from "@/components/RegistrationForm";
import {
  useRegisterSalon,
  type RegistrationData,
} from "@/hooks/useRegistration";
import { useToast } from "@/components/ui/toast";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { TrustIndicators } from "@/components/auth/TrustIndicators";

export function Register() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const registerMutation = useRegisterSalon();

  const handleSubmit = async (data: RegistrationData) => {
    setError("");
    setIsSubmitting(true);
    try {
      const response = await registerMutation.mutateAsync(data);
      if (response.success) {
        showToast({
          title: "Registration Submitted!",
          description: "Check your email for the verification code.",
          variant: "success",
          duration: 5000,
        });
        navigate(`/auth/verify?email=${encodeURIComponent(data.email)}`);
      }
    } catch (err: any) {
      if (err.response?.status === 422 && err.response?.data?.detail) {
        const details = err.response.data.detail;
        if (Array.isArray(details)) {
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
      } else if (err.response?.status === 500) {
        // Handle 500 errors specifically with user-friendly messages
        const errorMessage =
          err.response?.data?.detail ||
          err.message ||
          "A server error occurred. Please try again later.";
        setError(errorMessage);
        showToast({
          title: "Server Error",
          description: errorMessage,
          variant: "error",
          duration: 5000,
        });
      } else {
        // Handle all other errors
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
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="p-12 shadow-lg">
            <AuthHeader
              title="Create Your Salon Account"
              subtitle="Join thousands of salon owners managing their business with Kenikool"
              showLogo={true}
            />

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <p className="text-sm text-destructive font-medium">
                    {error}
                  </p>
                </div>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <RegistrationForm
                onSubmit={handleSubmit}
                isLoading={registerMutation.isPending || isSubmitting}
                error={error}
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Already have an account?{" "}
                  <Link
                    to="/auth/login"
                    className="text-primary hover:underline font-medium transition-colors"
                  >
                    Sign in
                  </Link>
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
            >
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
            </motion.div>

            <TrustIndicators />
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>Get 30 days free trial with all Enterprise features included</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
