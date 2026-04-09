import { useState } from "react";
import { usePublicServicePackages } from "@/hooks/useServicePackages";
import type { ServicePackage } from "@/hooks/useServicePackages";
import { ServicePackageCard } from "@/components/public/ServicePackageCard";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { useNavigate } from "react-router-dom";

export default function ServicePackages() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);

  const { data, isLoading, error } = usePublicServicePackages({
    page,
    page_size: 12,
    is_featured: showFeaturedOnly || undefined,
  });

  const handleSelectPackage = (pkg: ServicePackage) => {
    // Navigate to booking page with package pre-selected
    navigate("/book", { state: { packageId: pkg.id } });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="error">
          Failed to load service packages. Please try again later.
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Service Packages</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Save more with our bundled service packages
          </p>
        </div>

        {/* Filters */}
        <div className="mb-6 flex items-center gap-4">
          <Button
            variant={showFeaturedOnly ? "primary" : "outline"}
            onClick={() => setShowFeaturedOnly(!showFeaturedOnly)}
          >
            {showFeaturedOnly ? "Show All" : "Featured Only"}
          </Button>
        </div>

        {/* Packages Grid */}
        {data && data.packages.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {data.packages.map((pkg) => (
                <ServicePackageCard
                  key={pkg.id}
                  package={pkg}
                  onSelect={handleSelectPackage}
                />
              ))}
            </div>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Page {page} of {data.total_pages}
                </span>
                <Button
                  variant="outline"
                  onClick={() =>
                    setPage((p) => Math.min(data.total_pages, p + 1))
                  }
                  disabled={page === data.total_pages}
                >
                  Next
                </Button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No service packages available at the moment.
            </p>
            <Button onClick={() => navigate("/book")}>
              Book Individual Services
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
