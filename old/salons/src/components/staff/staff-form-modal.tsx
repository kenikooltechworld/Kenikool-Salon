import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  XIcon,
  UploadIcon,
  UserIcon,
  ChevronDownIcon,
} from "@/components/icons";
import {
  useCreateStylist,
  useUpdateStylist,
  useUploadStylistPhoto,
} from "@/lib/api/hooks/useStylists";
import { useLocations } from "@/lib/api/hooks/useLocations";
import { Stylist } from "@/lib/api/types";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

interface StaffFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  stylist?: Stylist;
}

export function StaffFormModal({
  isOpen,
  onClose,
  onSuccess,
  stylist,
}: StaffFormModalProps) {
  // Initialize form data based on stylist prop
  const getInitialFormData = () => ({
    name: stylist?.name || "",
    email: stylist?.email || "",
    phone: stylist?.phone || "",
    bio: stylist?.bio || "",
    commission_type:
      (stylist?.commission_type as "percentage" | "fixed") || "percentage",
    commission_value: stylist?.commission_value || 30,
    is_active: stylist?.is_active ?? true,
    specialties: stylist?.specialties || [],
    assigned_locations: stylist?.assigned_locations || [],
    location_availability: stylist?.location_availability || {},
  });

  const [formData, setFormData] = useState(getInitialFormData());
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>(
    stylist?.photo_url || "",
  );
  const [newSpecialty, setNewSpecialty] = useState("");
  const [expandedLocationId, setExpandedLocationId] = useState<string | null>(
    null,
  );

  const { toast } = useToast();
  const { data: locations = [] } = useLocations();
  const createStylistMutation = useCreateStylist();
  const updateStylistMutation = useUpdateStylist(stylist?.id || "");
  const uploadPhotoMutation = useUploadStylistPhoto(stylist?.id || "undefined");

  // For new stylists, we'll create a temporary mutation after creation
  const queryClient = useQueryClient();

  const isEditing = !!stylist;
  const isSubmitting =
    createStylistMutation.isPending ||
    updateStylistMutation.isPending ||
    uploadPhotoMutation.isPending;

  // Reset form when modal opens/closes or stylist changes
  useEffect(() => {
    if (isOpen) {
      setFormData(getInitialFormData());
      setPhotoPreview(stylist?.photo_url || "");
      setPhotoFile(null);
      setNewSpecialty("");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, stylist?.id]); // Only reset when modal opens or stylist changes

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast("Image size must be less than 5MB", "error");
        return;
      }
      setPhotoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadPhoto = async (): Promise<string | null> => {
    if (!photoFile) return null;

    try {
      const result = await uploadPhotoMutation.mutateAsync(photoFile);
      return result.photo_url;
    } catch (error) {
      throw error;
    }
  };

  const handleAddSpecialty = () => {
    if (
      newSpecialty.trim() &&
      !formData.specialties.includes(newSpecialty.trim())
    ) {
      setFormData({
        ...formData,
        specialties: [...formData.specialties, newSpecialty.trim()],
      });
      setNewSpecialty("");
    }
  };

  const handleRemoveSpecialty = (specialty: string) => {
    setFormData({
      ...formData,
      specialties: formData.specialties.filter((s) => s !== specialty),
    });
  };

  const handleToggleLocation = (locationId: string) => {
    const isAssigned = formData.assigned_locations.includes(locationId);
    setFormData({
      ...formData,
      assigned_locations: isAssigned
        ? formData.assigned_locations.filter((id) => id !== locationId)
        : [...formData.assigned_locations, locationId],
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    console.log("=== STAFF FORM SUBMIT START ===");
    console.log("Form Data:", formData);
    console.log("Is Editing:", isEditing);

    try {
      let createdStylistId = stylist?.id;

      // For new stylists, create first, then upload photo
      if (!isEditing) {
        console.log("Creating stylist with data:", formData);
        const result = await createStylistMutation.mutateAsync(formData);
        createdStylistId = result.id;
        console.log("Stylist created successfully:", result);
        console.log(
          "Created stylist assigned_locations:",
          result.assigned_locations,
        );
        console.log("Created stylist specialties:", result.specialties);

        // Now upload photo if provided
        if (photoFile && createdStylistId) {
          console.log("Uploading photo for new stylist...");
          try {
            const formDataForUpload = new FormData();
            formDataForUpload.append("file", photoFile);

            await apiClient.post(
              `/api/stylists/${createdStylistId}/photo`,
              formDataForUpload,
              {
                headers: {
                  "Content-Type": "multipart/form-data",
                },
              },
            );
            console.log("Photo uploaded successfully");
            queryClient.invalidateQueries({ queryKey: ["stylists"] });
            queryClient.invalidateQueries({
              queryKey: ["stylists", createdStylistId],
            });
          } catch (uploadError) {
            console.error("Photo upload error:", uploadError);
            toast(
              uploadError instanceof Error
                ? uploadError.message
                : "Failed to upload photo",
              "error",
            );
            // Don't return - photo upload failure shouldn't block stylist creation
          }
        }
      } else {
        // For existing stylists, upload photo first if provided
        if (photoFile) {
          console.log("Uploading photo...");
          try {
            const result = await uploadPhotoMutation.mutateAsync(photoFile);
            console.log("Photo uploaded:", result.photo_url);
          } catch (uploadError) {
            console.error("Photo upload error:", uploadError);
            toast(
              uploadError instanceof Error
                ? uploadError.message
                : "Failed to upload photo",
              "error",
            );
            return; // Stop if photo upload fails for existing stylist
          }
        }

        console.log("Updating stylist...");
        const submitData = {
          ...formData,
          assigned_locations: formData.assigned_locations,
          location_availability: formData.location_availability,
        };
        console.log("Submit data for update:", submitData);
        const result = await updateStylistMutation.mutateAsync(submitData);
        console.log("Stylist updated successfully:", result);
        console.log(
          "Updated stylist assigned_locations:",
          result.assigned_locations,
        );
        console.log("Updated stylist specialties:", result.specialties);
      }

      // Always show success toast - call it immediately
      const successMessage = isEditing
        ? "Staff member updated successfully"
        : "Staff member added successfully";

      console.log("Showing success toast:", successMessage);
      toast(successMessage, "success");

      // Call success callback
      console.log("Calling onSuccess");
      onSuccess();

      // Close modal after a delay to ensure toast renders
      console.log("Scheduling modal close");
      setTimeout(() => {
        console.log("Closing modal now");
        onClose();
      }, 150);

      console.log("=== STAFF FORM SUBMIT COMPLETE ===");
    } catch (err) {
      console.error("=== STAFF FORM SUBMIT ERROR ===", err);
      const errorMessage =
        err instanceof Error ? err.message : "Failed to save staff member";
      console.log("Showing error toast:", errorMessage);
      toast(errorMessage, "error");
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          {isEditing ? "Edit Staff Member" : "Add Staff Member"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Photo Upload */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Photo
            </label>
            <div className="flex items-start gap-4">
              {/* Preview */}
              <div className="relative w-24 h-24 rounded-lg overflow-hidden bg-muted flex items-center justify-center">
                {photoPreview ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <UserIcon size={32} className="text-muted-foreground" />
                )}
              </div>

              {/* Upload Button */}
              <div className="flex-1">
                <input
                  type="file"
                  id="photo-upload"
                  accept="image/*"
                  onChange={handlePhotoChange}
                  className="hidden"
                  disabled={uploadPhotoMutation.isPending}
                />
                <label htmlFor="photo-upload">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      document.getElementById("photo-upload")?.click()
                    }
                    disabled={uploadPhotoMutation.isPending}
                  >
                    <UploadIcon size={16} />
                    {photoPreview ? "Change Photo" : "Upload Photo"}
                  </Button>
                </label>
                <p className="text-xs text-muted-foreground mt-1">
                  JPG, PNG or GIF. Max 5MB.
                </p>
              </div>
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Full Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              placeholder="e.g., Jane Doe"
              required
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Email *
            </label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="jane@example.com"
              required
            />
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Phone *
            </label>
            <Input
              type="tel"
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
              placeholder="+234 800 000 0000"
              required
            />
          </div>

          {/* Bio */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Bio
            </label>
            <textarea
              value={formData.bio}
              onChange={(e) =>
                setFormData({ ...formData, bio: e.target.value })
              }
              placeholder="Brief description about the stylist..."
              rows={3}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground resize-none"
            />
          </div>

          {/* Specialties */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Specialties
            </label>
            <div className="flex gap-2 mb-2">
              <Input
                value={newSpecialty}
                onChange={(e) => setNewSpecialty(e.target.value)}
                placeholder="e.g., Hair Coloring, Braiding"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddSpecialty();
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                onClick={handleAddSpecialty}
                disabled={!newSpecialty.trim()}
              >
                Add
              </Button>
            </div>
            {formData.specialties.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.specialties.map((specialty) => (
                  <Badge
                    key={specialty}
                    variant="secondary"
                    className="flex items-center gap-1"
                  >
                    {specialty}
                    <button
                      type="button"
                      onClick={() => handleRemoveSpecialty(specialty)}
                      className="ml-1 hover:text-destructive"
                    >
                      <XIcon size={12} />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Commission Type */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Commission Type *
            </label>
            <select
              value={formData.commission_type}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  commission_type: e.target.value as "percentage" | "fixed",
                })
              }
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
              required
            >
              <option value="percentage">Percentage</option>
              <option value="fixed">Fixed Amount</option>
            </select>
          </div>

          {/* Commission Value */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Commission Value *
            </label>
            <Input
              type="number"
              value={formData.commission_value}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  commission_value: Number(e.target.value),
                })
              }
              min="0"
              step={formData.commission_type === "percentage" ? "1" : "0.01"}
              max={
                formData.commission_type === "percentage" ? "100" : undefined
              }
              required
            />
            <p className="text-xs text-muted-foreground mt-1">
              {formData.commission_type === "percentage"
                ? "Percentage of service price (0-100)"
                : "Fixed amount in Naira"}
            </p>
          </div>

          {/* Location Assignment */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Assigned Locations
            </label>
            {locations.length > 0 ? (
              <div className="space-y-2 border border-border rounded-lg p-3">
                {locations.map((location) => (
                  <div key={location._id} className="space-y-2">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id={`location-${location._id}`}
                        checked={formData.assigned_locations.includes(
                          location._id,
                        )}
                        onChange={() => handleToggleLocation(location._id)}
                        className="rounded border-border"
                      />
                      <label
                        htmlFor={`location-${location._id}`}
                        className="flex-1 text-sm font-medium text-foreground cursor-pointer"
                      >
                        {location.name}
                      </label>
                      {formData.assigned_locations.includes(location._id) && (
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

                    {/* Availability for this location */}
                    {expandedLocationId === location._id &&
                      formData.assigned_locations.includes(location._id) && (
                        <div className="ml-6 p-2 bg-muted/50 rounded space-y-2">
                          <p className="text-xs font-medium text-muted-foreground">
                            Availability at {location.name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Configure availability per location (optional)
                          </p>
                        </div>
                      )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground p-3 border border-border rounded-lg text-center">
                No locations available. Create locations first.
              </p>
            )}
            {formData.assigned_locations.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {formData.assigned_locations.map((locationId) => {
                  const location = locations.find((l) => l._id === locationId);
                  return (
                    <Badge key={locationId} variant="secondary">
                      {location?.name || locationId}
                    </Badge>
                  );
                })}
              </div>
            )}
          </div>

          {/* Active Status */}
          <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-foreground">
                Active Status
              </p>
              <p className="text-xs text-muted-foreground">
                Is this staff member currently active?
              </p>
            </div>
            <Switch
              checked={formData.is_active}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, is_active: checked })
              }
            />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Spinner size="sm" />
                  {isEditing ? "Updating..." : "Creating..."}
                </>
              ) : isEditing ? (
                "Update Staff"
              ) : (
                "Add Staff"
              )}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
