import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPinIcon, DollarIcon } from "@/components/icons";
import { useLocations } from "@/lib/api/hooks/useLocations";

interface ServiceLocationsSectionProps {
  availableAtLocations?: string[];
  locationPricing?: Array<{
    location_id: string;
    price: number;
    duration_minutes?: number;
  }>;
}

export function ServiceLocationsSection({
  availableAtLocations = [],
  locationPricing = [],
}: ServiceLocationsSectionProps) {
  const { data: locationsData = [] } = useLocations();
  const locations = Array.isArray(locationsData) ? locationsData : [];

  // Get location details for assigned locations
  const assignedLocations = locations.filter((loc) =>
    availableAtLocations.includes(loc._id),
  );

  if (availableAtLocations.length === 0) {
    return (
      <Card className="p-4 sm:p-6">
        <div className="flex items-center gap-3 mb-4">
          <MapPinIcon size={20} className="text-muted-foreground" />
          <h2 className="text-lg sm:text-xl font-bold text-foreground">
            Service Locations
          </h2>
        </div>
        <p className="text-sm text-muted-foreground">
          This service is not assigned to any locations yet. Edit the service to
          add locations.
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <div className="flex items-center gap-3 mb-4">
        <MapPinIcon size={20} className="text-primary" />
        <h2 className="text-lg sm:text-xl font-bold text-foreground">
          Service Locations
        </h2>
      </div>

      <div className="space-y-3">
        {assignedLocations.map((location) => {
          const pricing = locationPricing.find(
            (p) => p.location_id === location._id,
          );

          return (
            <div
              key={location._id}
              className="flex items-start justify-between p-3 bg-muted/50 rounded-lg border border-border"
            >
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-sm sm:text-base text-foreground mb-1">
                  {location.name}
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  {location.address}
                </p>
                {location.city && location.state && (
                  <p className="text-xs text-muted-foreground">
                    {location.city}, {location.state}
                  </p>
                )}
              </div>

              <div className="flex flex-col items-end gap-2 ml-3 flex-shrink-0">
                {pricing && (
                  <>
                    <div className="flex items-center gap-1">
                      <DollarIcon size={14} className="text-primary" />
                      <span className="text-sm sm:text-base font-semibold text-foreground">
                        ₦{pricing.price.toLocaleString()}
                      </span>
                    </div>
                    {pricing.duration_minutes && (
                      <Badge variant="secondary" className="text-xs">
                        {pricing.duration_minutes}m
                      </Badge>
                    )}
                  </>
                )}
                {!pricing && (
                  <Badge variant="outline" className="text-xs">
                    Default pricing
                  </Badge>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-muted-foreground mt-4">
        {assignedLocations.length} location
        {assignedLocations.length !== 1 ? "s" : ""} available
      </p>
    </Card>
  );
}
