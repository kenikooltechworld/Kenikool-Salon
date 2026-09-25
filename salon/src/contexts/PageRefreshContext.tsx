import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

interface PageRefreshContextValue {
  refreshHandler: (() => void) | null;
  setRefreshHandler: (handler: (() => void) | null) => void;
}

const PageRefreshContext = createContext<PageRefreshContextValue | undefined>(undefined);

export function PageRefreshProvider({ children }: { children: ReactNode }) {
  const [refreshHandler, setRefreshHandler] = useState<(() => void) | null>(null);

  return (
    <PageRefreshContext.Provider value={{ refreshHandler, setRefreshHandler }}>
      {children}
    </PageRefreshContext.Provider>
  );
}

export function usePageRefresh() {
  const context = useContext(PageRefreshContext);
  if (!context) {
    throw new Error("usePageRefresh must be used within PageRefreshProvider");
  }
  return context;
}
