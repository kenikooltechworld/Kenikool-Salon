/**
 * TemplateSelector Component
 * Allows user to select a template and pre-populate booking form
 * Validates: Requirements 4.2
 */
import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChevronLeftIcon, AlertCircleIcon } from "@/components/icons";
import type { BookingTemplate } from "../../lib/api/hooks/useBookingTemplates";

interface TemplateSelectorProps {
  template: BookingTemplate;
  onConfirm: (template: BookingTemplate) => void;
  onBack: () => void;
  loading?: boolean;
}

/**
 * Component for selecting a template and reviewing its details before applying
 */
export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  template,
  onConfirm,
  onBack,
  loading = false,
}) => {
  const [modifications, setModifications] = useState<Partial<BookingTemplate>>(
    {},
  );

  const handleModification = (field: string, value: any) => {
    setModifications((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const finalTemplate = {
    ...template,
    ...modifications,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button
          onClick={onBack}
          disabled={loading}
          variant="ghost"
          size="sm"
          aria-label="Go back"
        >
          <ChevronLeftIcon size={20} />
        </Button>
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            {template.name}
          </h2>
          <p className="text-sm text-muted-foreground">
            {template.description}
          </p>
        </div>
      </div>

      {/* Template Details */}
      <Card className="p-6 space-y-4">
        <h3 className="font-semibold text-foreground">Template Details</h3>

        <div className="space-y-4">
          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-foreground">
              Category
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              {template.category}
            </p>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-foreground">
              Duration
            </label>
            <div className="mt-1 flex items-center gap-2">
              <Input
                type="number"
                value={finalTemplate.duration}
                onChange={(e) =>
                  handleModification("duration", parseInt(e.target.value))
                }
                disabled={loading}
                className="w-24"
              />
              <span className="text-sm text-muted-foreground">minutes</span>
            </div>
          </div>

          {/* Pricing */}
          <div>
            <label className="block text-sm font-medium text-foreground">
              Price
            </label>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-sm text-muted-foreground">$</span>
              <Input
                type="number"
                value={finalTemplate.pricing}
                onChange={(e) =>
                  handleModification("pricing", parseFloat(e.target.value))
                }
                disabled={loading}
                step="0.01"
                className="w-32"
              />
            </div>
          </div>

          {/* Services */}
          <div>
            <label className="block text-sm font-medium text-foreground">
              Services Included
            </label>
            <div className="mt-2 space-y-2">
              {template.services && template.services.length > 0 ? (
                template.services.map((service, index) => (
                  <Card key={index} className="p-3 bg-muted">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">
                        {service.service_name}
                      </p>
                      {service.variant_id && (
                        <p className="text-xs text-muted-foreground">
                          Variant: {service.variant_id}
                        </p>
                      )}
                      {service.add_ons && service.add_ons.length > 0 && (
                        <p className="text-xs text-muted-foreground">
                          Add-ons: {service.add_ons.join(", ")}
                        </p>
                      )}
                    </div>
                  </Card>
                ))
              ) : (
                <Card className="p-3 bg-accent/10 border-accent flex items-center gap-2">
                  <AlertCircleIcon size={16} className="text-accent" />
                  <span className="text-sm text-accent-foreground">
                    No services in this template
                  </span>
                </Card>
              )}
            </div>
          </div>

          {/* Usage Count */}
          <div>
            <label className="block text-sm font-medium text-foreground">
              Times Used
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              {template.usage_count} times
            </p>
          </div>
        </div>
      </Card>

      {/* Summary */}
      <Card className="p-4 border-primary/20 bg-primary/5 space-y-2">
        <h4 className="font-semibold text-foreground">Summary</h4>
        <div className="space-y-1 text-sm text-foreground">
          <p>
            <span className="font-medium">Duration:</span>{" "}
            {finalTemplate.duration} minutes
          </p>
          <p>
            <span className="font-medium">Price:</span> $
            {finalTemplate.pricing.toFixed(2)}
          </p>
          <p>
            <span className="font-medium">Services:</span>{" "}
            {template.services?.length || 0} service(s)
          </p>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          onClick={onBack}
          disabled={loading}
          variant="outline"
          className="flex-1"
        >
          Back
        </Button>
        <Button
          onClick={() => onConfirm(finalTemplate)}
          disabled={loading}
          className="flex-1"
        >
          {loading ? "Loading..." : "Use This Template"}
        </Button>
      </div>
    </div>
  );
};

export default TemplateSelector;
