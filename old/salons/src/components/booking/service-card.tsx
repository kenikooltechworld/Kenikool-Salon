import { useState } from "react";
import type { Service, PublicSalon } from "@/lib/api/types";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ClockIcon, DollarIcon } from "@/components/icons";
import { BookingFlow } from "./booking-flow";

interface ServiceCardProps {
  service: Service;
  salon: PublicSalon;
}

export function ServiceCard({ service, salon }: ServiceCardProps) {
  const [isBookingOpen, setIsBookingOpen] = useState(false);

  return (
    <>
      <Card variant="default" hover>
        {service.photo_url && (
          <div className="w-full h-48 overflow-hidden rounded-t-lg">
            <img
              src={service.photo_url}
              alt={service.name}
              className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
            />
          </div>
        )}
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>{service.name}</CardTitle>
              <Badge variant="outline" size="sm" className="mt-2">
                {service.category}
              </Badge>
            </div>
          </div>
          <CardDescription className="mt-2">
            {service.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 text-primary">
              <DollarIcon size={16} />
              <span className="font-semibold">
                ₦{service.price.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-1 text-muted-foreground">
              <ClockIcon size={16} />
              <span>{service.duration_minutes} mins</span>
            </div>
          </div>
          {service.assigned_stylists &&
            service.assigned_stylists.length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-muted-foreground mb-2">
                  {service.assigned_stylists.length} Stylist
                  {service.assigned_stylists.length > 1 ? "s" : ""} Available
                </p>
              </div>
            )}
        </CardContent>
        <CardFooter>
          <Button fullWidth onClick={() => setIsBookingOpen(true)}>
            Book Now
          </Button>
        </CardFooter>
      </Card>

      <BookingFlow
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
        preSelectedService={service}
        salon={salon}
      />
    </>
  );
}
