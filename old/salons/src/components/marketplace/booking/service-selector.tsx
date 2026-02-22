import React from "react";
import { motion } from "framer-motion";
import {
  useSalonServices,
  useSalonStylists,
} from "@/lib/api/hooks/useMarketplaceQueries";
import { Spinner } from "@/components/ui/spinner";

interface Service {
  id: string;
  name: string;
  description?: string;
  price: number;
  duration: number;
  category?: string;
}

interface Stylist {
  id: string;
  name: string;
  specialty?: string;
  image?: string;
}

interface ServiceSelectorProps {
  salonId: string;
  onSelect: (service: Service & { stylist?: Stylist }) => void;
}

export function ServiceSelector({ salonId, onSelect }: ServiceSelectorProps) {
  const [selectedService, setSelectedService] = React.useState<Service | null>(
    null,
  );
  const [selectedStylist, setSelectedStylist] = React.useState<Stylist | null>(
    null,
  );

  const { data: services = [], isLoading: servicesLoading } =
    useSalonServices(salonId);
  const { data: stylists = [], isLoading: stylistsLoading } =
    useSalonStylists(salonId);

  const isLoading = servicesLoading || stylistsLoading;

  const handleServiceSelect = (service: Service) => {
    setSelectedService(service);
    onSelect({
      ...service,
      stylist: selectedStylist || undefined,
    });
  };

  const handleStylistSelect = (stylist: Stylist) => {
    setSelectedStylist(stylist);
    if (selectedService) {
      onSelect({
        ...selectedService,
        stylist,
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (services.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">No services available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Select a Service</h3>
        <div className="space-y-3">
          {services.map((service, index) => (
            <motion.button
              key={service.id}
              onClick={() => handleServiceSelect(service)}
              className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                selectedService?.id === service.id
                  ? "border-[var(--primary)] bg-[var(--primary)]/5"
                  : "border-[var(--border)] hover:border-[var(--primary)]"
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-[var(--foreground)]">
                    {service.name}
                  </h4>
                  {service.description && (
                    <p className="text-sm text-[var(--muted-foreground)] mt-1">
                      {service.description}
                    </p>
                  )}
                  <p className="text-xs text-[var(--muted-foreground)] mt-2">
                    Duration: {service.duration} mins
                  </p>
                </div>
                <div className="text-right ml-4">
                  <p className="font-bold text-[var(--primary)]">
                    ₦{service.price.toLocaleString()}
                  </p>
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {selectedService && stylists.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="text-lg font-semibold mb-4">
            Select a Stylist (Optional)
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {stylists.map((stylist, index) => (
              <motion.button
                key={stylist.id}
                onClick={() => handleStylistSelect(stylist)}
                className={`p-4 rounded-lg border-2 transition-all text-center ${
                  selectedStylist?.id === stylist.id
                    ? "border-[var(--primary)] bg-[var(--primary)]/5"
                    : "border-[var(--border)] hover:border-[var(--primary)]"
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 + index * 0.05 }}
              >
                {stylist.image && (
                  <img
                    src={stylist.image}
                    alt={stylist.name}
                    className="w-12 h-12 rounded-full mx-auto mb-2 object-cover"
                  />
                )}
                <p className="font-semibold text-sm text-[var(--foreground)]">
                  {stylist.name}
                </p>
                {stylist.specialty && (
                  <p className="text-xs text-[var(--muted-foreground)] mt-1">
                    {stylist.specialty}
                  </p>
                )}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-[var(--muted)] p-4 rounded-lg"
      >
        <p className="text-sm text-[var(--muted-foreground)]">
          <span className="font-semibold">Selected:</span>{" "}
          {selectedService ? (
            <>
              {selectedService.name} - ₦{selectedService.price.toLocaleString()}
              {selectedStylist && ` with ${selectedStylist.name}`}
            </>
          ) : (
            "No service selected"
          )}
        </p>
      </motion.div>
    </div>
  );
}
