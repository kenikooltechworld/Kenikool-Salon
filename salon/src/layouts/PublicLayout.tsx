import { Outlet } from "react-router-dom";
import { Navbar } from "@/components/Navbar";

export function PublicLayout() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1 pt-16">
        <Outlet />
      </main>
    </div>
  );
}
