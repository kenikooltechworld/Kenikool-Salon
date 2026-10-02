import type { ReactNode } from "react";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex h-screen bg-background">
      {/* Mobile: hidden by default, collapsible sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 w-[280px] -translate-x-full md:relative md:translate-x-0 md:w-64 bg-card border-r border-border transition-transform duration-300">
        <div className="h-16 border-b border-border flex items-center px-4">
          <span className="font-bold text-lg text-foreground">Menu</span>
        </div>
        <nav className="flex-1 overflow-y-auto p-2">
          <div className="space-y-1">
            <a href="/" className="block px-4 py-3 rounded-xl text-foreground hover:bg-muted transition min-h-[44px] flex items-center">
              Home
            </a>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden w-full">
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-4 md:px-6">
          <h1 className="text-lg font-semibold text-foreground">Main</h1>
        </header>
        <div className="flex-1 overflow-auto p-4 md:p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
