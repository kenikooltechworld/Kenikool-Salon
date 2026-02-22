import React, { Component, ErrorInfo, ReactNode } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangleIcon, RefreshCwIcon } from "@/components/icons";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class DashboardErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console
    console.error("Dashboard Error:", error);
    console.error("Error Info:", errorInfo);

    // Log to external service if available
    if (typeof window !== "undefined") {
      // You can integrate with error tracking services here
      // Example: Sentry, LogRocket, etc.
      try {
        const errorData = {
          error: {
            message: error.message,
            stack: error.stack,
          },
          errorInfo: {
            componentStack: errorInfo.componentStack,
          },
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
        };
        console.log("Error logged:", errorData);
      } catch (loggingError) {
        console.error("Failed to log error:", loggingError);
      }
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    this.setState({
      errorInfo,
    });
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
          <Card className="max-w-2xl w-full p-8 animate-in fade-in-0 zoom-in-95 duration-300">
            <div className="flex flex-col items-center text-center space-y-6">
              <div className="p-4 bg-[var(--error)]/10 rounded-full">
                <AlertTriangleIcon size={48} className="text-[var(--error)]" />
              </div>

              <div className="space-y-2">
                <h1 className="text-2xl font-bold text-foreground">
                  Something went wrong
                </h1>
                <p className="text-muted-foreground">
                  We encountered an error while loading the dashboard. Please
                  try again.
                </p>
              </div>

              {import.meta.env.MODE === "development" && this.state.error && (
                <div className="w-full p-4 bg-muted rounded-lg text-left">
                  <p className="text-sm font-semibold text-foreground mb-2">
                    Error Details:
                  </p>
                  <p className="text-xs text-muted-foreground font-mono break-all">
                    {this.state.error.message}
                  </p>
                  {this.state.error.stack && (
                    <details className="mt-2">
                      <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                        Stack Trace
                      </summary>
                      <pre className="text-xs text-muted-foreground mt-2 overflow-auto max-h-40">
                        {this.state.error.stack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              <div className="flex gap-3">
                <Button
                  onClick={this.handleRetry}
                  className="transition-all duration-200 ease-out hover:scale-105"
                >
                  <RefreshCwIcon size={16} className="mr-2" />
                  Try Again
                </Button>
                <Button
                  variant="outline"
                  onClick={this.handleReload}
                  className="transition-all duration-200 ease-out hover:scale-105"
                >
                  Reload Page
                </Button>
              </div>

              <p className="text-xs text-muted-foreground">
                If the problem persists, please contact support.
              </p>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook version for functional components
export function useDashboardErrorHandler() {
  const handleError = (error: Error, errorInfo: ErrorInfo) => {
    console.error("Dashboard Error:", error);
    console.error("Error Info:", errorInfo);
  };

  return { handleError };
}
