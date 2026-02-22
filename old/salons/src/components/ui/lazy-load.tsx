import { Suspense, lazy, ComponentType } from "react";
import { Spinner } from "./spinner";

interface LazyLoadProps {
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * Lazy loading wrapper component for performance optimization
 *
 * Requirements: Task 5.7 - Performance Optimization
 */
export function LazyLoad({ fallback, children }: LazyLoadProps) {
  return (
    <Suspense
      fallback={
        fallback || (
          <div className="flex justify-center items-center py-12">
            <Spinner size="lg" />
          </div>
        )
      }
    >
      {children}
    </Suspense>
  );
}

/**
 * Helper function to create lazy-loaded components
 */
export function createLazyComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>
) {
  return lazy(importFn);
}
