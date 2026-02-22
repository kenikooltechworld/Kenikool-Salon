import { Card } from "@/components/ui/card";
import type { Stylist } from "@/lib/api/types";

interface LocationsTabProps {
  stylist: Stylist;
}

export function LocationsTab({ stylist }: LocationsTabProps) {
  if (!stylist.assigned_locations || stylist.assigned_locations.length === 0) {
    return (
      <Card className="p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
          Assigned Locations
        </h2>
        <p className="text-muted-foreground">No locations assigned</p>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
        Assigned Locations
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {stylist.assigned_locations.map((locationId) => (
          <div
            key={locationId}
            className="p-3 border border-border rounded-lg bg-muted/50"
          >
            <p className="text-sm font-medium text-foreground">
              {stylist.location_names?.[locationId] || locationId}
            </p>
          </div>
        ))}
      </div>
    </Card>
  );
}
