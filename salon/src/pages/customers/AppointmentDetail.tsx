import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeftIcon } from "@/components/icons";
import { useCustomer } from "@/hooks/useCustomers";
import { useCustomerHistoryItem } from "@/hooks/useCustomerHistory";

export default function AppointmentDetail() {
  const { id: customerId, appointmentId } = useParams<{
    id: string;
    appointmentId: string;
  }>();
  const navigate = useNavigate();

  const { data: customer, isLoading: customerLoading } = useCustomer(
    customerId || "",
  );
  const { data: appointment, isLoading: appointmentLoading } =
    useCustomerHistoryItem(customerId || "", appointmentId || "");

  if (customerLoading || appointmentLoading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        <div className="flex items-center gap-2 sm:gap-4">
          <Skeleton className="h-10 w-10 rounded" />
          <Skeleton className="h-8 w-48" />
        </div>
        <Card className="p-4 sm:p-6">
          <div className="space-y-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-5 w-48" />
              </div>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  if (!customer || !appointment) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-muted-foreground">Appointment not found</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 sm:gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/customers/${customerId}/appointments`)}
          className="gap-2 cursor-pointer"
        >
          <ArrowLeftIcon size={18} />
          <span className="hidden sm:inline">Back</span>
        </Button>
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-foreground">
            Appointment Details
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            {customer.firstName} {customer.lastName}
          </p>
        </div>
      </div>

      {/* Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Main Details */}
        <Card className="p-4 sm:p-6">
          <h2 className="text-base sm:text-lg font-semibold text-foreground mb-4">
            Appointment Information
          </h2>
          <div className="space-y-4">
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                Service
              </p>
              <p className="text-sm sm:text-base text-foreground mt-1">
                {appointment.service_name}
              </p>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                Staff Member
              </p>
              <p className="text-sm sm:text-base text-foreground mt-1">
                {appointment.staff_name}
              </p>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                Date
              </p>
              <p className="text-sm sm:text-base text-foreground mt-1">
                {new Date(appointment.appointment_date).toLocaleDateString(
                  "en-US",
                  {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  },
                )}
              </p>
            </div>
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                Time
              </p>
              <p className="text-sm sm:text-base text-foreground mt-1">
                {appointment.appointment_time}
              </p>
            </div>
          </div>
        </Card>

        {/* Additional Details */}
        <Card className="p-4 sm:p-6">
          <h2 className="text-base sm:text-lg font-semibold text-foreground mb-4">
            Additional Information
          </h2>
          <div className="space-y-4">
            {appointment.notes && (
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Notes
                </p>
                <p className="text-sm sm:text-base text-foreground mt-1">
                  {appointment.notes}
                </p>
              </div>
            )}
            {appointment.rating > 0 && (
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Rating
                </p>
                <div className="mt-1">
                  <Badge variant="secondary">{appointment.rating}/5 ⭐</Badge>
                </div>
              </div>
            )}
            {appointment.feedback && (
              <div>
                <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                  Feedback
                </p>
                <p className="text-sm sm:text-base text-foreground mt-1">
                  {appointment.feedback}
                </p>
              </div>
            )}
            <div>
              <p className="text-xs sm:text-sm text-muted-foreground font-medium">
                Appointment ID
              </p>
              <p className="text-xs sm:text-sm text-muted-foreground mt-1 font-mono">
                {appointment.appointment_id}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
