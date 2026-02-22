import { useState } from "react";
import { CheckIcon, XIcon } from "@/components/icons";

interface AmenitiesSelectorProps {
  selectedAmenities: string[];
  onAmenitiesChange: (amenities: string[]) => void;
  allowCustom?: boolean;
}

const PREDEFINED_AMENITIES = [
  { id: "parking", label: "Parking" },
  { id: "wifi", label: "WiFi" },
  { id: "wheelchair_access", label: "Wheelchair Access" },
  { id: "air_conditioning", label: "Air Conditioning" },
  { id: "waiting_area", label: "Waiting Area" },
  { id: "refreshments", label: "Refreshments" },
  { id: "restroom", label: "Restroom" },
  { id: "valet_parking", label: "Valet Parking" },
];

export function AmenitiesSelector({
  selectedAmenities,
  onAmenitiesChange,
  allowCustom = false,
}: AmenitiesSelectorProps) {
  const [customAmenity, setCustomAmenity] = useState("");

  const toggleAmenity = (amenityId: string) => {
    if (selectedAmenities.includes(amenityId)) {
      onAmenitiesChange(selectedAmenities.filter((a) => a !== amenityId));
    } else {
      onAmenitiesChange([...selectedAmenities, amenityId]);
    }
  };

  const addCustomAmenity = () => {
    if (customAmenity.trim() && !selectedAmenities.includes(customAmenity)) {
      onAmenitiesChange([...selectedAmenities, customAmenity.trim()]);
      setCustomAmenity("");
    }
  };

  const removeAmenity = (amenityId: string) => {
    onAmenitiesChange(selectedAmenities.filter((a) => a !== amenityId));
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-2">
        {PREDEFINED_AMENITIES.map((amenity) => (
          <button
            key={amenity.id}
            onClick={() => toggleAmenity(amenity.id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-md border transition-colors ${
              selectedAmenities.includes(amenity.id)
                ? "bg-primary/10 border-primary text-primary"
                : "bg-background border-border text-foreground hover:border-primary/50"
            }`}
          >
            <div
              className={`w-4 h-4 rounded border flex items-center justify-center ${
                selectedAmenities.includes(amenity.id)
                  ? "bg-primary border-primary"
                  : "border-border"
              }`}
            >
              {selectedAmenities.includes(amenity.id) && (
                <CheckIcon size={12} className="text-primary-foreground" />
              )}
            </div>
            <span className="text-sm font-medium">{amenity.label}</span>
          </button>
        ))}
      </div>

      {allowCustom && (
        <div className="space-y-2 pt-4 border-t border-border">
          <div className="flex gap-2">
            <input
              type="text"
              value={customAmenity}
              onChange={(e) => setCustomAmenity(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && addCustomAmenity()}
              placeholder="Add custom amenity..."
              className="flex-1 px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <button
              onClick={addCustomAmenity}
              className="px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors text-sm font-medium"
            >
              Add
            </button>
          </div>

          {selectedAmenities.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {selectedAmenities.map((amenity) => (
                <div
                  key={amenity}
                  className="flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded-full text-xs"
                >
                  <span>{amenity}</span>
                  <button
                    onClick={() => removeAmenity(amenity)}
                    className="hover:text-primary/70 transition-colors"
                  >
                    <XIcon size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
