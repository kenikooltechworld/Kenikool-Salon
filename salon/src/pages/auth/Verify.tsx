import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { VerificationCodeInput } from "@/components/VerificationCodeInput";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { TrustIndicators } from "@/components/auth/TrustIndicators";
import {
  useVerifyRegistrationCode,
  useResendVerificationCode,
} from "@/hooks/useRegistration";
import { useAuthStore } from "@/stores/auth";
import { useToast } from "@/components/ui/toast";

export function Verify() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { showToast } = useToast();
  const [code, setCode] = useState("");
  const [error, setError] = useState<string>("");
  const [resendCountdown, setResendCountdown] = useState(0);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successData, setSuccessData] = useState<{
    subdomain: string;
    full_url: string;
    tenant_id: string;
  } | null>(null);

  const email = searchParams.get("email") || "";
  const setUser = useAuthStore((state) => state.setUser);

  const verifyMutation = useVerifyRegistrationCode();
  const resendMutation = useResendVerificationCode();

  // Redirect if no email
  useEffect(() => {
    if (!email) {
      navigate("/auth/register");
    }
  }, [email, navigate]);

  // Auto-close success modal after 30 seconds
  useEffect(() => {
    if (!showSuccessModal) return;
    const timer = setTimeout(() => {
      navigate("/auth/register-success", {
        state: {
          subdomain: successData?.subdomain,
          full_url: successData?.full_url,
          tenant_id: successData?.tenant_id,
        },
      });
    }, 30000);
    return () => clearTimeout(timer);
  }, [showSuccessModal, successData, navigate]);

  // Resend countdown
  useEffect(() => {
    if (resendCountdown <= 0) return;
    const timer = setTimeout(
      () => setResendCountdown(resendCountdown - 1),
      1000,
    );
    return () => clearTimeout(timer);
  }, [resendCountdown]);

  const handleVerify = async () => {
    if (code.length !== 6) {
      setError("Please enter all 6 digits");
      return;
    }

    setError("");
    try {
      const response = await verifyMutation.mutateAsync({
        email,
        code,
      });

      if (response.success && response.data) {
        // Store user data (tokens are handled by httpOnly cookies)
        setUser({
          id: response.data.user_id,
          email,
          firstName: "",
          lastName: "",
          phone: "",
          role: "owner",
          roleNames: ["Owner"],
          tenantId: response.data.tenant_id,
        });

        // Show success toast
        showToast({
          title: "Registration Successful!",
          description: "Your account has been created successfully.",
          variant: "success",
          duration: 5000,
        });

        // Store success data and show modal
        setSuccessData({
          subdomain: response.data.subdomain,
          full_url: response.data.full_url,
          tenant_id: response.data.tenant_id,
        });
        setShowSuccessModal(true);
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Failed to verify code. Please try again.";
      setError(errorMessage);
      showToast({
        title: "Verification Failed",
        description: errorMessage,
        variant: "error",
        duration: 5000,
      });
    }
  };

  const handleResend = async () => {
    setError("");
    try {
      const response = await resendMutation.mutateAsync(email);
      if (response.success) {
        setCode("");
        // Start resend cooldown (60 seconds)
        setResendCountdown(60);
        showToast({
          title: "Code Sent!",
          description: "A new verification code has been sent to your email.",
          variant: "success",
          duration: 5000,
        });
      }
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Failed to resend code. Please try again.";
      setError(errorMessage);
      showToast({
        title: "Failed to Send Code",
        description: errorMessage,
        variant: "error",
        duration: 5000,
      });
    }
  };

  const handleCopyUrl = async () => {
    if (successData?.full_url) {
      try {
        await navigator.clipboard.writeText(successData.full_url);
        showToast({
          title: "Copied!",
          description: "Subdomain URL copied to clipboard",
          variant: "success",
          duration: 3000,
        });
      } catch (err) {
        showToast({
          title: "Failed to Copy",
          description: "Could not copy to clipboard",
          variant: "error",
          duration: 3000,
        });
      }
    }
  };

  if (!email) {
    return null;
  }

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
              title="Verify Your Email"
              subtitle="Enter the code we sent to your email"
              showLogo={true}
            />

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Alert variant="error" className="mb-6">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <div className="space-y-6">
                <div className="text-center">
                  <p className="text-muted-foreground">
                    We sent a 6-digit code to{" "}
                    <span className="font-medium text-foreground">{email}</span>
                  </p>
                </div>

                <VerificationCodeInput
                  value={code}
                  onChange={setCode}
                  disabled={verifyMutation.isPending}
                  error={error}
                />

                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                  whileHover={{ scale: code.length === 6 ? 1.02 : 1 }}
                  whileTap={{ scale: code.length === 6 ? 0.98 : 1 }}
                >
                  <Button
                    onClick={handleVerify}
                    disabled={code.length !== 6 || verifyMutation.isPending}
                    variant="primary"
                    size="lg"
                    className="w-full"
                  >
                    {verifyMutation.isPending ? (
                      <>
                        <Spinner className="mr-2 h-4 w-4" />
                        Verifying...
                      </>
                    ) : (
                      "Verify Code"
                    )}
                  </Button>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                >
                  <div className="text-center">
                    <p className="text-sm text-muted-foreground mb-3">
                      Didn't receive the code?
                    </p>
                    <Button
                      variant="outline"
                      onClick={handleResend}
                      disabled={resendCountdown > 0 || resendMutation.isPending}
                      className="w-full"
                    >
                      {resendMutation.isPending ? (
                        <>
                          <Spinner className="mr-2 h-4 w-4" />
                          Sending...
                        </>
                      ) : resendCountdown > 0 ? (
                        `Resend in ${resendCountdown}s`
                      ) : (
                        "Resend Code"
                      )}
                    </Button>
                  </div>
                </motion.div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <div className="mt-6 pt-6 border-t border-border text-center">
                <Button
                  variant="ghost"
                  onClick={() => navigate("/auth/register")}
                  className="text-sm"
                >
                  Back to Registration
                </Button>
              </div>
            </motion.div>

            <TrustIndicators />
          </Card>
        </motion.div>
      </div>

      {/* Success Modal */}
      <Modal
        open={showSuccessModal}
        onClose={() => {
          navigate("/auth/register-success", {
            state: {
              subdomain: successData?.subdomain,
              full_url: successData?.full_url,
              tenant_id: successData?.tenant_id,
            },
          });
        }}
        size="md"
        showCloseButton={true}
      >
        <ModalHeader>
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <ModalTitle className="text-center">🎉 Congratulations!</ModalTitle>
          </div>
        </ModalHeader>
        <ModalBody>
          <div className="text-center space-y-4">
            <p className="text-lg font-semibold text-foreground">
              Your account has been created successfully!
            </p>
            <p className="text-muted-foreground">
              Welcome to Kenikool. Your salon management platform is ready to
              use.
            </p>
            <div className="bg-muted p-4 rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">
                Your Subdomain:
              </p>
              <p className="font-mono font-semibold text-foreground break-all">
                {successData?.full_url}
              </p>
              <Button
                onClick={handleCopyUrl}
                variant="outline"
                size="sm"
                className="mt-3 w-full"
              >
                Copy Subdomain URL
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              This modal will close automatically in 30 seconds, or you can
              close it now.
            </p>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button
            onClick={() => {
              navigate("/auth/register-success", {
                state: {
                  subdomain: successData?.subdomain,
                  full_url: successData?.full_url,
                  tenant_id: successData?.tenant_id,
                },
              });
            }}
            className="w-full"
          >
            Continue to Dashboard
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
}
