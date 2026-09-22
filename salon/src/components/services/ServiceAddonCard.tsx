import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EditIcon, TrashIcon } from "@/components/icons";
import type { ServiceAddon } from "@/hooks/useServiceAddons";

interface ServiceAddonCardProps {
  addon: ServiceAddon;
  onEdit: (addon: ServiceAddon) => void;
  onDelete: (id: string, name: string) => void;
}

export function ServiceAddonCard({
  addon,
  onEdit,
  onDelete,
}: ServiceAddonCardProps) {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case "product":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "upgrade":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "treatment":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div
      className={`bg-card border border-border rounded-lg overflow-hidden hover:shadow-md transition ${
        !addon.is_active ? "opacity-60" : ""
      }`}
    >
      {/* Image */}
      {addon.image_url ? (
        <div className="w-full h-32 overflow-hidden bg-muted">
          <img
            src={addon.image_url}
            alt={addon.name}
            className="w-full h-full object-cover"
          />
        </div>
      ) : (
        <div className="w-full h-32 bg-muted flex items-center justify-center">
          <p className="text-muted-foreground text-sm">No image</p>
        </div>
      )}

      {/* Content */}
      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-foreground">
                {addon.name}
              </h3>
              {!addon.is_active && (
                <Badge variant="secondary" className="text-xs">
                  Inactive
                </Badge>
              )}
            </div>
            <Badge className={`${getCategoryColor(addon.category)} text-xs mb-2`}>
              {addon.category}
            </Badge>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(addon)}
              className="p-2 hover:bg-muted rounded-lg transition cursor-pointer"
            >
              <EditIcon size={16} className="text-muted-foreground" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(addon.id, addon.name)}
              className="p-2 hover:bg-destructive/10 rounded-lg transition cursor-pointer"
            >
              <TrashIcon size={16} className="text-destructive" />
            </Button>
          </div>
        </div>

        <p className="text-sm text-muted-foreground line-clamp-2">
          {addon.description}
        </p>

        <div className="flex items-center justify-between pt-2 border-t border-border">
          <div>
            <p className="text-xs text-muted-foreground">Duration</p>
            <p className="text-sm font-medium text-foreground">
              {addon.duration_minutes} min
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Price</p>
            <p className="text-sm font-medium text-foreground">
              ₦{typeof addon.price === "number"
                ? addon.price.toLocaleString()
                : parseFloat(String(addon.price)).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}