import { useState, useEffect } from "react";
import {
  Location,
  LocationCreate,
  useCreateLocation,
  useUpdateLocation,
} from "@/lib/api/hooks/useLocations";
import { XIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { AddressAutocomplete } from "./AddressAutocomplete";
import { MapboxGLMap } from "./MapboxGLMap";
import { LocationImageUpload } from "./LocationImageUpload";
import { AmenitiesSelector } from "./AmenitiesSelector";

interface LocationFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  location?: Location | null;
}

const DAYS_OF_WEEK = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

const LOCATION_STATUSES = [
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "temporarily_closed", label: "Temporarily Closed" },
];

const TIMEZONES = [
  "UTC",
  "Africa/Lagos",
  "Africa/Johannesburg",
  "Africa/Cairo",
  "Africa/Nairobi",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Paris",
  "Asia/Dubai",
  "Asia/Singapore",
  "Australia/Sydney",
];

export function LocationFormModal({
  isOpen,
  onClose,
  location,
}: LocationFormModalProps) {
  const createMutation = useCreateLocation();
  const updateMutation = useUpdateLocation();

  const [formData, setFormData] = useState<LocationCreate>({
    name: "",
    address: "",
    city: "",
    state: "",
    country: "",
    postal_code: "",
    phone: "",
    email: "",
    timezone: "UTC",
    status: "active",
    is_primary: false,
    amenities: [],
    capacity: 1,
    manager_id: null,
    latitude: undefined,
    longitude: undefined,
    formatted_address: "",
    business_hours: DAYS_OF_WEEK.reduce(
      (acc, day) => ({
        ...acc,
        [day]: { open: "09:00", close: "18:00", closed: false },
      }),
      {},
    ),
  });

  const [images, setImages] = useState<any[]>([]);

  useEffect(() => {
    if (location) {
      setFormData({
        name: location.name,
        address: location.address,
        city: location.city,
        state: location.state,
        country: location.country,
        postal_code: location.postal_code,
        phone: location.phone,
        email: location.email || "",
        timezone: location.timezone || "UTC",
        status: location.status || "active",
        is_primary: location.is_primary || false,
        amenities: location.amenities || [],
        capacity: location.capacity || 1,
        manager_id: location.manager_id || null,
        latitude: location.latitude,
        longitude: location.longitude,
        formatted_address: location.formatted_address || "",
        business_hours:
          location.business_hours ||
          DAYS_OF_WEEK.reduce(
            (acc, day) => ({
              ...acc,
              [day]: { open: "09:00", close: "18:00", closed: false },
            }),
            {},
          ),
      });
      setImages(location.images || []);
    } else {
      setFormData({
        name: "",
        address: "",
        city: "",
        state: "",
        country: "",
        postal_code: "",
        phone: "",
        email: "",
        timezone: "UTC",
        status: "active",
        is_primary: false,
        amenities: [],
        capacity: 1,
        manager_id: null,
        latitude: undefined,
        longitude: undefined,
        formatted_address: "",
        business_hours: DAYS_OF_WEEK.reduce(
          (acc, day) => ({
            ...acc,
            [day]: { open: "09:00", close: "18:00", closed: false },
          }),
          {},
        ),
      });
      setImages([]);
    }
  }, [location, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      let submitData = {
        ...formData,
        images: images,
      };

      // If address is provided but coordinates are missing, geocode the address
      if (
        submitData.address &&
        (!submitData.latitude || !submitData.longitude)
      ) {
        try {
          const response = await fetch("/api/locations/geocode", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              address: submitData.address,
              country: submitData.country,
            }),
          });

          if (response.ok) {
            const geocodeResult = await response.json();
            submitData = {
              ...submitData,
              latitude: geocodeResult.latitude,
              longitude: geocodeResult.longitude,
              formatted_address:
                geocodeResult.formatted_address || submitData.address,
            };
            showToast("Address geocoded successfully", "success");
          } else {
            // If geocoding fails, still allow save but warn user
            showToast(
              "Could not geocode address - location will not appear on map",
              "warning",
            );
          }
        } catch (geocodeError) {
          console.error("Geocoding error:", geocodeError);
          showToast(
            "Could not geocode address - location will not appear on map",
            "warning",
          );
        }
      }

      if (location) {
        await updateMutation.mutateAsync({
          id: location._id,
          data: submitData,
        });
        showToast("Location updated successfully", "success");
      } else {
        await createMutation.mutateAsync(submitData);
        showToast("Location created successfully", "success");
      }
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to save location",
        "error",
      );
    }
  };

  const handleHoursChange = (
    day: string,
    field: "open" | "close" | "closed",
    value: string | boolean,
  ) => {
    setFormData((prev) => ({
      ...prev,
      business_hours: {
        ...prev.business_hours,
        [day]: {
          ...prev.business_hours![day],
          [field]: value,
        },
      },
    }));
  };

  const handleLocationSelect = (locationData: any) => {
    setFormData((prev) => ({
      ...prev,
      latitude: locationData.latitude,
      longitude: locationData.longitude,
      formatted_address: locationData.formatted_address,
      address: prev.address || locationData.formatted_address,
    }));
  };

  const handleAmenitiesChange = (amenities: string[]) => {
    setFormData((prev) => ({
      ...prev,
      amenities: amenities,
    }));
  };

  const handleImagesChange = (newImages: any[]) => {
    setImages(newImages);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
          <h2 className="text-xl font-bold">
            {location ? "Edit Location" : "Add Location"}
          </h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <XIcon size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Location Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Phone *
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Address & Map Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Location & Address</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Address *
                </label>
                <AddressAutocomplete
                  value={formData.address}
                  onChange={(value) =>
                    setFormData({ ...formData, address: value })
                  }
                  onSelect={(suggestion) => {
                    setFormData((prev) => ({
                      ...prev,
                      address: suggestion.formatted_address,
                      latitude: suggestion.latitude,
                      longitude: suggestion.longitude,
                      formatted_address: suggestion.formatted_address,
                    }));
                  }}
                  placeholder="Search for address..."
                  country={formData.country}
                  error={false}
                />
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    City *
                  </label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) =>
                      setFormData({ ...formData, city: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    State/Province *
                  </label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={(e) =>
                      setFormData({ ...formData, state: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Postal Code *
                  </label>
                  <input
                    type="text"
                    value={formData.postal_code}
                    onChange={(e) =>
                      setFormData({ ...formData, postal_code: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Country *
                  </label>
                  <input
                    type="text"
                    value={formData.country}
                    onChange={(e) =>
                      setFormData({ ...formData, country: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  />
                </div>
              </div>

              {/* Interactive Map */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Location on Map
                </label>
                <MapboxGLMap
                  markers={
                    formData.latitude && formData.longitude
                      ? [
                          {
                            id: "current-location",
                            name: formData.name || "Location",
                            latitude: formData.latitude,
                            longitude: formData.longitude,
                            address: formData.address,
                          },
                        ]
                      : []
                  }
                  center={
                    formData.longitude && formData.latitude
                      ? [formData.longitude, formData.latitude]
                      : [-74.5, 40]
                  }
                  zoom={formData.latitude && formData.longitude ? 15 : 12}
                  style="light"
                  height="400px"
                  onMarkerClick={(marker) => {
                    // Handle marker click if needed
                  }}
                />
              </div>

              {/* Coordinates Display */}
              {formData.latitude && formData.longitude && (
                <div className="grid gap-4 md:grid-cols-2 p-3 bg-muted rounded-md">
                  <div>
                    <p className="text-xs text-muted-foreground">Latitude</p>
                    <p className="text-sm font-mono">
                      {formData.latitude.toFixed(6)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Longitude</p>
                    <p className="text-sm font-mono">
                      {formData.longitude.toFixed(6)}
                    </p>
                  </div>
                </div>
              )}

              {formData.address &&
                (!formData.latitude || !formData.longitude) && (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-sm text-yellow-800">
                      ⚠️ Address will be geocoded when you save. Make sure the
                      address is correct.
                    </p>
                  </div>
                )}
            </div>
          </div>

          {/* Location Settings Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Location Settings</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) =>
                    setFormData({ ...formData, status: e.target.value as any })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {LOCATION_STATUSES.map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Timezone
                </label>
                <select
                  value={formData.timezone}
                  onChange={(e) =>
                    setFormData({ ...formData, timezone: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {TIMEZONES.map((tz) => (
                    <option key={tz} value={tz}>
                      {tz}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Capacity (Max Concurrent Clients)
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.capacity}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      capacity: parseInt(e.target.value) || 1,
                    })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Manager ID (Optional)
                </label>
                <input
                  type="text"
                  value={formData.manager_id || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      manager_id: e.target.value || null,
                    })
                  }
                  placeholder="Staff member ID"
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div className="mt-4 flex items-center gap-2">
              <input
                type="checkbox"
                id="is_primary"
                checked={formData.is_primary}
                onChange={(e) =>
                  setFormData({ ...formData, is_primary: e.target.checked })
                }
                className="w-4 h-4 text-primary bg-background border-border rounded focus:ring-2 focus:ring-primary"
              />
              <label htmlFor="is_primary" className="text-sm font-medium">
                Set as primary location
              </label>
            </div>

            {formData.status === "temporarily_closed" && (
              <div className="mt-4">
                <label className="block text-sm font-medium mb-2">
                  Reopening Date
                </label>
                <input
                  type="datetime-local"
                  value={
                    formData.reopening_date
                      ? new Date(formData.reopening_date)
                          .toISOString()
                          .slice(0, 16)
                      : ""
                  }
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      reopening_date: e.target.value
                        ? new Date(e.target.value)
                        : undefined,
                    })
                  }
                  className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            )}
          </div>

          {/* Amenities Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Amenities</h3>
            <AmenitiesSelector
              selectedAmenities={formData.amenities}
              onAmenitiesChange={handleAmenitiesChange}
              allowCustom={true}
            />
          </div>

          {/* Images Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Location Images</h3>
            <LocationImageUpload
              images={images}
              onImagesChange={handleImagesChange}
              maxImages={10}
              maxFileSize={5}
            />
          </div>

          {/* Business Hours Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Business Hours</h3>
            <div className="space-y-2">
              {DAYS_OF_WEEK.map((day) => (
                <div key={day} className="flex items-center gap-3">
                  <div className="w-24">
                    <span className="text-sm capitalize">{day}</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={!formData.business_hours![day].closed}
                    onChange={(e) =>
                      handleHoursChange(day, "closed", !e.target.checked)
                    }
                    className="w-4 h-4"
                  />
                  {!formData.business_hours![day].closed && (
                    <>
                      <input
                        type="time"
                        value={formData.business_hours![day].open}
                        onChange={(e) =>
                          handleHoursChange(day, "open", e.target.value)
                        }
                        className="px-2 py-1 bg-background border border-border rounded-md text-sm"
                      />
                      <span className="text-sm text-muted-foreground">to</span>
                      <input
                        type="time"
                        value={formData.business_hours![day].close}
                        onChange={(e) =>
                          handleHoursChange(day, "close", e.target.value)
                        }
                        className="px-2 py-1 bg-background border border-border rounded-md text-sm"
                      />
                    </>
                  )}
                  {formData.business_hours![day].closed && (
                    <span className="text-sm text-muted-foreground">
                      Closed
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-muted text-foreground rounded-md hover:bg-muted/80 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors font-medium disabled:opacity-50"
            >
              {createMutation.isPending || updateMutation.isPending
                ? "Saving..."
                : location
                  ? "Update Location"
                  : "Create Location"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
