import { useAuth } from "../../lib/hooks/useAuth";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-lg">Welcome back, {user?.full_name}!</p>
        <p className="text-gray-600 mt-2">
          Your salon management dashboard is ready.
        </p>
      </div>
    </div>
  );
}
