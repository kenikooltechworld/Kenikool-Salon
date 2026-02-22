import { useState } from "react";
import { Outlet } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Header } from "@/components/dashboard/header";
import { Breadcrumb } from "@/components/dashboard/breadcrumb";
import { useDashboardPrefetch } from "@/lib/api/hooks/useDashboardPrefetch";

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Prefetch dashboard data when layout mounts
  // This ensures data is available before components render,
  // eliminating loading states on navigation between dashboard pages
  useDashboardPrefetch({
    defaultPeriod: "month",
    immediate: true,
    activityLimit: 10,
    eventsDays: 7,
  });

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="lg:pl-64">
          <Header onMenuClick={() => setSidebarOpen(true)} />

          <main className="p-4 lg:p-6">
            <Breadcrumb />
            <Outlet />
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
