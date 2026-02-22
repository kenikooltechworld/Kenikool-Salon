import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  UploadIcon,
  AlertTriangleIcon,
  XIcon,
  ChevronDownIcon,
} from "@/components/icons";
import {
  useCreateService,
  useUpdateService,
} from "@/lib/api/hooks/useServices";
import { useLocations } from "@/lib/api/hooks/useLocations";
import { showToast } from "@/lib/utils/toast";
import { apiClient } from "@/lib/api/client";

interface ServiceFormData {
  name: string;
  description: string;
  category: string;
  price: number;
  duration_minutes: number;
  assigned_stylists: string[];
  available_at_locations: string[];
  location_pricing: Array<{
    location_id: string;
    price: number;
    duration_minutes?: number;
  }>;
  tiered_pricing?: any[];
  booking_rules?: any;
  availability?: any;
  max_concurrent_bookings?: number;
  commission_structure?: any;
  required_resources?: any[];
  marketing_settings?: any;
  is_active?: boolean;
}

interface ServiceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (serviceId?: string) => void;
  service?: {
    id: string;
    name: string;
    description?: string;
    category?: string;
    price: number;
    duration_minutes: number;
    photo_url?: string;
    assigned_stylists: string[];
    available_at_locations?: string[];
    location_pricing?: Array<{
      location_id: string;
      price: number;
      duration_minutes?: number;
    }>;
  };
  availableStylists?: Array<{
    id: string;
    name: string;
  }>;
}

const CATEGORIES = ["Hair", "Nails", "Makeup", "Spa", "Massage", "Other"];

