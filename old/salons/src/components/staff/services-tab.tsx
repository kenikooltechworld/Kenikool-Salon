import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import type { Stylist } from "@/lib/api/types";

interface ServicesTabProps {
  stylist: Stylist;
  serviceNames: Record<string, string>;
  isLoading: boolean;
}

export function ServicesTab({
  stylist,
  serviceNames,
  isLoading,
}: ServicesTabProps) {
  if (!stylist.assigned_services || stylist.assigned_services.length === 0) {
    return (
      <Card className="p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
          Assigned Services
        </h2>
        <p className="text-muted-foreground">No services assigned</p>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
        Assigned Services
      </h2>
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {stylist.assigned_services.map((serviceId: string) => (
            <div
              key={serviceId}
              className="p-3 border border-border rounded-lg"
            >
              <p className="text-sm font-medium">
                {serviceNames[serviceId] || serviceId}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
