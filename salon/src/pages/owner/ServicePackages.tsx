import { useState } from "react";
import {
  useServicePackages,
  useDeleteServicePackage,
  useTogglePackageActive,
  useTogglePackageFeatured,
} from "@/hooks/useServicePackages";
import type { ServicePackage } from "@/hooks/useServicePackages";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { formatCurrency, formatDuration } from "@/lib/utils/format";
import {
  PlusIcon,
  EditIcon,
  TrashIcon,
  EyeIcon,
  EyeOffIcon,
  StarIcon,
} from "@/components/icons";
import { useNavigate } from "react-router-dom";

export default function ServicePackages() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<{
    is_active?: boolean;
    is_featured?: boolean;
  }>({});

  const { data, isLoading, error } = useServicePackages({
    page,
    page_size: 20,
    ...filters,
  });

  const deletePackage = useDeleteServicePackage();
  const toggleActive = useTogglePackageActive();
  const toggleFeatured = useTogglePackageFeatured();

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to delete this package?")) {
      try {
        await deletePackage.mutateAsync(id);
      } catch (error) {
        console.error("Failed to delete package:", error);
      }
    }
  };

  const handleToggleActive = async (id: string) => {
    try {
      await toggleActive.mutateAsync(id);
    } catch (error) {
      console.error("Failed to toggle active status:", error);
    }
  };

  const handleToggleFeatured = async (id: string) => {
    try {
      await toggleFeatured.mutateAsync(id);
    } catch (error) {
      console.error("Failed to toggle featured status:", error);
    }
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
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Service Packages</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage bundled service packages
          </p>
        </div>
        <Button onClick={() => navigate("/owner/service-packages/create")}>
          <PlusIcon className="w-4 h-4 mr-2" />
          Create Package
        </Button>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center gap-4">
        <Button
          variant={filters.is_active === undefined ? "primary" : "outline"}
          onClick={() => setFilters({ ...filters, is_active: undefined })}
        >
          All
        </Button>
        <Button
          variant={filters.is_active === true ? "primary" : "outline"}
          onClick={() => setFilters({ ...filters, is_active: true })}
        >
          Active
        </Button>
        <Button
          variant={filters.is_active === false ? "primary" : "outline"}
          onClick={() => setFilters({ ...filters, is_active: false })}
        >
          Inactive
        </Button>
        <Button
          variant={filters.is_featured === true ? "primary" : "outline"}
          onClick={() =>
            setFilters({
              ...filters,
              is_featured: filters.is_featured ? undefined : true,
            })
          }
        >
          Featured Only
        </Button>
      </div>

      {/* Packages List */}
      {data && data.packages.length > 0 ? (
        <>
          <div className="space-y-4 mb-8">
            {data.packages.map((pkg) => (
              <PackageCard
                key={pkg.id}
                package={pkg}
                onEdit={() =>
                  navigate(`/owner/service-packages/${pkg.id}/edit`)
                }
                onDelete={() => handleDelete(pkg.id)}
                onToggleActive={() => handleToggleActive(pkg.id)}
                onToggleFeatured={() => handleToggleFeatured(pkg.id)}
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
        <Card className="p-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            No service packages found.
          </p>
          <Button onClick={() => navigate("/owner/service-packages/create")}>
            <PlusIcon className="w-4 h-4 mr-2" />
            Create Your First Package
          </Button>
        </Card>
      )}
    </div>
  );
}

interface PackageCardProps {
  package: ServicePackage;
  onEdit: () => void;
  onDelete: () => void;
  onToggleActive: () => void;
  onToggleFeatured: () => void;
}

function PackageCard({
  package: pkg,
  onEdit,
  onDelete,
  onToggleActive,
  onToggleFeatured,
}: PackageCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-xl font-semibold">{pkg.name}</h3>
            {pkg.is_featured && (
              <Badge className="bg-yellow-500 text-white">Featured</Badge>
            )}
            {!pkg.is_active && <Badge variant="secondary">Inactive</Badge>}
            {!pkg.is_valid && <Badge variant="destructive">Expired</Badge>}
          </div>

          {pkg.description && (
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {pkg.description}
            </p>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Services
              </p>
              <p className="font-medium">{pkg.services.length} services</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Duration
              </p>
              <p className="font-medium">
                {formatDuration(pkg.total_duration)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Bookings
              </p>
              <p className="font-medium">
                {pkg.current_bookings_count}
                {pkg.total_bookings_limit && ` / ${pkg.total_bookings_limit}`}
              </p>
            </div>
          </div>

          <div className="flex items-baseline gap-4">
            <div>
              <span className="text-2xl font-bold text-primary">
                {formatCurrency(pkg.package_price)}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 line-through ml-2">
                {formatCurrency(pkg.original_price)}
              </span>
            </div>
            <Badge variant="default" className="bg-green-500 text-white">
              Save {pkg.discount_percentage.toFixed(0)}%
            </Badge>
          </div>
        </div>

        <div className="flex items-center gap-2 ml-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleActive}
            title={pkg.is_active ? "Deactivate" : "Activate"}
          >
            {pkg.is_active ? (
              <EyeIcon className="w-4 h-4" />
            ) : (
              <EyeOffIcon className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleFeatured}
            title={pkg.is_featured ? "Unfeature" : "Feature"}
          >
            <StarIcon
              className={`w-4 h-4 ${
                pkg.is_featured ? "fill-yellow-500 text-yellow-500" : ""
              }`}
            />
          </Button>
          <Button variant="ghost" size="sm" onClick={onEdit}>
            <EditIcon className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={onDelete}>
            <TrashIcon className="w-4 h-4 text-red-500" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
