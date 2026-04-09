import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ArrowLeftIcon,
  EditIcon,
  TrashIcon,
  MailIcon,
} from "@/components/icons";
import { useCustomerProfile } from "@/hooks/useCustomerWithDetails";
import { useDeleteCustomer } from "@/hooks/useCustomers";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { EditCustomerModal } from "@/components/customers/EditCustomerModal";
import { useToast } from "@/components/ui/toast";
import { apiClient } from "@/lib/utils/api";
import { useState } from "react";

const APPOINTMENTS_PREVIEW_LIMIT = 5;

export default function CustomerDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [deleteConfirm, setDeleteConfirm] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [isSendingInvite, setIsSendingInvite] = useState(false);

  const { data: customer, isLoading } = useCustomerProfile(id || "");
  const { mutate: deleteCustomer, isPending: isDeleting } = useDeleteCustomer();

  const handleSendPortalInvitation = async () => {
    if (!id) return;

    setIsSendingInvite(true);
    try {
      await apiClient.post(
        `/public/customer-auth/resend-setup-invitation/${id}`,
      );
      showToast({
        title: "Invitation Sent",
        description:
          "Portal setup invitation has been sent to the customer's email.",
        variant: "success",
      });
    } catch (error: any) {
      showToast({
        title: "Failed to Send",
        description:
          error.response?.data?.detail || "Failed to send portal invitation.",
        variant: "error",
      });
    } finally {
      setIsSendingInvite(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-start gap-2 sm:gap-4">
            <Skeleton className="h-10 w-10 rounded" />
            <div className="min-w-0 flex-1">
              <Skeleton className="h-8 w-48" />
              <Skeleton className="h-4 w-32 mt-2" />
            </div>
          </div>
          <div className="flex gap-2 shrink-0">
            <Skeleton className="h-10 w-20" />
            <Skeleton className="h-10 w-20" />
          </div>
        </div>

        {/* Content Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6">
            {/* Contact Info Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-5 w-48" />
                  </div>
                ))}
              </div>
            </Card>

            {/* Preferences Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-5 w-full" />
                  </div>
                ))}
              </div>
            </Card>

            {/* History Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="border-b border-border pb-3 last:border-0"
                  >
                    <Skeleton className="h-4 w-40 mb-2" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4 sm:space-y-6">
            {/* Status Card */}
            <Card className="p-4 sm:p-6">
              <Skeleton className="h-6 w-24 mb-4" />
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-5 w-24" />
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (!isLoading && !customer) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-muted-foreground">Customer not found</div>
      </div>
    );
  }

  const handleDelete = () => {
    if (id) {
      deleteCustomer(id, {
        onSuccess: () => {
          showToast({
            title: "Customer Deleted",
            description:
              "Customer and all related data have been deleted successfully.",
            variant: "success",
          });
          navigate("/customers");
        },
        onError: (error: any) => {
          showToast({
            title: "Delete Failed",
            description:
              error.response?.data?.detail || "Failed to delete customer.",
            variant: "error",
          });
        },
      });
    }
  };

  const appointmentCount = customer!.history?.length || 0;
  const lastAppointment = customer!.history?.[0];

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-start gap-2 sm:gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/customers")}
            className="gap-2 cursor-pointer shrink-0"
          >
            <ArrowLeftIcon size={18} />
            <span className="hidden sm:inline">Back</span>
          </Button>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-foreground wrap-break-word">
              {customer!.firstName} {customer!.lastName}
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">
              Customer ID: {customer!.id}
            </p>
          </div>
        </div>
        <div className="flex gap-2 shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSendPortalInvitation}
            disabled={isSendingInvite}
            className="gap-2 cursor-pointer text-xs sm:text-sm"
            title="Send portal access invitation"
          >
            <MailIcon size={16} />
            <span className="hidden sm:inline">
              {isSendingInvite ? "Sending..." : "Send Portal Invite"}
            </span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setEditModalOpen(true)}
            className="gap-2 cursor-pointer text-xs sm:text-sm"
          >
            <EditIcon size={16} />
            <span className="hidden sm:inline">Edit</span>
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setDeleteConfirm(true)}
            className="gap-2 cursor-pointer text-xs sm:text-sm"
          >
            <TrashIcon size={16} />
            <span className="hidden sm:inline">Delete</span>
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-4 sm:space-y-6">
          {/* Contact Information */}
          <Card className="p-4 sm:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
              Contact Information
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Email
                </p>
                <p className="text-sm sm:text-base text-foreground mt-1 break-all">
                  {customer!.email}
                </p>
              </div>
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Phone
                </p>
                <p className="text-sm sm:text-base text-foreground mt-1">
                  {customer!.phone}
                </p>
              </div>
              {customer!.address && (
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                    Address
                  </p>
                  <p className="text-sm sm:text-base text-foreground mt-1">
                    {customer!.address}
                  </p>
                </div>
              )}
              {customer!.dateOfBirth && (
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                    Date of Birth
                  </p>
                  <p className="text-sm sm:text-base text-foreground mt-1">
                    {new Date(customer!.dateOfBirth).toLocaleDateString()}
                  </p>
                </div>
              )}
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Member Since
                </p>
                <p className="text-sm sm:text-base text-foreground mt-1">
                  {new Date(customer!.createdAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          </Card>

          {/* Preferences */}
          {customer!.preferences && (
            <Card className="p-4 sm:p-6">
              <h2 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
                Preferences
              </h2>
              <div className="space-y-4">
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                    Preferred Time Slots
                  </p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {customer!.preferences.preferred_time_slots?.length > 0 ? (
                      customer!.preferences.preferred_time_slots.map((slot) => (
                        <Badge key={slot} variant="secondary">
                          {slot.charAt(0).toUpperCase() + slot.slice(1)}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">
                        No preference
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                    Communication Methods
                  </p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {customer!.preferences.communication_methods?.length > 0 ? (
                      customer!.preferences.communication_methods.map(
                        (method) => (
                          <Badge key={method} variant="secondary">
                            {method.charAt(0).toUpperCase() + method.slice(1)}
                          </Badge>
                        ),
                      )
                    ) : (
                      <span className="text-sm text-muted-foreground">
                        No preference
                      </span>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                    Language
                  </p>
                  <p className="text-sm sm:text-base text-foreground mt-1">
                    {customer!.preferences.language || "Not specified"}
                  </p>
                </div>
                {customer!.preferences.notes && (
                  <div>
                    <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                      Notes
                    </p>
                    <p className="text-sm sm:text-base text-foreground mt-1">
                      {customer!.preferences.notes}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Appointment History */}
          {customer!.history && customer!.history.length > 0 && (
            <Card className="p-4 sm:p-6">
              <h2 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
                Appointment History ({customer!.history.length})
              </h2>
              <div className="space-y-3">
                {customer!.history
                  .slice(0, APPOINTMENTS_PREVIEW_LIMIT)
                  .map((appointment: any) => (
                    <div
                      key={appointment.id}
                      className="border-b border-border pb-3 last:border-0"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <p className="text-sm sm:text-base font-medium text-foreground">
                            {appointment.service_name}
                          </p>
                          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                            with {appointment.staff_name}
                          </p>
                        </div>
                        <p className="text-xs sm:text-sm text-muted-foreground shrink-0 whitespace-nowrap">
                          {new Date(
                            appointment.appointment_date,
                          ).toLocaleDateString()}
                        </p>
                      </div>
                      {appointment.rating > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-muted-foreground">
                            Rating: {appointment.rating}/5
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
              {customer!.history.length > APPOINTMENTS_PREVIEW_LIMIT && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/customers/${id}/appointments`)}
                  className="mt-4 w-full"
                >
                  View All Appointments ({customer!.history.length})
                </Button>
              )}
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4 sm:space-y-6">
          {/* Status Card */}
          <Card className="p-4 sm:p-6">
            <h3 className="text-base sm:text-lg font-semibold text-foreground mb-3 sm:mb-4">
              Status
            </h3>
            <div className="space-y-3 sm:space-y-4">
              <div>
                <p className="text-xs text-muted-foreground">Account Status</p>
                <Badge
                  variant={
                    customer!.status === "active" ? "default" : "secondary"
                  }
                  className="mt-1"
                >
                  {customer!.status.charAt(0).toUpperCase() +
                    customer!.status.slice(1)}
                </Badge>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">
                  Total Appointments
                </p>
                <p className="text-lg sm:text-xl font-semibold text-foreground mt-1">
                  {appointmentCount}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">
                  Last Appointment
                </p>
                <p className="text-sm sm:text-base text-foreground mt-1">
                  {lastAppointment
                    ? new Date(
                        lastAppointment.appointment_date,
                      ).toLocaleDateString()
                    : "No appointments"}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirm}
        onClose={() => setDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Delete Customer"
        description="Are you sure you want to delete this customer? This will permanently delete the customer and ALL their related data including appointments, invoices, payments, and history. This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="destructive"
        isLoading={isDeleting}
      />

      {/* Edit Customer Modal */}
      {editModalOpen && (
        <EditCustomerModal
          customerId={id || ""}
          open={editModalOpen}
          onOpenChange={setEditModalOpen}
          onSuccess={() => {
            setEditModalOpen(false);
          }}
        />
      )}
    </div>
  );
}
