import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global error:", error);
  }, [error]);

  return (
    <html>
      <body>
        <div style={{ padding: "2rem", textAlign: "center" }}>
          <h1>Application Error</h1>
          <p>{error.message || "An unexpected error occurred"}</p>
          <button
            onClick={() => {
              // Clear all storage
              try {
                localStorage.clear();
                sessionStorage.clear();
                indexedDB.databases().then((dbs) => {
                  dbs.forEach((db) => {
                    if (db.name) indexedDB.deleteDatabase(db.name);
                  });
                });
              } catch (e) {
                console.error("Failed to clear storage:", e);
              }
              window.location.href = "/";
            }}
            style={{
              marginTop: "1rem",
              padding: "0.5rem 1rem",
              background: "#8B5CF6",
              color: "white",
              border: "none",
              borderRadius: "0.375rem",
              cursor: "pointer",
            }}
          >
            Clear cache and restart
          </button>
        </div>
      </body>
    </html>
  );
}
