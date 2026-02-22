import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EditIcon, TrashIcon, TagIcon } from "@/components/icons";

interface Package {
  id: string;
  name: string;
  description: string;
  service_ids: string[];
  package_price: number;
  total_service_price: number;
  savings: number;
  savings_percentage: number;
  valid_from: string | null;
  valid_until: string | null;
  is_active: boolean;
}

interface PackageListProps {
  packages: Package[];
  onEdit: (pkg: Package) => void;
  onDelete: (id: string, name: string) => void;
  onToggleActive: (id: string, currentStatus: boolean) => void;
}

export function PackageList({
  packages,
  onEdit,
  onDelete,
  onToggleActive,
}: PackageListProps) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return null;
    }
  };

  const isExpired = (validUntil: string | null) => {
    if (!validUntil) return false;
    return new Date(validUntil) < new Date();
  };

  if (packages.length === 0) {
    return (
      <Card className="p-8 text-center">
        <TagIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <p className="text-muted-foreground mb-2">No packages created yet</p>
        <p className="text-sm text-muted-foreground">
          Create packages to offer bundled services at discounted prices
        </p>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {packages.map((pkg) => {
        const expired = isExpired(pkg.valid_until);

        return (
          <Card key={pkg.id} className="p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="font-bold text-lg text-foreground mb-1">
                  {pkg.name}
                </h3>
                <div className="flex gap-2 flex-wrap">
                  <Badge
                    variant={
                      pkg.is_active && !expired ? "success" : "secondary"
                    }
                  >
                    {expired
                      ? "Expired"
                      : pkg.is_active
                      ? "Active"
                      : "Inactive"}
                  </Badge>
                  <Badge variant="primary">
                    {pkg.service_ids.length} service
                    {pkg.service_ids.length !== 1 ? "s" : ""}
                  </Badge>
                </div>
              </div>
            </div>

            {pkg.description && (
              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {pkg.description}
              </p>
            )}

            {/* Pricing */}
            <div className="space-y-2 mb-4">
              <div className="flex justify-between items-baseline">
                <span className="text-sm text-muted-foreground line-through">
                  ₦{pkg.total_service_price.toLocaleString()}
                </span>
                <span className="text-2xl font-bold text-foreground">
                  ₦{pkg.package_price.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900/20 rounded">
                <span className="text-sm font-medium text-green-700 dark:text-green-400">
                  Save ₦{pkg.savings.toLocaleString()}
                </span>
                <span className="text-sm font-bold text-green-700 dark:text-green-400">
                  {pkg.savings_percentage.toFixed(1)}% OFF
                </span>
              </div>
            </div>

            {/* Validity */}
            {(pkg.valid_from || pkg.valid_until) && (
              <div className="text-xs text-muted-foreground mb-4 space-y-1">
                {pkg.valid_from && (
                  <p>Valid from: {formatDate(pkg.valid_from)}</p>
                )}
                {pkg.valid_until && (
                  <p className={expired ? "text-red-500 font-medium" : ""}>
                    Valid until: {formatDate(pkg.valid_until)}
                  </p>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4 border-t border-border">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onToggleActive(pkg.id, pkg.is_active)}
                className="flex-1"
              >
                {pkg.is_active ? "Deactivate" : "Activate"}
              </Button>
              <Button variant="outline" size="sm" onClick={() => onEdit(pkg)}>
                <EditIcon size={16} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onDelete(pkg.id, pkg.name)}
              >
                <TrashIcon size={16} />
              </Button>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
