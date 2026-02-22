import { useState, lazy, Suspense } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  ArrowLeftIcon,
  PhoneIcon,
  MailIcon,
  CalendarIcon,
  DollarIcon,
  AlertTriangleIcon,
  EditIcon,
  PlusIcon,
} from "@/components/icons";
import { useClient } from "@/lib/api/hooks/useClients";
import {
  ClientFormModal,
  ClientAnalyticsCard,
  UpcomingAppointments,
  AppointmentMetrics,
  ClientFinancialSummary,
  CommunicationTimeline,
  ClientReviewsSection,
  ClientRelationshipsSection,
  ClientMembershipSection,
  ClientPhotoGallery,
  ClientActivityTimeline,
  BirthdayWidget,
} from "@/components/clients";
import { BookingWizard } from "@/components/booking";
import { Booking } from "@/lib/api/types";
import { useGetBalance, useGetHistory } from "@/lib/api/hooks/useLoyalty";
import { LoyaltyBalance, LoyaltyHistory } from "@/components/loyalty";
import { ClientPreferences } from "@/components/clients/client-preferences";

// Lazy load components
const ServiceHistoryTimeline = lazy(() =>
  import("@/components/clients/service-history-timeline").then((mod) => ({
    default: mod.ServiceHistoryTimeline,
  })),
);

const DocumentsSection = lazy(() =>
  import("@/components/clients/documents-section").then((mod) => ({
    default: mod.DocumentsSection,
  })),
);

const PrivacyManagementSection = lazy(() =>
  import("@/components/clients/privacy-management-section").then((mod) => ({
    default: mod.PrivacyManagementSection,
  })),
);

const NotificationSettingsPage = lazy(() =>
  import("@/components/clients/notification-settings-page").then((mod) => ({
    default: mod.NotificationSettingsPage,
  })),
);

export default function ClientProfilePage() {
  const navigate = useNavigate();
  const params = useParams();
  const clientId = params.id as string;
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [bookingToReschedule, setBookingToReschedule] =
    useState<Booking | null>(null);

  // Fetch client details using REST API
  const { data: client, isLoading, error, refetch } = useClient(clientId);

  // Fetch loyalty information
  const { data: loyaltyBalance } = useGetBalance(clientId);
  const { data: loyaltyHistory } = useGetHistory(clientId);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (error || !client) {
    return (
      <div className="space-y-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading client</h3>
            <p className="text-sm">{error?.message || "Client not found"}</p>
          </div>
        </Alert>
        <Button variant="outline" onClick={() => navigate(-1)}>
          <ArrowLeftIcon size={20} />
          Go Back
        </Button>
      </div>
    );
  }

  const getSegmentColor = (segment: string) => {
    switch (segment) {
      case "vip":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200";
      case "regular":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "inactive":
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
      case "new":
      default:
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    }
  };

  const handleBookAppointment = () => {
    setBookingToReschedule(null);
    setIsBookingModalOpen(true);
  };

  const handleReschedule = (booking: Booking) => {
    setBookingToReschedule(booking);
    setIsBookingModalOpen(true);
  };

  const handleBookingSuccess = () => {
    refetch();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeftIcon size={20} />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-foreground">
                {client.name}
              </h1>
              <Badge className={getSegmentColor(client.segment)}>
                {client.segment}
              </Badge>
            </div>
            <p className="text-muted-foreground">Client Profile</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => setIsEditModalOpen(true)}>
            <EditIcon size={20} />
            Edit
          </Button>
          <Button onClick={handleBookAppointment}>
            <PlusIcon size={20} />
            Book Appointment
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Client Info */}
        <div className="lg:col-span-1 space-y-6">
          {/* Birthday Widget */}
          <BirthdayWidget clientId={clientId} />

          {/* Contact Information */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Contact Information
            </h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <PhoneIcon size={20} className="text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Phone</p>
                  <p className="text-foreground">{client.phone}</p>
                </div>
              </div>
              {client.email && (
                <div className="flex items-center gap-3">
                  <MailIcon size={20} className="text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p className="text-foreground">{client.email}</p>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Stats */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Statistics
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <CalendarIcon size={20} className="text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Total Visits
                    </p>
                    <p className="text-xl font-bold text-foreground">
                      {client.total_visits}
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <DollarIcon size={20} className="text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Total Spent</p>
                    <p className="text-xl font-bold text-foreground">
                      ₦{client.total_spent.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <CalendarIcon size={20} className="text-primary" />
                  <div>
                    <p className="text-sm text-muted-foreground">Last Visit</p>
                    <p className="text-foreground">
                      {client.last_visit_date
                        ? new Date(client.last_visit_date).toLocaleDateString()
                        : "Never"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Notes */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Notes
            </h2>
            {client.notes ? (
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {client.notes}
              </p>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                No notes added yet
              </p>
            )}
          </Card>

          {/* Loyalty Balance */}
          {loyaltyBalance && <LoyaltyBalance balance={loyaltyBalance} />}

          {/* Client Preferences */}
          <ClientPreferences
            clientId={clientId}
            preferences={client.preferences}
            onUpdate={refetch}
          />
        </div>

        {/* Right Column - Service History & Loyalty */}
        <div className="lg:col-span-2 space-y-6">
          {/* Photo Gallery */}
          <Suspense fallback={<Spinner />}>
            <ClientPhotoGallery clientId={clientId} />
          </Suspense>

          {/* Upcoming Appointments */}
          <UpcomingAppointments
            clientId={clientId}
            onReschedule={handleReschedule}
          />

          {/* Membership Section */}
          <ClientMembershipSection clientId={clientId} />

          {/* Appointment Metrics */}
          <AppointmentMetrics clientId={clientId} />

          {/* Client Analytics */}
          <ClientAnalyticsCard clientId={clientId} />

          {/* Financial Summary */}
          <ClientFinancialSummary clientId={clientId} />

          {/* Communication History */}
          <CommunicationTimeline clientId={clientId} />

          {/* Activity Timeline */}
          <Suspense fallback={<Spinner />}>
            <ClientActivityTimeline clientId={clientId} />
          </Suspense>

          {/* Service History */}
          <Card className="p-6">
            <Suspense fallback={<Spinner />}>
              <ServiceHistoryTimeline clientId={clientId} />
            </Suspense>
          </Card>

          {/* Loyalty History */}
          {loyaltyHistory && <LoyaltyHistory history={loyaltyHistory} />}

          {/* Client Reviews Section */}
          <ClientReviewsSection clientId={clientId} />

          {/* Client Relationships Section */}
          <ClientRelationshipsSection clientId={clientId} />

          {/* Documents Section */}
          <Suspense fallback={<Spinner />}>
            <DocumentsSection clientId={clientId} />
          </Suspense>

          {/* Privacy Management Section */}
          <Suspense fallback={<Spinner />}>
            <PrivacyManagementSection clientId={clientId} />
          </Suspense>

          {/* Notification Settings */}
          <Suspense fallback={<Spinner />}>
            <NotificationSettingsPage clientId={clientId} />
          </Suspense>
        </div>
      </div>

      {/* Edit Client Modal */}
      <ClientFormModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSuccess={refetch}
        client={client}
      />

      {/* Booking Modal */}
      <BookingWizard
        isOpen={isBookingModalOpen}
        onClose={() => {
          setIsBookingModalOpen(false);
          setBookingToReschedule(null);
        }}
        onSuccess={handleBookingSuccess}
        initialDate={
          bookingToReschedule
            ? new Date(bookingToReschedule.booking_date)
            : undefined
        }
      />
    </div>
  );
}
