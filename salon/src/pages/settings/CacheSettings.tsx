import { useCacheOptimization } from "@/hooks/useCacheOptimization";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { BarChartIcon, Trash2Icon, RefreshCwIcon } from "@/components/icons";

export default function CacheSettings() {
  const { cacheStats, isLoadingStats, warmCache, clearCache, invalidateCache } =
    useCacheOptimization();
  const navigate = useNavigate();

  if (isLoadingStats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spinner />
      </div>
    );
  }

  const cacheTypes = [
    { key: "appointments", label: "Appointments" },
    { key: "customers", label: "Customers" },
    { key: "staff", label: "Staff" },
    { key: "services", label: "Services" },
    { key: "invoices", label: "Invoices" },
    { key: "payments", label: "Payments" },
  ];

  return (
    <div className="space-y-6 p-6">
      {/* Back Button */}
      <button
        onClick={() => navigate("/settings")}
        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        ← Back to Settings
      </button>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Cache Optimization</h1>
        <p className="text-gray-600 mt-1">
          Manage application cache and performance settings
        </p>
      </div>

      {/* Cache Statistics */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <BarChartIcon size={24} />
          <h2 className="text-xl font-semibold">Cache Statistics</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Keys</p>
            <p className="text-3xl font-bold">{cacheStats?.total_keys || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Hits</p>
            <p className="text-3xl font-bold">{cacheStats?.hits || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Misses</p>
            <p className="text-3xl font-bold">{cacheStats?.misses || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Hit Rate</p>
            <p className="text-3xl font-bold">
              {((cacheStats?.hit_rate || 0) * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </Card>

      {/* Cache Management */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cache Types */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Cache Types</h2>
            <div className="space-y-3">
              {cacheTypes.map((cache) => (
                <div
                  key={cache.key}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                >
                  <div>
                    <p className="font-medium">{cache.label}</p>
                    <p className="text-sm text-gray-600">
                      {cacheStats?.key_types?.[cache.key] || 0} entries
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <RefreshCwIcon size={16} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => invalidateCache(cache.key)}
                    >
                      <Trash2Icon size={16} className="text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Actions */}
        <div className="space-y-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Cache Actions</h3>
            <div className="space-y-2">
              <Button
                onClick={() => warmCache()}
                className="w-full gap-2"
                variant="outline"
              >
                <RefreshCwIcon size={18} />
                Warm Cache
              </Button>
              <Button
                onClick={() => clearCache()}
                className="w-full gap-2"
                variant="destructive"
              >
                <Trash2Icon size={18} />
                Clear All Cache
              </Button>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold mb-3">Status</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Redis Status</span>
                <Badge variant="outline" className="text-green-700">
                  Connected
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Updated</span>
                <span className="font-medium">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Cache Performance */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600">Total Keys</p>
            <p className="text-2xl font-bold">{cacheStats?.total_keys || 0}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-600">Cache Hits</p>
            <p className="text-2xl font-bold">{cacheStats?.hits || 0}</p>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg">
            <p className="text-sm text-gray-600">Cache Misses</p>
            <p className="text-2xl font-bold">{cacheStats?.misses || 0}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
