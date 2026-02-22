import React, { useState, useEffect } from "react";
import { useLocations } from "@/lib/api/hooks/useLocations";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

interface LocationFilterProps {
  selectedLocations: string[];
  onLocationsChange: (locations: string[]) => void;
  allowMultiple?: boolean;
}

export const LocationFilter: React.FC<LocationFilterProps> = ({
  selectedLocations,
  onLocationsChange,
  allowMultiple = true,
}) => {
  const { locations, loading } = useLocations();
  const [expanded, setExpanded] = useState(false);

  const handleLocationToggle = (locationId: string) => {
    if (allowMultiple) {
      const updated = selectedLocations.includes(locationId)
        ? selectedLocations.filter((id) => id !== locationId)
        : [...selectedLocations, locationId];
      onLocationsChange(updated);
    } else {
      onLocationsChange(
        selectedLocations.includes(locationId) ? [] : [locationId],
      );
    }
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading locations...</div>;
  }

  return (
    <div className="space-y-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full p-2 border rounded hover:bg-gray-50"
      >
        <span className="font-medium text-sm">
          Locations
          {selectedLocations.length > 0 && (
            <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              {selectedLocations.length} selected
            </span>
          )}
        </span>
        <span className="text-gray-500">{expanded ? "▼" : "▶"}</span>
      </button>

      {expanded && (
        <div className="space-y-2 pl-2">
          {locations.map((location) => (
            <div key={location.id} className="flex items-center space-x-2">
              <Checkbox
                id={`location-${location.id}`}
                checked={selectedLocations.includes(location.id)}
                onCheckedChange={() => handleLocationToggle(location.id)}
              />
              <Label
                htmlFor={`location-${location.id}`}
                className="text-sm cursor-pointer"
              >
                {location.name}
              </Label>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
