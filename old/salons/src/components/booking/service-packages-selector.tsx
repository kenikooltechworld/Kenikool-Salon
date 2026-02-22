import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckIcon } from "@/components/icons";

interface ServicePackage {
  id: string;
  name: string;
  description: string;
  price: number;
  sessions: number;
  discount: number;
}

interface ServicePackagesSelectorProps {
  packages?: ServicePackage[];
  onSelect?: (packageId: string) => void;
}

export function ServicePackagesSelector({
  packages = [],
  onSelect,
}: ServicePackagesSelectorProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = (packageId: string) => {
    setSelectedId(packageId);
    onSelect?.(packageId);
  };

  if (packages.length === 0) {
    return (
      <Card className="p-6 text-center text-muted-foreground">
        No packages available
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Service Packages</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {packages.map((pkg) => (
          <Card
            key={pkg.id}
            className={`p-4 cursor-pointer transition-all ${
              selectedId === pkg.id
                ? "border-primary border-2 bg-primary/5"
                : "hover:border-primary/50"
            }`}
            onClick={() => handleSelect(pkg.id)}
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <h4 className="font-semibold">{pkg.name}</h4>
                {selectedId === pkg.id && (
                  <CheckIcon size={20} className="text-primary" />
                )}
              </div>

              <p className="text-sm text-muted-foreground">{pkg.description}</p>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Sessions:</span>
                  <span className="font-medium">{pkg.sessions}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Price:</span>
                  <span className="font-medium">
                    ₦{pkg.price.toLocaleString()}
                  </span>
                </div>
              </div>

              {pkg.discount > 0 && (
                <Badge variant="accent">Save {pkg.discount}%</Badge>
              )}

              <Button
                variant={selectedId === pkg.id ? "primary" : "outline"}
                className="w-full"
                onClick={() => handleSelect(pkg.id)}
              >
                {selectedId === pkg.id ? "Selected" : "Select"}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
