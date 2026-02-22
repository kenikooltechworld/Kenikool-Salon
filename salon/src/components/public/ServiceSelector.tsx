/**
 * Service Selector Component - Display published services for public booking
 */

import { useState } from "react";
import { Card, Button, Spinner, Badge } from "@/components/ui";
import { usePublicServices } from "@/hooks/usePublicBooking";
import { formatCurrency } from "@/lib/utils/format";
import { CheckIcon } from "@/components/icons";

interface ServiceSelectorProps {
  onSelect: (serviceId: string, durationMinutes: number) => void;
}

export default function ServiceSelector({ onSelect }: ServiceSelectorProps) {
  const [selectedServiceId, setSelectedServiceId] = useState<string | null>(
    null,
  );

  const { data: services, isLoading, error } = usePublicServices();

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">
          Failed to load services. Please try again.
        </p>
      </div>
    );
  }

  if (!services || services.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">
          No services available at this time.
        </p>
      </div>
    );
  }

  const handleSelect = (serviceId: string, durationMinutes: number) => {
    setSelectedServiceId(serviceId);
    onSelect(serviceId, durationMinutes);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Select a Service</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Choose the service you want to book
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {services.map((service) => (
          <Card
            key={service.id}
            className={`p-4 cursor-pointer transition-all ${
              selectedServiceId === service.id
                ? "ring-2 ring-primary bg-primary/5"
                : "hover:shadow-lg"
            }`}
            onClick={() => handleSelect(service.id, service.duration_minutes)}
          >
            {service.public_image_url && (
              <img
                src={service.public_image_url}
                alt={service.name}
                className="w-full h-40 object-cover rounded-lg mb-4"
              />
            )}

            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">{service.name}</h3>
                <p className="text-muted-foreground text-sm mt-1">
                  {service.public_description || service.description}
                </p>
              </div>
              {selectedServiceId === service.id && (
                <CheckIcon size={20} className="text-primary flex-shrink-0" />
              )}
            </div>

            <div className="flex justify-between items-center mt-4 pt-4 border-t">
              <Badge variant="secondary">{service.duration_minutes} min</Badge>
              <span className="text-lg font-bold text-primary">
                {formatCurrency(service.price, "NGN")}
              </span>
            </div>

            <Button
              variant={selectedServiceId === service.id ? "primary" : "outline"}
              className="w-full mt-4"
              onClick={() => handleSelect(service.id, service.duration_minutes)}
            >
              {selectedServiceId === service.id ? "✓ Selected" : "Select"}
            </Button>
          </Card>
        ))}
      </div>

      {selectedServiceId && (
        <div className="flex justify-end">
          <Button variant="primary">Continue →</Button>
        </div>
      )}
    </div>
  );
}
