import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "@/components/icons";
import { AuthHeader } from "@/components/auth/AuthHeader";
import { TrustIndicators } from "@/components/auth/TrustIndicators";
import { useToast } from "@/components/ui/toast";

export function RegisterSuccess() {
  const navigate = useNavigate();
  const location = useLocation();
  const [countdown, setCountdown] = useState(5);
  const [copied, setCopied] = useState(false);
  const { addToast } = useToast();

  const subdomain = (location.state as any)?.subdomain || "";
  const full_url = (location.state as any)?.full_url || "";

  // Auto-redirect after 5 seconds
  useEffect(() => {
    if (countdown <= 0) {
      navigate("/dashboard");
      return;
    }

    const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown, navigate]);

  // Redirect if no subdomain
  useEffect(() => {
    if (!subdomain) {
      navigate("/auth/register");
    }
  }, [subdomain, navigate]);

  const handleCopySubdomain = async () => {
    try {
      await navigator.clipboard.writeText(subdomain);
      setCopied(true);
      addToast({
        title: "Copied",
        description: "Subdomain copied to clipboard",
        variant: "success",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to copy subdomain",
        variant: "error",
      });
    }
  };

  if (!subdomain) {
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
              title="🎉 Welcome to Kenikool!"
              subtitle="Your salon account has been created successfully"
              showLogo={true}
            />

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <div className="space-y-6">
                <div className="flex justify-center">
                  <CheckCircle className="w-16 h-16 text-green-500" />
                </div>

                <div className="bg-muted p-6 rounded-lg">
                  <p className="text-sm text-muted-foreground mb-2">
                    Your Salon URL:
                  </p>
                  <p className="text-lg font-mono font-semibold text-foreground break-all mb-4">
                    {full_url || subdomain}
                  </p>
                  <Button
                    onClick={handleCopySubdomain}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    {copied ? "✓ Copied" : "Copy Subdomain URL"}
                  </Button>
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                >
                  <div className="bg-[var(--primary)]/10 border border-[var(--primary)]/20 p-4 rounded-lg">
                    <p className="text-sm font-medium text-[var(--primary)] mb-2">
                      🎁 30-Day Free Trial
                    </p>
                    <p className="text-sm text-muted-foreground">
                      You have access to all Enterprise features for 30 days. No
                      credit card required.
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                >
                  <div className="space-y-3">
                    <h3 className="font-semibold text-foreground">
                      Quick Start Guide:
                    </h3>
                    <ol className="text-sm text-muted-foreground space-y-2 text-left">
                      <li>1. Add your staff members</li>
                      <li>2. Create your services and pricing</li>
                      <li>3. Set your working hours</li>
                      <li>4. Share your salon URL with customers</li>
                    </ol>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button
                    onClick={() => navigate("/dashboard")}
                    variant="primary"
                    size="lg"
                    className="w-full"
                  >
                    Go to Dashboard
                  </Button>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3, delay: 0.5 }}
                >
                  <p className="text-xs text-muted-foreground text-center">
                    Redirecting in {countdown}s...
                  </p>
                </motion.div>
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
