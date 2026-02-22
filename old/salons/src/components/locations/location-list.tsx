import { useState } from "react";
import { Location } from "@/lib/api/hooks/useLocations";
import {
  MapPinIcon,
  PhoneIcon,
  MailIcon,
  EditIcon,
  TrashIcon,
  CheckCircleIcon,
  MenuIcon,
  EyeIcon,
  UsersIcon,
  PackageIcon,
  WifiIcon,
  SettingsIcon,
} from "@/components/icons";
import { LocationStatusBadge } from "./LocationStatusBadge";
import { LocationMapPreview } from "./LocationMapPreview";

interface LocationListProps {
  locations: Location[];
  onEdit: (location: Location) => void;
  onDelete: (id: string) => void;
  onViewDetails?: (location: Location) => void;
  staffCounts?: Record<string, number>;
  serviceCounts?: Record<string, number>;
  deletingId?: string | null;
}

// Amenity icon mapping
const AMENITY_ICONS: Record<string, any> = {
  parking: MapPinIcon,
  shopping: PackageIcon,
  wifi: WifiIcon,
  wheelchair_access: SettingsIcon,
  air_conditioning: SettingsIcon,
  waiting_area: SettingsIcon,
  refreshments: SettingsIcon,
};

const AMENITY_LABELS: Record<string, string> = {
  parking: "Parking",
  wifi: "WiFi",
  wheelchair_access: "Wheelchair Access",
  air_conditioning: "Air Conditioning",
  waiting_area: "Waiting Area",
  refreshments: "Refreshments",
};

