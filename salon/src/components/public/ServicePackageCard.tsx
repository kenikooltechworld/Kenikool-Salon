import type { ServicePackage } from "@/hooks/useServicePackages";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDuration } from "@/lib/utils/format";
import { CheckIcon, ClockIcon, TagIcon } from "@/components/icons";

interface ServicePackageCardProps {
  package: ServicePackage;
  onSelect: (pkg: ServicePackage) => void;
}

export function ServicePackageCard({
  package: pkg,
  onSelect,
}: ServicePackageCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      {pkg.image_url && (
        <div className="relative h-48 overflow-hidden">
          <img
            src={pkg.image_url}
            alt={pkg.name}
            className="w-full h-full object-cover"
          />
          {pkg.is_featured && (
            <Badge className="absolute top-2 right-2 bg-yellow-500 text-white">
              Featured
            </Badge>
          )}
        </div>
      )}

      <div className="p-6">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-xl font-semibold">{pkg.name}</h3>
          {pkg.is_featured && !pkg.image_url && (
            <Badge className="bg-yellow-500 text-white">Featured</Badge>
          )}
        </div>

        {pkg.description && (
          <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
            {pkg.description}
          </p>
        )}

        <div className="space-y-3 mb-4">
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <ClockIcon className="w-4 h-4 mr-2" />
            <span>Total Duration: {formatDuration(pkg.total_duration)}</span>
          </div>

          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Includes {pkg.services.length} services:
            </p>
            <ul className="space-y-1">
              {pkg.services.slice(0, 3).map((service) => (
                <li
                  key={service.id}
                  className="flex items-start text-sm text-gray-600 dark:text-gray-400"
                >
                  <CheckIcon className="w-4 h-4 mr-2 mt-0.5 text-green-500 shrink-0" />
                  <span>
                    {service.service_name}
                    {service.quantity > 1 && ` (×${service.quantity})`}
                  </span>
                </li>
              ))}
              {pkg.services.length > 3 && (
                <li className="text-sm text-gray-500 dark:text-gray-500 ml-6">
                  +{pkg.services.length - 3} more services
                </li>
              )}
            </ul>
          </div>
        </div>

        <div className="border-t pt-4 mb-4">
          <div className="flex items-baseline justify-between mb-2">
            <div>
              <span className="text-2xl font-bold text-primary">
                {formatCurrency(pkg.package_price)}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 line-through ml-2">
                {formatCurrency(pkg.original_price)}
              </span>
            </div>
            <Badge
              variant="default"
              className="flex items-center gap-1 bg-green-500 text-white"
            >
              <TagIcon className="w-3 h-3" />
              Save {pkg.discount_percentage.toFixed(0)}%
            </Badge>
          </div>

          <p className="text-sm text-green-600 dark:text-green-400 font-medium">
            You save {formatCurrency(pkg.discount_amount)}
          </p>
        </div>

        {pkg.valid_until && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
            Valid until {new Date(pkg.valid_until).toLocaleDateString()}
          </p>
        )}

        {pkg.total_bookings_limit && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
            {pkg.total_bookings_limit - pkg.current_bookings_count} spots
            remaining
          </p>
        )}

        <Button
          onClick={() => onSelect(pkg)}
          className="w-full"
          disabled={!pkg.is_valid}
        >
          {pkg.is_valid ? "Book Package" : "Not Available"}
        </Button>
      </div>
    </Card>
  );
}
