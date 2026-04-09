import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "motion/react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { useAuthStore } from "@/stores/auth";
import { useTenantStore } from "@/stores/tenant";
import { useToast } from "@/components/ui/toast";
import { apiClient } from "@/lib/utils/api";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { FormFieldWithValidation } from "@/components/auth/FormFieldWithValidation";
import { TrustIndicators } from "@/components/auth/TrustIndicators";
import { validateEmail } from "@/lib/utils/auth-validation";

export default function Login() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState<boolean>(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [deletedAccountInfo, setDeletedAccountInfo] = useState<{
    days_remaining: number;
    recovery_token: string;
  } | null>(null);
  const [emailError, setEmailError] = useState("");
  const [isFormValid, setIsFormValid] = useState(false);

  const setUser = useAuthStore((state) => state.setUser);
  const setTenant = useTenantStore((state) => state.setTenant);

  // Validate form
  useEffect(() => {
    const isValid = !!(
      email &&
      password &&
      validateEmail(email) &&
      !emailError
    );
    setIsFormValid(isValid);
  }, [email, password, emailError]);

  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (value && !validateEmail(value)) {
      setEmailError("Please enter a valid email address");
    } else {
      setEmailError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await apiClient.post("/auth/login", {
        email,
        password,
        remember_me: rememberMe,
      });

      if (response.data) {
        // Fetch current user data
        const userResponse = await apiClient.get("/auth/me");
        if (userResponse.data) {
          // Backend returns { user: {...}, permissions: [...] }
          const userData = userResponse.data.user || userResponse.data;
          const roleNames = userData.roleNames || [];

          // Set user in auth store
          setUser({
            id: userData.id,
            email: userData.email,
            firstName: userData.firstName,
            lastName: userData.lastName,
            phone: userData.phone,
            role: roleNames[0] || "user",
            roleNames: roleNames,
            tenantId: userData.tenantId,
          });

          // Set tenant in store (minimal tenant object with just ID)
          // Tenant context comes from httpOnly cookie, no need for localStorage
          setTenant({
            id: userData.tenantId,
            name: "",
            subdomain: "",
            subscriptionTier: "starter",
            status: "active",
            isPublished: false,
          });

          // Show success toast
          showToast({
            title: "Welcome Back!",
            description: `Logged in as ${userData.email}`,
            variant: "success",
            duration: 3000,
          });

          // Determine redirect path based on role names
          // Route based on role priority (Owner > Manager > Staff > Customer)
          let redirectPath = "/dashboard"; // default

          if (roleNames.includes("Owner")) {
            redirectPath = "/dashboard"; // Owner Dashboard
          } else if (roleNames.includes("Manager")) {
            redirectPath = "/manager"; // Manager Dashboard
          } else if (roleNames.includes("Staff")) {
            redirectPath = "/appointments"; // Staff Dashboard - view their appointments
          } else if (roleNames.includes("Customer")) {
            redirectPath = "/my-account"; // Customer Dashboard
          }

          navigate(redirectPath);
        }
      }
    } catch (err: any) {
      if (
        err.response?.status === 403 &&
        (err.response?.headers["x-password-change-required"] ||
          err.response?.data?.password_change_required)
      ) {
        // Password change required - redirect to forced password change
        // The backend now provides a limited session for this
        showToast({
          title: "Password Change Required",
          description: "Please change your password to continue.",
          variant: "info",
          duration: 3000,
        });
        navigate("/auth/change-password-required");
      } else if (
        err.response?.status === 403 &&
        err.response?.headers["x-mfa-required"]
      ) {
        // MFA required - redirect to MFA verification
        showToast({
          title: "MFA Required",
          description: "Please verify your identity with your MFA method.",
          variant: "info",
          duration: 3000,
        });
        navigate("/auth/mfa-verify", { state: { email } });
      } else if (err.response?.data?.error === "account_deleted") {
        // Account is soft deleted but within grace period
        setDeletedAccountInfo({
          days_remaining: err.response.data.days_remaining,
          recovery_token: err.response.data.recovery_token,
        });
        setError(
          `Your account is deactivated. You have ${err.response.data.days_remaining} days to recover it.`,
        );
      } else if (err.response?.data?.error === "account_permanently_deleted") {
        // Account was permanently deleted
        setError(
          "Your account was permanently deleted. Contact support for paid recovery options.",
        );
      } else {
        const errorMessage =
          err.response?.data?.detail ||
          err.message ||
          "Failed to login. Please check your credentials.";
        setError(errorMessage);
        showToast({
          title: "Login Failed",
          description: errorMessage,
          variant: "error",
          duration: 5000,
        });
      }
    } finally {
      setIsLoading(false);
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
              title="Sign In"
              subtitle="Welcome back to Kenikool"
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
                  {deletedAccountInfo && (
                    <div className="mt-4 space-y-3">
                      <p className="text-sm font-semibold">
                        Recover your account within{" "}
                        {deletedAccountInfo.days_remaining} days:
                      </p>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          navigate(
                            `/auth/account-recovery?token=${deletedAccountInfo.recovery_token}`,
                          )
                        }
                        className="w-full"
                      >
                        Recover Account
                      </Button>
                    </div>
                  )}
                </Alert>
              </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0 }}
              >
                <FormFieldWithValidation
                  label="Email Address"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={handleEmailChange}
                  error={emailError}
                  disabled={isLoading}
                  validation={validateEmail}
                  validationMessage="Please enter a valid email"
                  showValidation={true}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={isLoading}
                      required
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      disabled={isLoading}
                    >
                      {showPassword ? (
                        <svg
                          className="w-5 h-5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path
                            fillRule="evenodd"
                            d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      ) : (
                        <svg
                          className="w-5 h-5"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z"
                            clipRule="evenodd"
                          />
                          <path d="M15.171 13.576l1.414 1.414A10.025 10.025 0 0019.542 10c-1.274-4.057-5.064-7-9.542-7a9.96 9.96 0 00-5.084 1.368l1.433 1.433C5.124 3.936 7.403 3 10 3c4.478 0 8.268 2.943 9.542 7a9.958 9.958 0 01-1.371 2.576z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      disabled={isLoading}
                      className="w-4 h-4 rounded border-border"
                    />
                    <span className="text-sm text-muted-foreground">
                      Remember me
                    </span>
                  </label>
                  <Link
                    to="/auth/forgot-password"
                    className="text-sm text-primary hover:underline transition-colors"
                  >
                    Forgot password?
                  </Link>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
                whileHover={{ scale: isFormValid ? 1.02 : 1 }}
                whileTap={{ scale: isFormValid ? 0.98 : 1 }}
              >
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={isLoading || !isFormValid}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <Spinner className="mr-2 h-4 w-4" />
                      Signing in...
                    </>
                  ) : (
                    "Sign In"
                  )}
                </Button>
              </motion.div>
            </form>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Don't have an account?{" "}
                  <Link
                    to="/auth/register"
                    className="text-primary hover:underline font-medium transition-colors"
                  >
                    Create one
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
                  By signing in, you agree to our{" "}
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
            <p>
              Need help?{" "}
              <a href="#" className="text-primary hover:underline">
                Contact Support
              </a>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
