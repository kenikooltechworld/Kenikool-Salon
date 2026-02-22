import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useServices } from "@/hooks/useServices";
import type { Service } from "@/types/service";
import { SearchIcon, CheckIcon, InfoIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/format";
import { ServiceDetailModal } from "./ServiceDetailModal";

interface ServiceSelectorProps {
  services?: any[];
  selectedServiceId?: string;
  onServiceSelect: (service: Service) => void;
  onNext?: () => void;
}

export function ServiceSelector({
  services: providedServices,
  selectedServiceId,
  onServiceSelect,
  onNext,
}: ServiceSelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedDetailService, setSelectedDetailService] =
    useState<Service | null>(null);
  const { data: fetchedServices = [], isLoading } = useServices({
    is_active: true,
  });

  const services = providedServices || fetchedServices;

  const filteredServices = services.filter(
    (service: Service) =>
      service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      service.category.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const selectedService = services.find(
    (s: Service) => s.id === selectedServiceId,
  );
  const isLoadingServices = !providedServices && isLoading;

  const handleViewDetails = (service: Service) => {
    setSelectedDetailService(service);
    setDetailModalOpen(true);
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-foreground mb-2">
          Select a Service
        </h3>
        <p className="text-sm text-muted-foreground">
          Choose the service you want to book
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <SearchIcon
          size={18}
          className="absolute left-3 top-3 text-muted-foreground"
        />
        <Input
          placeholder="Search services..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Services Grid */}
      {isLoadingServices ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="overflow-hidden">
              <Skeleton className="h-40 w-full" />
              <div className="p-4 space-y-3">
                <div className="space-y-2">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-8 w-full" />
                <div className="flex gap-2 pt-2">
                  <Skeleton className="h-9 flex-1" />
                  <Skeleton className="h-9 flex-1" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : filteredServices.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredServices.map((service: Service) => (
            <Card
              key={service.id}
              className={`overflow-hidden cursor-pointer transition ${
                selectedServiceId === service.id
                  ? "border-primary bg-primary/5"
                  : "hover:border-primary/50"
              }`}
            >
              {/* Service Image */}
              {service.public_image_url && (
                <div className="relative h-40 overflow-hidden bg-muted">
                  <img
                    src={service.public_image_url}
                    alt={service.name}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Service Details */}
              <div className="p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-foreground">
                      {service.name}
                    </h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      {service.category}
                    </p>
                  </div>
                  {selectedServiceId === service.id && (
                    <CheckIcon
                      size={20}
                      className="text-primary flex-shrink-0 ml-2"
                    />
                  )}
                </div>

                <p className="text-sm text-muted-foreground line-clamp-2">
                  {service.description}
                </p>

                <div className="flex items-center justify-between pt-2 border-t border-border">
                  <div>
                    <p className="text-xs text-muted-foreground">Duration</p>
                    <p className="text-sm font-medium text-foreground">
                      {service.duration_minutes} min
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">Price</p>
                    <p className="text-sm font-medium text-foreground">
                      {formatCurrency(service.price, "NGN")}
                    </p>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleViewDetails(service)}
                    className="flex-1 gap-2 cursor-pointer"
                  >
                    <InfoIcon size={16} />
                    <span>Details</span>
                  </Button>
                  <Button
                    variant={
                      selectedServiceId === service.id ? "primary" : "outline"
                    }
                    size="sm"
                    onClick={() => onServiceSelect(service)}
                    className="flex-1 cursor-pointer"
                  >
                    {selectedServiceId === service.id ? "Selected" : "Select"}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          No services found
        </div>
      )}

      {/* Selected Service Summary */}
      {selectedService && (
        <Card className="p-4 bg-muted/50 border-primary/50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Selected Service</p>
              <p className="font-semibold text-foreground">
                {selectedService.name}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Duration</p>
              <p className="font-semibold text-foreground">
                {selectedService.duration_minutes} min
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Next Button */}
      {onNext && (
        <Button
          onClick={onNext}
          disabled={!selectedServiceId}
          className="w-full"
        >
          Continue to Staff Selection
        </Button>
      )}

      {/* Service Detail Modal */}
      {selectedDetailService && (
        <ServiceDetailModal
          isOpen={detailModalOpen}
          service={selectedDetailService}
          onClose={() => {
            setDetailModalOpen(false);
            setSelectedDetailService(null);
          }}
          onSelect={() => {
            onServiceSelect(selectedDetailService);
            setDetailModalOpen(false);
            setSelectedDetailService(null);
          }}
        />
      )}
    </div>
  );
}
