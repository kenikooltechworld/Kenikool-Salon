import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScissorsIcon } from "@/components/icons";

export function LandingHeader() {
  return (
    <header className="border-b border-[var(--border)] bg-[var(--card)]">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ScissorsIcon size={32} className="text-[var(--primary)]" />
            <span className="text-2xl font-bold">Kenikool</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link to="/register">
              <Button variant="primary">Get Started</Button>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
