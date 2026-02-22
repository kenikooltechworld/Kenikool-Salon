import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { XIcon } from "@/components/icons";
import { getIconComponent } from "@/lib/utils/icon-utils";
import type { Service } from "@/types/service";
import { formatCurrency } from "@/lib/utils/format";

interface ServiceDetailModalProps {
  isOpen: boolean;
  service: Service;
  onClose: () => void;
  onSelect: () => void;
}

export function ServiceDetailModal({
  isOpen,
  service,
  onClose,
  onSelect,
}: ServiceDetailModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              {/* Service Icon */}
              {service.icon &&
                (() => {
                  const IconComponent = getIconComponent(service.icon);
                  return IconComponent ? (
                    <div className="flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center bg-primary">
                      <IconComponent
                        size={24}
                        className="text-primary-foreground"
                      />
                    </div>
                  ) : null;
                })()}
              <div className="min-w-0">
                <h2 className="text-2xl font-bold text-foreground">
                  {service.name}
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {service.category}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="p-2 cursor-pointer flex-shrink-0"
            >
              <XIcon size={20} />
            </Button>
          </div>

          {/* Image */}
          {service.public_image_url && (
            <div className="rounded-lg overflow-hidden bg-muted">
              <img
                src={service.public_image_url}
                alt={service.name}
                className="w-full h-64 object-cover"
              />
            </div>
          )}

          {/* Description */}
          <div>
            <h3 className="font-semibold text-foreground mb-2">Description</h3>
            <p className="text-sm text-muted-foreground">
              {service.description || "No description provided"}
            </p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground font-medium">
                Duration
              </p>
              <p className="text-lg font-semibold text-foreground">
                {service.duration_minutes} min
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground font-medium">Price</p>
              <p className="text-lg font-semibold text-foreground">
                {formatCurrency(service.price, "NGN")}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground font-medium">
                Status
              </p>
              <Badge variant={service.is_active ? "default" : "secondary"}>
                {service.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground font-medium">
                Published
              </p>
              <Badge variant={service.is_published ? "default" : "secondary"}>
                {service.is_published ? "Yes" : "No"}
              </Badge>
            </div>
          </div>

          {/* Tags */}
          {service.tags && service.tags.length > 0 && (
            <div>
              <h3 className="font-semibold text-foreground mb-2">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {service.tags.map((tag: string) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Quick Info */}
          <Card className="p-4 bg-muted/50">
            <h3 className="font-semibold text-foreground mb-3">Quick Info</h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-muted-foreground">Created</p>
                <p className="text-sm font-medium text-foreground">
                  {new Date(service.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Last Updated</p>
                <p className="text-sm font-medium text-foreground">
                  {new Date(service.updated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </Card>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-border">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1 cursor-pointer"
            >
              Close
            </Button>
            <Button onClick={onSelect} className="flex-1 cursor-pointer">
              Select This Service
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
