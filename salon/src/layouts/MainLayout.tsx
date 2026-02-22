import { ReactNode } from "react";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-100">Sidebar</aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
