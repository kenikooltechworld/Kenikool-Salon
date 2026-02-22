import { Button } from "@/components/ui/button";
import { EditIcon, TrashIcon } from "@/components/icons";
import type { Service } from "@/types/service";

interface ServiceCardProps {
  service: Service;
  onEdit?: (service: Service) => void;
  onDelete?: (id: string) => void;
}

export function ServiceCard({ service, onEdit, onDelete }: ServiceCardProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-4 space-y-3 hover:shadow-md transition">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-foreground">{service.name}</h3>
          <p className="text-xs text-muted-foreground mt-1">
            {service.category}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit?.(service)}
            className="p-2"
          >
            <EditIcon size={16} className="text-muted-foreground" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete?.(service.id)}
            className="p-2"
          >
            <TrashIcon size={16} className="text-destructive" />
          </Button>
        </div>
      </div>

      <p className="text-sm text-muted-foreground">{service.description}</p>

      <div className="flex items-center justify-between pt-2 border-t border-border">
        <div>
          <p className="text-xs text-muted-foreground">Duration</p>
          <p className="text-sm font-medium text-foreground">
            {service.duration_minutes || 0} min
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Price</p>
          <p className="text-sm font-medium text-foreground">
            ₦
            {typeof service.price === "number"
              ? service.price.toLocaleString()
              : parseFloat(String(service.price)).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}
