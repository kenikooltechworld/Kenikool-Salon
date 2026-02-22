import { useState } from "react";
import React from "react";
import { Button } from "@/components/ui/button";
import { XIcon } from "@/components/icons";
import { useImageUpload } from "@/hooks/useImageUpload";
import { ImageLightbox } from "@/components/services/ImageLightbox";
import type { Staff } from "@/types/staff";

interface StaffFormProps {
  onSubmit: (
    data: Omit<Staff, "id" | "createdAt" | "updatedAt">,
  ) => Promise<void>;
  isLoading?: boolean;
  initialData?: Partial<Staff>;
}

export function StaffForm({
  onSubmit,
  isLoading = false,
  initialData,
}: StaffFormProps) {
  const isEditing = !!initialData?.id;
  const [formData, setFormData] = useState({
    firstName: initialData?.firstName || "",
    lastName: initialData?.lastName || "",
    email: initialData?.email || "",
    phone: initialData?.phone || "",
    role_ids: initialData?.role_ids || ([] as string[]),
    specialties: initialData?.specialties || ([] as string[]),
    certifications: initialData?.certifications || ([] as string[]),
    certification_files: initialData?.certification_files || ([] as string[]),
    payment_type: (initialData?.payment_type || "hourly") as
      | "hourly"
      | "daily"
      | "weekly"
      | "monthly"
      | "commission",
    payment_rate: initialData?.payment_rate || 0,
    hire_date: initialData?.hire_date || "",
    bio: initialData?.bio || "",
    profile_image_url: initialData?.profile_image_url || "",
    status: (initialData?.status || "active") as
      | "active"
      | "inactive"
      | "on_leave"
      | "terminated",
  });
  const [specialtyInput, setSpecialtyInput] = useState("");
  const [certificationInput, setCertificationInput] = useState("");
  const [error, setError] = useState("");
  const [roles, setRoles] = useState<Array<{ id: string; name: string }>>([]);
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);

  // Image upload hooks
  const profileImageUpload = useImageUpload({ folder: "staff-profiles" });
  const certificateUpload = useImageUpload({ folder: "staff-certificates" });

  // Fetch roles on mount
  React.useEffect(() => {
    const fetchRoles = async () => {
      try {
        const response = await fetch("/api/v1/roles");
        if (response.ok) {
          const data = await response.json();
          setRoles(data.roles || []);
        }
      } catch (err) {
        console.error("Failed to fetch roles:", err);
      }
    };
    fetchRoles();
  }, []);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value, type } = e.target;
    if (type === "checkbox") {
      setFormData((prev) => ({
        ...prev,
        [name]: (e.target as HTMLInputElement).checked,
      }));
    } else if (name === "payment_rate") {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleAddSpecialty = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const specialty = specialtyInput.trim();
      if (specialty && !formData.specialties.includes(specialty)) {
        setFormData((prev) => ({
          ...prev,
          specialties: [...prev.specialties, specialty],
        }));
        setSpecialtyInput("");
      }
    }
  };

  const handleRemoveSpecialty = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      specialties: prev.specialties.filter((_, i) => i !== index),
    }));
  };

  const handleAddCertification = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const cert = certificationInput.trim();
      if (cert && !formData.certifications.includes(cert)) {
        setFormData((prev) => ({
          ...prev,
          certifications: [...prev.certifications, cert],
        }));
        setCertificationInput("");
      }
    }
  };

  const handleRemoveCertification = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      certifications: prev.certifications.filter((_, i) => i !== index),
    }));
  };

  const handleRoleToggle = (roleId: string) => {
    setFormData((prev) => ({
      ...prev,
      role_ids: prev.role_ids.includes(roleId)
        ? prev.role_ids.filter((id) => id !== roleId)
        : [...prev.role_ids, roleId],
    }));
  };

  const handleProfileImageChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = profileImageUpload.handleFileChange(e);
    if (file) {
      setError("");
      try {
        const url = await profileImageUpload.uploadImage(file);
        setFormData((prev) => ({
          ...prev,
          profile_image_url: url,
        }));
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to upload profile image",
        );
      }
    }
  };

  const handleCertificateFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setError("");

    try {
      // Upload each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const url = await certificateUpload.uploadImage(file);
        setFormData((prev) => ({
          ...prev,
          certification_files: [...prev.certification_files, url],
        }));
      }
      // Reset file input
      e.target.value = "";
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to upload certificate file(s)",
      );
    }
  };

  const handleRemoveCertificateFile = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      certification_files: prev.certification_files.filter(
        (_, i) => i !== index,
      ),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.firstName.trim()) {
      setError("First name is required");
      return;
    }

    if (!formData.lastName.trim()) {
      setError("Last name is required");
      return;
    }

    if (!formData.email.trim()) {
      setError("Email is required");
      return;
    }

    try {
      await onSubmit({
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        role_ids: formData.role_ids,
        specialties: formData.specialties,
        certifications: formData.certifications,
        certification_files: formData.certification_files,
        payment_type: formData.payment_type,
        payment_rate: formData.payment_rate,
        hire_date: formData.hire_date,
        bio: formData.bio,
        profile_image_url: formData.profile_image_url,
        status: formData.status,
      } as any);

      setFormData({
        firstName: "",
        lastName: "",
        email: "",
        phone: "",
        role_ids: [],
        specialties: [],
        certifications: [],
        certification_files: [],
        payment_type: "hourly",
        payment_rate: 0,
        hire_date: "",
        bio: "",
        profile_image_url: "",
        status: "active",
      });
      setSpecialtyInput("");
      setCertificationInput("");
      profileImageUpload.clearPreview();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : isEditing
            ? "Failed to update staff member"
            : "Failed to add staff member",
      );
    }
  };

  const isPending =
    isLoading ||
    profileImageUpload.isUploading ||
    certificateUpload.isUploading;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 text-destructive text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            First Name *
          </label>
          <input
            type="text"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            placeholder="First name"
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Last Name *
          </label>
          <input
            type="text"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            placeholder="Last name"
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Email *
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="email@example.com"
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Phone
          </label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="Phone number"
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-2">
            Roles
          </label>
          <div className="space-y-2">
            {roles.length > 0 ? (
              roles.map((role) => (
                <label
                  key={role.id}
                  className="flex items-center gap-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={formData.role_ids.includes(role.id)}
                    onChange={() => handleRoleToggle(role.id)}
                    className="w-4 h-4 rounded border-border"
                  />
                  <span className="text-sm text-foreground">{role.name}</span>
                </label>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No roles available
              </p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Payment Type
          </label>
          <select
            name="payment_type"
            value={formData.payment_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          >
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="commission">Commission</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Payment Rate{" "}
            {(formData.payment_type as string) === "commission" ? "(%)" : "(₦)"}
          </label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              name="payment_rate"
              value={formData.payment_rate}
              onChange={handleChange}
              placeholder="0.00"
              step={
                (formData.payment_type as string) === "commission"
                  ? "0.1"
                  : "0.01"
              }
              min="0"
              max={
                (formData.payment_type as string) === "commission"
                  ? "100"
                  : undefined
              }
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              {(formData.payment_type as string) === "commission"
                ? "% commission"
                : `per ${formData.payment_type}`}
            </span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Hire Date
          </label>
          <input
            type="date"
            name="hire_date"
            value={formData.hire_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Status
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="on_leave">On Leave</option>
            <option value="terminated">Terminated</option>
          </select>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-1">
            Bio
          </label>
          <textarea
            name="bio"
            value={formData.bio}
            onChange={handleChange}
            placeholder="Staff member bio/description"
            rows={3}
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-1">
            Profile Image
          </label>
          <div className="space-y-2">
            {profileImageUpload.preview && (
              <div className="relative w-full h-40 rounded-lg overflow-hidden border border-border">
                <img
                  src={profileImageUpload.preview}
                  alt="Profile preview"
                  className="w-full h-full object-cover"
                />
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleProfileImageChange}
              disabled={profileImageUpload.isUploading}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm disabled:opacity-50 cursor-pointer"
            />
            {profileImageUpload.isUploading && (
              <p className="text-xs text-muted-foreground">Uploading...</p>
            )}
            {profileImageUpload.preview && (
              <button
                type="button"
                onClick={() => {
                  profileImageUpload.clearPreview();
                  setFormData((prev) => ({
                    ...prev,
                    profile_image_url: "",
                  }));
                }}
                className="text-xs text-destructive hover:text-destructive/80 cursor-pointer"
              >
                Remove
              </button>
            )}
          </div>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-1">
            Specialties
          </label>
          <div className="space-y-2">
            <input
              type="text"
              value={specialtyInput}
              onChange={(e) => setSpecialtyInput(e.target.value)}
              onKeyDown={handleAddSpecialty}
              placeholder="Type specialty and press Enter"
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            {formData.specialties.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.specialties.map((specialty, index) => (
                  <div
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-sm text-primary"
                  >
                    <span>{specialty}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveSpecialty(index)}
                      className="hover:bg-primary/20 rounded-full p-0.5 transition cursor-pointer"
                      aria-label="Remove specialty"
                    >
                      <XIcon size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-1">
            Certifications
          </label>
          <div className="space-y-2">
            <input
              type="text"
              value={certificationInput}
              onChange={(e) => setCertificationInput(e.target.value)}
              onKeyDown={handleAddCertification}
              placeholder="Type certification and press Enter"
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            {formData.certifications.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.certifications.map((cert, index) => (
                  <div
                    key={index}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-sm text-primary"
                  >
                    <span>{cert}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveCertification(index)}
                      className="hover:bg-primary/20 rounded-full p-0.5 transition cursor-pointer"
                      aria-label="Remove certification"
                    >
                      <XIcon size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-foreground mb-1">
            Certificate Files (Optional)
          </label>
          <div className="space-y-2">
            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              onChange={handleCertificateFileChange}
              disabled={certificateUpload.isUploading}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm disabled:opacity-50 cursor-pointer"
              multiple
            />
            {certificateUpload.isUploading && (
              <p className="text-xs text-muted-foreground">
                Uploading certificate(s)...
              </p>
            )}
            {formData.certification_files.length > 0 && (
              <div className="space-y-3">
                <p className="text-xs text-muted-foreground font-medium">
                  {formData.certification_files.length} certificate(s) uploaded
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {formData.certification_files.map((fileUrl, index) => {
                    const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(fileUrl);
                    const fileName = fileUrl.split("/").pop() || "certificate";

                    return (
                      <div
                        key={index}
                        className="relative group rounded-lg border border-border overflow-hidden bg-muted/50 hover:bg-muted transition cursor-pointer"
                        onClick={() => isImage && setLightboxImage(fileUrl)}
                      >
                        {isImage ? (
                          <img
                            src={fileUrl}
                            alt={`Certificate ${index + 1}`}
                            className="w-full h-24 object-cover"
                          />
                        ) : (
                          <div className="w-full h-24 flex items-center justify-center bg-muted">
                            <div className="text-center">
                              <div className="text-2xl mb-1">📄</div>
                              <p className="text-xs text-muted-foreground font-medium truncate px-2">
                                {fileName.substring(0, 15)}
                              </p>
                            </div>
                          </div>
                        )}
                        {isImage && (
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                            <span className="text-white text-sm font-medium">
                              View
                            </span>
                          </div>
                        )}
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveCertificateFile(index);
                          }}
                          className="absolute top-1 right-1 bg-destructive/90 hover:bg-destructive text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
                          aria-label="Remove certificate"
                        >
                          <XIcon size={14} />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-2 justify-end pt-4">
        <Button type="submit" disabled={isPending} className="cursor-pointer">
          {profileImageUpload.isUploading
            ? "Uploading..."
            : isLoading
              ? isEditing
                ? "Updating..."
                : "Adding..."
              : isEditing
                ? "Update Staff Member"
                : "Add Staff Member"}
        </Button>
      </div>

      {/* Certificate Lightbox */}
      <ImageLightbox
        isOpen={!!lightboxImage}
        imageUrl={lightboxImage || ""}
        onClose={() => setLightboxImage(null)}
      />
    </form>
  );
}
