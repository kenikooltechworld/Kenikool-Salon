import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeftIcon,
  EditIcon,
  TrashIcon,
  PhoneIcon,
  MailIcon,
  CalendarIcon,
  BriefcaseIcon,
  AwardIcon,
  StarIcon,
  FileIcon,
  ClockIcon,
  DollarSignIcon,
} from "@/components/icons";
import {
  useStaffMember,
  useDeleteStaff,
  useUpdateStaff,
} from "@/hooks/useStaff";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { AddStaffModal } from "@/components/staff/AddStaffModal";
import { ImageLightbox } from "@/components/services/ImageLightbox";
import type { Staff } from "@/types/staff";

export default function StaffDetailPage() {
  const { staffId } = useParams<{ staffId: string }>();
  const navigate = useNavigate();
  const { data: staff, isLoading, error } = useStaffMember(staffId || "");
  const deleteStaffMutation = useDeleteStaff();
  const updateStaffMutation = useUpdateStaff();
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);

  if (!staffId) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Invalid staff ID
      </div>
    );
  }

  const handleDelete = async () => {
    await deleteStaffMutation.mutateAsync(staffId);
    navigate("/staff");
  };

  const handleEditSubmit = async (
    data: Omit<Staff, "id" | "createdAt" | "updatedAt">,
  ) => {
    await updateStaffMutation.mutateAsync({
      id: staffId!,
      ...data,
    });
    setIsEditModalOpen(false);
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "active":
        return "default";
      case "inactive":
        return "secondary";
      case "on_leave":
        return "outline";
      case "terminated":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getStatusLabel = (status: string) => {
    return status
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  if (isLoading) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        Loading staff details...
      </div>
    );
  }

  if (error || !staff) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate("/staff")}
          className="flex items-center gap-2 text-primary hover:text-primary/80 cursor-pointer"
        >
          <ArrowLeftIcon size={18} />
          Back to Staff
        </button>
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-destructive text-sm">
          Failed to load staff details. Please try again.
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <button
          onClick={() => navigate("/staff")}
          className="flex items-center gap-2 text-primary hover:text-primary/80 cursor-pointer"
        >
          <ArrowLeftIcon size={18} />
          Back to Staff
        </button>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex gap-4">
            {staff.profile_image_url && (
              <img
                src={staff.profile_image_url}
                alt={`${staff.firstName} ${staff.lastName}`}
                className="w-20 h-20 rounded-lg object-cover border border-border cursor-pointer hover:opacity-80 transition"
                onClick={() => setLightboxImage(staff.profile_image_url)}
              />
            )}
            <div>
              <h1 className="text-3xl font-bold text-foreground">
                {staff.firstName} {staff.lastName}
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <a
                  href={`mailto:${staff.email}`}
                  className="text-sm text-primary hover:text-primary/80 transition"
                >
                  {staff.email}
                </a>
              </div>
              <Badge
                variant={getStatusBadgeVariant(staff.status)}
                className="mt-2"
              >
                {getStatusLabel(staff.status)}
              </Badge>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              className="gap-2 cursor-pointer"
              onClick={() => setIsEditModalOpen(true)}
            >
              <EditIcon size={18} />
              Edit
            </Button>
            <Button
              variant="destructive"
              className="gap-2 cursor-pointer"
              onClick={() => setDeleteConfirm(true)}
            >
              <TrashIcon size={18} />
              Delete
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <MailIcon size={20} />
              Contact Information
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <MailIcon
                  size={18}
                  className="text-muted-foreground mt-1 flex-shrink-0"
                />
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Email</p>
                  <a
                    href={`mailto:${staff.email}`}
                    className="text-foreground font-medium hover:text-primary transition"
                  >
                    {staff.email}
                  </a>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <PhoneIcon
                  size={18}
                  className="text-muted-foreground mt-1 flex-shrink-0"
                />
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Phone</p>
                  <p className="text-foreground font-medium">
                    {staff.phone || "N/A"}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Employment Information */}
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <BriefcaseIcon size={20} />
              Employment Information
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <CalendarIcon
                  size={18}
                  className="text-muted-foreground mt-1 flex-shrink-0"
                />
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Hire Date
                  </p>
                  <p className="text-foreground font-medium">
                    {staff.hire_date
                      ? new Date(staff.hire_date).toLocaleDateString()
                      : "N/A"}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Status</p>
                <Badge variant={getStatusBadgeVariant(staff.status)}>
                  {getStatusLabel(staff.status)}
                </Badge>
              </div>
              <div className="flex items-start gap-3">
                <BriefcaseIcon
                  size={18}
                  className="text-muted-foreground mt-1 flex-shrink-0"
                />
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Payment Type
                  </p>
                  <p className="text-foreground font-medium capitalize">
                    {staff.payment_type}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <DollarSignIcon
                  size={18}
                  className="text-muted-foreground mt-1 flex-shrink-0"
                />
                <div>
                  <p className="text-sm text-muted-foreground mb-1">
                    Payment Rate
                  </p>
                  <p className="text-foreground font-medium">
                    {staff.payment_type === "commission"
                      ? `${staff.payment_rate}%`
                      : `₦${staff.payment_rate.toLocaleString()}`}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Bio */}
          {staff.bio && (
            <div className="bg-card border border-border rounded-lg p-6 space-y-4">
              <h2 className="text-lg font-semibold text-foreground">Bio</h2>
              <p className="text-foreground whitespace-pre-wrap">{staff.bio}</p>
            </div>
          )}

          {/* Specialties */}
          {staff.specialties.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6 space-y-4">
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <StarIcon size={20} />
                Specialties
              </h2>
              <div className="flex flex-wrap gap-2">
                {staff.specialties.map((specialty: string, idx: number) => (
                  <Badge key={idx} variant="outline">
                    {specialty}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Certifications */}
          {staff.certifications.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6 space-y-4">
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <AwardIcon size={20} />
                Certifications
              </h2>
              <div className="flex flex-wrap gap-2">
                {staff.certifications.map((cert: string, idx: number) => (
                  <Badge key={idx} variant="secondary">
                    {cert}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Certificate Files */}
          {staff.certification_files.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6 space-y-4">
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <FileIcon size={20} />
                Certificate Files
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {staff.certification_files.map(
                  (fileUrl: string, idx: number) => {
                    const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(fileUrl);
                    const fileName = fileUrl.split("/").pop() || "certificate";

                    return (
                      <div
                        key={idx}
                        className="group relative rounded-lg border border-border overflow-hidden bg-muted/50 hover:bg-muted transition cursor-pointer"
                        onClick={() => isImage && setLightboxImage(fileUrl)}
                      >
                        {isImage ? (
                          <img
                            src={fileUrl}
                            alt={`Certificate ${idx + 1}`}
                            className="w-full h-32 object-cover"
                          />
                        ) : (
                          <a
                            href={fileUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-full h-32 flex items-center justify-center bg-muted"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div className="text-center">
                              <div className="text-3xl mb-1">📄</div>
                              <p className="text-xs text-muted-foreground font-medium truncate px-2">
                                {fileName.substring(0, 15)}
                              </p>
                            </div>
                          </a>
                        )}
                        {isImage && (
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                            <span className="text-white text-sm font-medium">
                              View
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  },
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Summary */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold text-foreground">Summary</h2>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-muted-foreground mb-1">
                  Total Specialties
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {staff.specialties.length}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">
                  Total Certifications
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {staff.certifications.length}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground mb-1">
                  Certificate Files
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {staff.certification_files.length}
                </p>
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div className="bg-card border border-border rounded-lg p-6 space-y-3 text-sm">
            <div className="flex items-start gap-3">
              <ClockIcon
                size={18}
                className="text-muted-foreground mt-0.5 flex-shrink-0"
              />
              <div>
                <p className="text-xs text-muted-foreground mb-1">Created</p>
                <p className="text-foreground">
                  {new Date(staff.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <ClockIcon
                size={18}
                className="text-muted-foreground mt-0.5 flex-shrink-0"
              />
              <div>
                <p className="text-xs text-muted-foreground mb-1">
                  Last Updated
                </p>
                <p className="text-foreground">
                  {new Date(staff.updatedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirm}
        onClose={() => setDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Delete Staff Member"
        description={`Are you sure you want to delete ${staff.firstName} ${staff.lastName}? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={deleteStaffMutation.isPending}
      />

      {/* Edit Staff Modal */}
      {staff && (
        <AddStaffModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSubmit={handleEditSubmit}
          isLoading={updateStaffMutation.isPending}
          initialData={staff}
        />
      )}

      {/* Profile Image Lightbox */}
      <ImageLightbox
        isOpen={!!lightboxImage}
        imageUrl={lightboxImage || ""}
        onClose={() => setLightboxImage(null)}
      />
    </div>
  );
}
