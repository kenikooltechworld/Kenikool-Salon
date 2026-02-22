import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useMultiLocation } from "@/lib/api/hooks/useMultiLocation";

interface LocationAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  staffId: string;
  staffName: string;
  availableLocations: Array<{ id: string; name: string; address?: string }>;
  onUpdate?: () => Promise<void>;
}

const XIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);

const CheckIcon = () => (
  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
  </svg>
);

const MapPinIcon = () => (
  <svg
    className="w-4 h-4"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
    />
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
    />
  </svg>
);

export const LocationAssignmentModal: React.FC<
  LocationAssignmentModalProps
> = ({ isOpen, onClose, staffId, staffName, availableLocations, onUpdate }) => {
  const { locations, loading, assignLocations, fetchLocations } =
    useMultiLocation(staffId);
  const [selectedLocationIds, setSelectedLocationIds] = useState<Set<string>>(
    new Set(),
  );
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Fetch the current locations when modal opens
      fetchLocations();
    }
  }, [isOpen, staffId, fetchLocations]);

  useEffect(() => {
    if (locations.length > 0) {
      // Update selected locations when they're loaded
      setSelectedLocationIds(new Set(locations.map((loc) => loc.id)));
    }
  }, [locations]);

  const handleToggleLocation = (locationId: string) => {
    const newSelected = new Set(selectedLocationIds);
    if (newSelected.has(locationId)) {
      newSelected.delete(locationId);
    } else {
      newSelected.add(locationId);
    }
    setSelectedLocationIds(newSelected);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const success = await assignLocations(Array.from(selectedLocationIds));
      if (success) {
        if (onUpdate) await onUpdate();
        onClose();
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle className="flex items-center gap-2">
            <MapPinIcon />
            Location Assignment - {staffName}
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <XIcon />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <p className="text-center text-slate-500">Loading locations...</p>
          ) : availableLocations.length === 0 ? (
            <p className="text-center text-slate-500">No locations available</p>
          ) : (
            <div className="space-y-2">
              {availableLocations.map((location) => (
                <div
                  key={location.id}
                  className="flex items-center gap-3 p-3 border rounded-lg hover:bg-slate-50 cursor-pointer"
                  onClick={() => handleToggleLocation(location.id)}
                >
                  <div
                    className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                      selectedLocationIds.has(location.id)
                        ? "bg-blue-500 border-blue-500"
                        : "border-slate-300"
                    }`}
                  >
                    {selectedLocationIds.has(location.id) && <CheckIcon />}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{location.name}</p>
                    {location.address && (
                      <p className="text-xs text-slate-600">
                        {location.address}
                      </p>
                    )}
                  </div>
                  {selectedLocationIds.has(location.id) && (
                    <Badge className="text-xs">Selected</Badge>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>

        <div className="border-t p-4 flex gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
            disabled={isSaving}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="flex-1"
            disabled={isSaving || selectedLocationIds.size === 0}
          >
            {isSaving ? "Saving..." : "Save Locations"}
          </Button>
        </div>
      </Card>
    </div>
  );
};
