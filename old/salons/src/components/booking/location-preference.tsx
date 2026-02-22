import React, { useEffect, useState } from "react";
import { useLocations } from "@/lib/api/hooks/useLocations";
import { Button } from "@/components/ui/button";

interface LocationPreferenceProps {
  onPreferenceSet: (locationId: string) => void;
  currentPreference?: string;
}

export const LocationPreference: React.FC<LocationPreferenceProps> = ({
  onPreferenceSet,
  currentPreference,
}) => {
  const { locations, loading } = useLocations();
  const [preference, setPreference] = useState<string | undefined>(
    currentPreference,
  );

  useEffect(() => {
    // Load preference from localStorage on mount
    const stored = localStorage.getItem("preferred_location");
    if (stored) {
      setPreference(stored);
    }
  }, []);

  const handleSetPreference = (locationId: string) => {
    setPreference(locationId);
    localStorage.setItem("preferred_location", locationId);
    onPreferenceSet(locationId);
  };

  const handleClearPreference = () => {
    setPreference(undefined);
    localStorage.removeItem("preferred_location");
    onPreferenceSet("");
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading locations...</div>;
  }

  return (
    <div className="space-y-3 p-3 border rounded bg-blue-50">
      <div className="text-sm font-medium">Preferred Location</div>

      {preference ? (
        <div className="space-y-2">
          <div className="text-sm">
            Current preference:{" "}
            <span className="font-medium">
              {locations.find((l) => l.id === preference)?.name}
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearPreference}
            className="w-full"
          >
            Clear Preference
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="text-xs text-gray-600">
            Select a location to remember for future bookings
          </div>
          <div className="grid grid-cols-2 gap-2">
            {locations.map((location) => (
              <Button
                key={location.id}
                variant="outline"
                size="sm"
                onClick={() => handleSetPreference(location.id)}
                className="text-xs"
              >
                {location.name}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
