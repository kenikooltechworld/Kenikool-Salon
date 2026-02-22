import { Outlet } from "react-router-dom";
import { Link } from "react-router-dom";
import { ThemeSelector } from "@/components/ui/theme-selector";

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navbar */}
      <header className="h-16 border-b border-border flex items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">K</span>
          </div>
          <span className="font-bold text-lg text-foreground hidden sm:inline">
            Kenikool
          </span>
        </Link>

        <ThemeSelector variant="icon" />
      </header>

      {/* Auth Content */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