export function LocationList({
  locations,
  onEdit,
  onDelete,
  onViewDetails,
  staffCounts = {},
  serviceCounts = {},
  deletingId = null,
}: LocationListProps) {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  if (locations.length === 0) {
    return (
      <div className="text-center py-12">
        <MapPinIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No locations yet</h3>
        <p className="text-muted-foreground">
          Add your first location to get started
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {locations.map((location) => (
        <div
          key={location._id}
          className="bg-card border border-border rounded-[var(--radius-lg)] overflow-hidden hover:shadow-lg transition-shadow flex flex-col"
        >
          {/* Map Preview */}
          {location.latitude && location.longitude && (
            <div className="h-40 bg-muted relative group cursor-pointer">
              <LocationMapPreview
                latitude={location.latitude}
                longitude={location.longitude}
                title={location.name}
                height="100%"
                width="100%"
                zoom={14}
                interactive={false}
              />
              {onViewDetails && (
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <button
                    onClick={() => onViewDetails(location)}
                    className="bg-primary text-primary-foreground px-3 py-1.5 rounded-md text-sm font-medium flex items-center gap-1 cursor-pointer"
                  >
                    <EyeIcon size={14} />
                    View Details
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="p-4 flex-1 flex flex-col">
            {/* Header with Status */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-base">{location.name}</h3>
                  {location.is_primary && (
                    <span className="flex items-center gap-1 text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded-full">
                      <CheckCircleIcon size={10} />
                      Primary
                    </span>
                  )}
                </div>
                <LocationStatusBadge
                  status={location.status || "active"}
                  reopeningDate={location.reopening_date}
                  className="text-xs"
                />
              </div>

              {/* Quick Actions Menu */}
              <div className="relative">
                <button
                  onClick={() =>
                    setOpenMenuId(
                      openMenuId === location._id ? null : location._id,
                    )
                  }
                  className="p-1 hover:bg-muted rounded-md transition-colors cursor-pointer"
                >
                  <MenuIcon size={16} />
                </button>

                {openMenuId === location._id && (
                  <div className="absolute right-0 top-full mt-1 bg-card border border-border rounded-md shadow-lg z-10 min-w-[150px]">
                    {onViewDetails && (
                      <button
                        onClick={() => {
                          onViewDetails(location);
                          setOpenMenuId(null);
                        }}
                        className="w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors flex items-center gap-2 cursor-pointer"
                      >
                        <EyeIcon size={14} />
                        View Details
                      </button>
                    )}
                    <button
                      onClick={() => {
                        onEdit(location);
                        setOpenMenuId(null);
                      }}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors flex items-center gap-2 cursor-pointer"
                    >
                      <EditIcon size={14} />
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        onDelete(location._id);
                        setOpenMenuId(null);
                      }}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-destructive/10 text-destructive transition-colors flex items-center gap-2 cursor-pointer"
                    >
                      <TrashIcon size={14} />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Address */}
            <div className="flex items-start gap-2 text-sm mb-3">
              <MapPinIcon
                size={14}
                className="text-muted-foreground mt-0.5 flex-shrink-0"
              />
              <div className="text-xs">
                <p className="text-foreground">{location.address}</p>
                <p className="text-muted-foreground">
                  {location.city}, {location.state} {location.postal_code}
                </p>
              </div>
            </div>

            {/* Contact Info */}
            <div className="space-y-1 mb-3 text-xs">
              <div className="flex items-center gap-2">
                <PhoneIcon size={12} className="text-muted-foreground" />
                <span className="text-foreground">{location.phone}</span>
              </div>
              {location.email && (
                <div className="flex items-center gap-2">
                  <MailIcon size={12} className="text-muted-foreground" />
                  <span className="text-foreground truncate">
                    {location.email}
                  </span>
                </div>
              )}
            </div>

            {/* Amenities Icons */}
            {location.amenities && location.amenities.length > 0 && (
              <div className="mb-3 pb-3 border-b border-border">
                <p className="text-xs font-semibold text-muted-foreground mb-2">
                  Amenities
                </p>
                <div className="flex flex-wrap gap-2">
                  {location.amenities.slice(0, 4).map((amenity) => {
                    const Icon = AMENITY_ICONS[amenity];
                    return Icon ? (
                      <div
                        key={amenity}
                        className="flex items-center gap-1 px-2 py-1 bg-muted rounded text-xs"
                        title={AMENITY_LABELS[amenity] || amenity}
                      >
                        <Icon size={12} />
                        <span className="hidden sm:inline">
                          {AMENITY_LABELS[amenity] || amenity}
                        </span>
                      </div>
                    ) : null;
                  })}
                  {location.amenities.length > 4 && (
                    <div className="text-xs text-muted-foreground px-2 py-1">
                      +{location.amenities.length - 4} more
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Staff and Service Counts */}
            <div className="flex gap-3 mb-3 pb-3 border-b border-border">
              <div className="flex items-center gap-1 text-xs">
                <UsersIcon size={14} className="text-muted-foreground" />
                <span className="font-medium">
                  {staffCounts[location._id] || 0}
                </span>
                <span className="text-muted-foreground">Staff</span>
              </div>
              <div className="flex items-center gap-1 text-xs">
                <PackageIcon size={14} className="text-muted-foreground" />
                <span className="font-medium">
                  {serviceCounts[location._id] || 0}
                </span>
                <span className="text-muted-foreground">Services</span>
              </div>
            </div>

            {/* Business Hours Preview */}
            {location.business_hours && (
              <div className="mb-3 text-xs">
                <p className="font-semibold text-muted-foreground mb-1">
                  Hours
                </p>
                <div className="space-y-0.5">
                  {Object.entries(location.business_hours)
                    .slice(0, 2)
                    .map(([day, hours]: any) => (
                      <div key={day} className="flex justify-between">
                        <span className="text-muted-foreground capitalize">
                          {day.slice(0, 3)}
                        </span>
                        <span className="text-foreground">
                          {hours.closed
                            ? "Closed"
                            : `${hours.open} - ${hours.close}`}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2 pt-3 border-t border-border mt-auto">
              <button
                onClick={() => onEdit(location)}
                disabled={deletingId === location._id}
                className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <EditIcon size={14} />
                <span className="hidden sm:inline">Edit</span>
              </button>
              <button
                onClick={() => onDelete(location._id)}
                disabled={deletingId === location._id}
                className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-destructive/10 text-destructive rounded-[var(--radius-md)] hover:bg-destructive/20 transition-colors text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {deletingId === location._id ? (
                  <>
                    <div className="w-3 h-3 border-2 border-destructive border-t-transparent rounded-full animate-spin" />
                    <span className="hidden sm:inline">Deleting...</span>
                  </>
                ) : (
                  <>
                    <TrashIcon size={14} />
                    <span className="hidden sm:inline">Delete</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
