import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UserIcon, EditIcon, TrashIcon } from "@/components/icons";
import type { Stylist } from "@/lib/api/types";

interface StylistHeaderProps {
  stylist: Stylist;
  onEdit: () => void;
  onDelete: () => void;
  onPhotoClick: () => void;
}

export function StylistHeader({
  stylist,
  onEdit,
  onDelete,
  onPhotoClick,
}: StylistHeaderProps) {
  return (
    <Card className="p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
        {/* Stylist Photo */}
        <div
          className="w-full sm:w-32 md:w-40 lg:w-48 h-48 sm:h-32 md:h-40 lg:h-48 rounded-lg overflow-hidden bg-muted shrink-0 cursor-pointer hover:opacity-80 transition-opacity"
          onClick={onPhotoClick}
        >
          {stylist.photo_url ? (
            <img
              src={stylist.photo_url}
              alt={stylist.name}
              className="object-cover w-full h-full"
              sizes="(max-width: 640px) 100vw, (max-width: 768px) 128px, (max-width: 1024px) 160px, 192px"
              loading="eager"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <UserIcon
                size={48}
                className="sm:w-12 sm:h-12 md:w-16 md:h-16 text-muted-foreground"
              />
            </div>
          )}
        </div>

        {/* Stylist Info */}
        <div className="flex-1">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-4 gap-3">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground mb-2">
                {stylist.name}
              </h1>
              <div className="flex flex-wrap items-center gap-2">
                <Badge
                  variant={stylist.is_active ? "default" : "destructive"}
                  className="text-xs"
                >
                  {stylist.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
            </div>
          </div>

          {stylist.bio && (
            <p className="text-sm sm:text-base text-muted-foreground mb-4">
              {stylist.bio}
            </p>
          )}

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4">
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                Commission
              </p>
              <p className="text-lg sm:text-xl md:text-2xl font-bold text-foreground">
                {stylist.commission_type === "percentage"
                  ? `${stylist.commission_value}%`
                  : `₦${(stylist.commission_value || 0).toLocaleString()}`}
              </p>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                Specialties
              </p>
              <p className="text-lg sm:text-xl md:text-2xl font-bold text-foreground">
                {stylist.specialties?.length || 0}
              </p>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground mb-1">
                Services
              </p>
              <p className="text-lg sm:text-xl md:text-2xl font-bold text-foreground">
                {stylist.assigned_services?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 mt-6 pt-6 border-t border-border">
        <Button
          variant="outline"
          size="sm"
          className="text-xs cursor-pointer"
          onClick={onEdit}
        >
          <EditIcon size={14} className="sm:w-4 sm:h-4" />
          Edit
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="text-xs cursor-pointer"
          onClick={onDelete}
        >
          <TrashIcon size={14} className="sm:w-4 sm:h-4" />
          Delete
        </Button>
      </div>
    </Card>
  );
}
