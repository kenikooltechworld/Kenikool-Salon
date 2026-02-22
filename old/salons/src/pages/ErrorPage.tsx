import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Application error:", error);
  }, [error]);

  const handleClearCache = async () => {
    try {
      // Clear IndexedDB
      const dbs = await indexedDB.databases();
      for (const db of dbs) {
        if (db.name) {
          indexedDB.deleteDatabase(db.name);
        }
      }

      // Clear localStorage
      localStorage.clear();

      // Clear sessionStorage
      sessionStorage.clear();

      // Reload the page
      window.location.reload();
    } catch (e) {
      console.error("Failed to clear cache:", e);
      showToast(
        "Please manually clear your browser data and refresh the page.",
        "error",
      );
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md space-y-6 rounded-lg bg-white p-8 shadow-lg">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-bold text-gray-900">
            Something went wrong
          </h1>
          <p className="text-sm text-gray-600">
            {error.message || "An unexpected error occurred"}
          </p>
        </div>

        <div className="space-y-3">
          <Button onClick={reset} className="w-full">
            Try again
          </Button>

          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            className="w-full"
          >
            Reload page
          </Button>

          <Button
            onClick={handleClearCache}
            variant="outline"
            className="w-full"
          >
            Clear cache and reload
          </Button>
        </div>

        <div className="rounded-md bg-gray-100 p-4">
          <p className="text-xs text-gray-600">If the problem persists, try:</p>
          <ul className="mt-2 list-inside list-disc space-y-1 text-xs text-gray-600">
            <li>Close all other tabs with this app</li>
            <li>Clear your browser cache manually</li>
            <li>Use incognito/private mode</li>
            <li>Contact support if the issue continues</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
