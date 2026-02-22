import { useState } from "react";
import { usePOSStore } from "@/stores/pos";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { Skeleton } from "@/components/ui/skeleton";

interface Service {
  id: string;
  name: string;
  price: number;
  description?: string;
  image?: string;
}

interface ItemSelectorProps {
  services: Service[];
  isLoading?: boolean;
}

export default function ItemSelector({
  services,
  isLoading = false,
}: ItemSelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const { addToCart } = usePOSStore();
  const { showToast } = useToast();

  const filteredServices = services.filter((s) =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  const handleAddToCart = (service: Service) => {
    const quantity = quantities[service.id] || 1;
    addToCart({
      itemType: "service",
      itemId: service.id,
      itemName: service.name,
      quantity,
      unitPrice: service.price,
      lineTotal: quantity * service.price,
    });
    setQuantities({ ...quantities, [service.id]: 1 });
    showToast({
      title: "Added to Cart",
      description: `${service.name} (qty: ${quantity}) added to cart`,
      variant: "success",
    });
  };

  return (
    <div className="space-y-4">
      <Input
        placeholder="Search services..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        disabled={isLoading}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 md:gap-3 max-h-96 overflow-y-auto">
        {isLoading ? (
          // Skeleton loading
          <>
            {[...Array(6)].map((_, idx) => (
              <Card key={idx} className="p-3">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-3 w-16" />
                  <div className="flex gap-2">
                    <Skeleton className="h-8 w-12" />
                    <Skeleton className="h-8 flex-1" />
                  </div>
                </div>
              </Card>
            ))}
          </>
        ) : filteredServices.length === 0 ? (
          <div className="col-span-full text-center py-8">
            <p className="text-muted-foreground">
              {searchTerm ? "No services found" : "No services available"}
            </p>
          </div>
        ) : (
          filteredServices.map((service) => (
            <Card key={service.id} className="p-3 hover:shadow-md transition">
              <div className="space-y-2">
                <div>
                  <p className="font-medium text-sm text-foreground">
                    {service.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    ₦
                    {service.price.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min="1"
                    value={quantities[service.id] || 1}
                    onChange={(e) =>
                      setQuantities({
                        ...quantities,
                        [service.id]: parseInt(e.target.value) || 1,
                      })
                    }
                    className="w-12 h-8 text-center text-sm"
                  />
                  <Button
                    size="sm"
                    onClick={() => handleAddToCart(service)}
                    className="flex-1"
                  >
                    Add
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