export function ServiceFormModal({
  isOpen,
  onClose,
  onSuccess,
  service,
  availableStylists = [],
}: ServiceFormModalProps) {
  const isEdit = !!service;

  const getInitialFormData = (): ServiceFormData => ({
    name: service?.name || "",
    description: service?.description || "",
    category: service?.category || "Hair",
    price: service?.price || 0,
    duration_minutes: service?.duration_minutes || 30,
    assigned_stylists: service?.assigned_stylists || [],
    available_at_locations: service?.available_at_locations || [],
    location_pricing: service?.location_pricing || [],
    tiered_pricing: (service as any)?.tiered_pricing || [],
    booking_rules: (service as any)?.booking_rules || undefined,
    availability: (service as any)?.availability || undefined,
    max_concurrent_bookings: (service as any)?.max_concurrent_bookings || 0,
    commission_structure: (service as any)?.commission_structure || undefined,
    required_resources: (service as any)?.required_resources || [],
    marketing_settings: (service as any)?.marketing_settings || undefined,
    is_active:
      (service as any)?.is_active !== undefined
        ? (service as any).is_active
        : true,
  });

  const [formData, setFormData] =
    useState<ServiceFormData>(getInitialFormData());

  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>(
    service?.photo_url || "",
  );
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isUploadingPhoto, setIsUploadingPhoto] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [expandedLocationId, setExpandedLocationId] = useState<string | null>(
    null,
  );

  const createServiceMutation = useCreateService();
  // CRITICAL: Only create update mutation if we have a valid service ID
  // The ID must be a real MongoDB ID (24 hex chars), not a temporary ID
  const isValidServiceId =
    service?.id &&
    service.id.length === 24 &&
    /^[0-9a-f]{24}$/i.test(service.id);
  const updateServiceMutation = useUpdateService(
    isValidServiceId ? service.id : "",
  );
  const { data: locations = [] } = useLocations();

  const loading =
    createServiceMutation.isPending ||
    updateServiceMutation.isPending ||
    isUploadingPhoto;

  // Reset form when modal opens with a different service
  useEffect(() => {
    if (isOpen) {
      setFormData(getInitialFormData());
      setPhotoPreview(service?.photo_url || "");
      setPhotoFile(null);
      setErrors({});
      setIsUploadingPhoto(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, service?.id]);

  const handleChange = (
    field: keyof ServiceFormData,
    value:
      | string
      | number
      | string[]
      | Array<{
          location_id: string;
          price: number;
          duration_minutes?: number;
        }>,
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhotoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const toggleStylist = (stylistId: string) => {
    const newStylistIds = formData.assigned_stylists.includes(stylistId)
      ? formData.assigned_stylists.filter((id) => id !== stylistId)
      : [...formData.assigned_stylists, stylistId];
    handleChange("assigned_stylists", newStylistIds);
  };

  const toggleLocation = (locationId: string) => {
    const isAssigned = formData.available_at_locations.includes(locationId);
    const newLocations = isAssigned
      ? formData.available_at_locations.filter((id) => id !== locationId)
      : [...formData.available_at_locations, locationId];

    handleChange("available_at_locations", newLocations);

    // Initialize location pricing if not exists
    if (!isAssigned) {
      const newPricing = [...formData.location_pricing];
      if (!newPricing.find((p) => p.location_id === locationId)) {
        newPricing.push({
          location_id: locationId,
          price: formData.price,
          duration_minutes: formData.duration_minutes,
        });
      }
      handleChange("location_pricing", newPricing);
    } else {
      // Remove location pricing when unchecked
      const newPricing = formData.location_pricing.filter(
        (p) => p.location_id !== locationId,
      );
      handleChange("location_pricing", newPricing);
    }
  };

  const updateLocationPricing = (
    locationId: string,
    field: "price" | "duration_minutes",
    value: number,
  ) => {
    const newPricing = formData.location_pricing.map((p) =>
      p.location_id === locationId ? { ...p, [field]: value } : p,
    );
    handleChange("location_pricing", newPricing);
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Service name is required";
    }
    if (formData.price <= 0) {
      newErrors.price = "Price must be greater than 0";
    }
    if (formData.duration_minutes <= 0) {
      newErrors.duration_minutes = "Duration must be greater than 0";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    try {
      let serviceId = service?.id;

      // Step 1: Create or update the service
      if (isEdit && service) {
        // CRITICAL: Validate service ID before updating
        if (!isValidServiceId) {
          throw new Error(
            "Invalid service ID. Please refresh the page and try again.",
          );
        }
        await updateServiceMutation.mutateAsync(formData);
        serviceId = service.id;
        showToast("Service updated successfully", "success");
      } else {
        const newService = await createServiceMutation.mutateAsync(formData);
        serviceId = newService.id;
        showToast("Service created successfully", "success");
      }

      // Step 2: Upload photo if there's a new file and we have a service ID
      if (photoFile && serviceId) {
        setIsUploadingPhoto(true);
        setUploadProgress(0);

        const formDataPhoto = new FormData();
        formDataPhoto.append("file", photoFile);

        // Use apiClient which automatically sends cookies
        try {
          await apiClient.post(
            `/api/services/${serviceId}/photo`,
            formDataPhoto,
            {
              // DO NOT set Content-Type header - let axios/browser set it with boundary
              // Setting it manually breaks multipart/form-data
              onUploadProgress: (progressEvent: any) => {
                if (progressEvent.lengthComputable) {
                  const percentComplete = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total,
                  );
                  setUploadProgress(percentComplete);
                }
              },
            },
          );

          setIsUploadingPhoto(false);
          setUploadProgress(0);
          showToast("Photo uploaded successfully", "success");
        } catch (uploadError) {
          setIsUploadingPhoto(false);
          setUploadProgress(0);
          throw new Error(
            uploadError instanceof Error
              ? uploadError.message
              : "Photo upload failed",
          );
        }
      }

      // Pass the service ID to onSuccess callback
      onSuccess(serviceId);
      onClose();
    } catch (error) {
      console.error("Submit error:", error);
      setIsUploadingPhoto(false);
      const errorMessage =
        error instanceof Error ? error.message : "An error occurred";
      showToast(errorMessage, "error");
      setErrors({
        submit: errorMessage,
      });
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">
          {isEdit ? "Edit Service" : "Add Service"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.submit && (
            <Alert variant="error">
              <AlertTriangleIcon size={20} />
              <div>
                <p className="text-sm font-semibold mb-1">Error</p>
                <p className="text-sm">{errors.submit}</p>
              </div>
            </Alert>
          )}

          {/* Service Name */}
          <div>
            <Label htmlFor="name">Service Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => handleChange("name", e.target.value)}
              placeholder="e.g., Haircut & Styling"
              error={!!errors.name}
            />
            {errors.name && (
              <p className="text-sm text-destructive mt-1">{errors.name}</p>
            )}
          </div>

          {/* Category */}
          <div>
            <Label htmlFor="category">Category *</Label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => handleChange("category", e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleChange("description", e.target.value)}
              placeholder="Describe the service..."
              rows={3}
            />
          </div>

          {/* Price and Duration */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="price">Price (₦) *</Label>
              <Input
                id="price"
                type="number"
                value={formData.price || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  handleChange("price", value === "" ? 0 : parseFloat(value));
                }}
                placeholder="0"
                error={!!errors.price}
              />
              {errors.price && (
                <p className="text-sm text-destructive mt-1">{errors.price}</p>
              )}
            </div>
            <div>
              <Label htmlFor="duration">Duration (mins) *</Label>
              <Input
                id="duration"
                type="number"
                value={formData.duration_minutes || ""}
                onChange={(e) => {
                  const value = e.target.value;
                  handleChange(
                    "duration_minutes",
                    value === "" ? 0 : parseInt(value),
                  );
                }}
                placeholder="30"
                error={!!errors.duration_minutes}
              />
              {errors.duration_minutes && (
                <p className="text-sm text-destructive mt-1">
                  {errors.duration_minutes}
                </p>
              )}
            </div>
          </div>

          {/* Photo Upload */}
          <div>
            <Label>Service Photo</Label>
            <div className="mt-2">
              {photoPreview ? (
                <div className="relative w-full h-48 rounded-lg overflow-hidden border border-border">
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-full object-cover"
                  />
                  {isUploadingPhoto && (
                    <div className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center">
                      <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mb-2" />
                      <span className="text-white font-bold">
                        {uploadProgress}%
                      </span>
                    </div>
                  )}
                  {!isUploadingPhoto && (
                    <button
                      type="button"
                      onClick={() => {
                        setPhotoPreview("");
                        setPhotoFile(null);
                      }}
                      className="absolute top-2 right-2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
                    >
                      <XIcon size={16} />
                    </button>
                  )}
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                  <UploadIcon
                    size={32}
                    className="text-muted-foreground mb-2"
                  />
                  <p className="text-sm text-muted-foreground">
                    Click to upload photo
                  </p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                    className="hidden"
                    disabled={isUploadingPhoto}
                  />
                </label>
              )}
              {isUploadingPhoto && !photoPreview && (
                <div className="mt-2">
                  <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-primary h-full transition-all duration-300 ease-out"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Uploading... {uploadProgress}%
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Stylist Selection */}
          <div>
            <Label>Assign Stylists</Label>
            <div className="mt-2 space-y-2 max-h-40 overflow-y-auto border border-border rounded-lg p-3">
              {availableStylists.length > 0 ? (
                availableStylists.map((stylist) => (
                  <label
                    key={stylist.id}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={formData.assigned_stylists.includes(stylist.id)}
                      onChange={() => toggleStylist(stylist.id)}
                      className="rounded border-border"
                    />
                    <span className="text-sm text-foreground">
                      {stylist.name}
                    </span>
                  </label>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-2">
                  No stylists available. Add staff members first.
                </p>
              )}
            </div>
          </div>

          {/* Location Assignment */}
          <div>
            <Label>Available at Locations</Label>
            {locations.length > 0 ? (
              <div className="mt-2 space-y-2 border border-border rounded-lg p-3">
                {locations.map((location) => {
                  const locationPricing = formData.location_pricing.find(
                    (p) => p.location_id === location._id,
                  );
                  const isAssigned = formData.available_at_locations.includes(
                    location._id,
                  );

                  return (
                    <div key={location._id} className="space-y-2">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id={`location-${location._id}`}
                          checked={isAssigned}
                          onChange={() => toggleLocation(location._id)}
                          className="rounded border-border"
                        />
                        <label
                          htmlFor={`location-${location._id}`}
                          className="flex-1 text-sm font-medium text-foreground cursor-pointer"
                        >
                          {location.name}
                        </label>
                        {isAssigned && (
                          <button
                            type="button"
                            onClick={() =>
                              setExpandedLocationId(
                                expandedLocationId === location._id
                                  ? null
                                  : location._id,
                              )
                            }
                            className="p-1 hover:bg-muted rounded"
                          >
                            <ChevronDownIcon
                              size={16}
                              className={`transition-transform ${
                                expandedLocationId === location._id
                                  ? "rotate-180"
                                  : ""
                              }`}
                            />
                          </button>
                        )}
                      </div>

                      {/* Location-specific pricing */}
                      {expandedLocationId === location._id &&
                        isAssigned &&
                        locationPricing && (
                          <div className="ml-6 p-2 bg-muted/50 rounded space-y-2">
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <Label
                                  htmlFor={`price-${location._id}`}
                                  className="text-xs"
                                >
                                  Price (₦)
                                </Label>
                                <Input
                                  id={`price-${location._id}`}
                                  type="number"
                                  value={locationPricing.price || ""}
                                  onChange={(e) =>
                                    updateLocationPricing(
                                      location._id,
                                      "price",
                                      parseFloat(e.target.value) || 0,
                                    )
                                  }
                                  placeholder="0"
                                  min="0"
                                  step="0.01"
                                  className="text-sm"
                                />
                              </div>
                              <div>
                                <Label
                                  htmlFor={`duration-${location._id}`}
                                  className="text-xs"
                                >
                                  Duration (mins)
                                </Label>
                                <Input
                                  id={`duration-${location._id}`}
                                  type="number"
                                  value={locationPricing.duration_minutes || ""}
                                  onChange={(e) =>
                                    updateLocationPricing(
                                      location._id,
                                      "duration_minutes",
                                      parseInt(e.target.value) || 0,
                                    )
                                  }
                                  placeholder="30"
                                  min="1"
                                  className="text-sm"
                                />
                              </div>
                            </div>
                          </div>
                        )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground p-3 border border-border rounded-lg text-center mt-2">
                No locations available. Create locations first.
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? (
                <>
                  <Spinner size="sm" />
                  {isUploadingPhoto
                    ? "Uploading photo..."
                    : isEdit
                      ? "Updating..."
                      : "Creating..."}
                </>
              ) : (
                <>{isEdit ? "Update Service" : "Create Service"}</>
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
