import { ReactNode } from "react";

interface AdminLayoutProps {
  children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-900 text-white">Admin Sidebar</aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
