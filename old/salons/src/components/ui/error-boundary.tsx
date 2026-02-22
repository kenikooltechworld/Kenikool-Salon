import React, { ReactNode, ReactElement } from "react";
import { AlertTriangleIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactElement;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <Card className="p-6 border-2 border-[var(--error)]/20 bg-[var(--error)]/5">
            <div className="flex items-start gap-3">
              <AlertTriangleIcon
                size={20}
                className="text-[var(--error)] flex-shrink-0 mt-0.5"
              />
              <div>
                <h3 className="font-semibold text-[var(--error)]">
                  Error Loading Widget
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {this.state.error?.message ||
                    "An error occurred while loading this component"}
                </p>
              </div>
            </div>
          </Card>
        )
      );
    }

    return this.props.children;
  }
}
