import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "@/components/icons";

export function RegisterSuccess() {
  const navigate = useNavigate();
  const location = useLocation();
  const [countdown, setCountdown] = useState(5);

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

  if (!subdomain) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="p-8 text-center">
          <div className="mb-6 flex justify-center">
            <CheckCircle className="w-16 h-16 text-green-500" />
          </div>

          <h1 className="text-3xl font-bold text-foreground mb-2">
            Welcome to Kenikool!
          </h1>

          <p className="text-muted-foreground mb-6">
            Your salon account has been created successfully
          </p>

          <div className="bg-muted p-4 rounded-lg mb-6">
            <p className="text-sm text-muted-foreground mb-2">
              Your Salon URL:
            </p>
            <p className="text-lg font-mono font-semibold text-foreground break-all">
              {full_url || subdomain}
            </p>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-4 rounded-lg mb-6">
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
              🎉 30-Day Free Trial
            </p>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              You have access to all Enterprise features for 30 days. No credit
              card required.
            </p>
          </div>

          <div className="space-y-3 mb-6">
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

          <Button
            onClick={() => navigate("/dashboard")}
            className="w-full mb-3"
          >
            Go to Dashboard
          </Button>

          <p className="text-xs text-muted-foreground">
            Redirecting in {countdown}s...
          </p>
        </Card>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          <p>
            Need help?{" "}
            <a href="#" className="text-primary hover:underline">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
