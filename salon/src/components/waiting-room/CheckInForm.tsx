import { useState, useEffect } from "react";
import { useAppointments } from "@/hooks/useAppointments";
import { useCheckIn, useQueuePosition } from "@/hooks/useWaitingRoom";
import { AlertCircle, CheckCircle } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

export default function CheckInForm() {
  const [selectedAppointmentId, setSelectedAppointmentId] =
    useState<string>("");
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const { data: appointments = [], isLoading: appointmentsLoading } =
    useAppointments({
      status: "confirmed",
    });
  const checkIn = useCheckIn();

  const selectedAppointment = appointments.find(
    (a) => a.id === selectedAppointmentId,
  );

  const customerId = selectedAppointment?.customerId || "";
  const { data: queuePosition } = useQueuePosition(customerId);

  useEffect(() => {
    if (checkIn.isSuccess && checkIn.data) {
      setSuccessMessage(
        `Successfully checked in! Your position in queue: ${checkIn.data.position || queuePosition?.position || "N/A"}`,
      );
      setShowSuccess(true);
      setSelectedAppointmentId("");
      setTimeout(() => setShowSuccess(false), 5000);
    }
  }, [checkIn.isSuccess, checkIn.data, queuePosition?.position]);

  const handleCheckIn = () => {
    if (!selectedAppointmentId || !selectedAppointment) {
      alert("Please select an appointment");
      return;
    }

    checkIn.mutate({
      appointmentId: selectedAppointmentId,
      customerId: selectedAppointment.customerId,
      customerName: "",
      customerPhone: "",
      serviceId: selectedAppointment.serviceId,
      serviceName: "",
      staffId: selectedAppointment.staffId,
      staffName: "",
      estimatedWaitTime: undefined,
    });
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-background rounded-lg border border-border">
      <h2 className="text-2xl font-bold text-foreground mb-6">
        Check In
      </h2>

      {showSuccess && (
        <div className="mb-4 p-4 bg-success/10 border border-success/20 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
          <p className="text-sm text-success-foreground">
            {successMessage}
          </p>
        </div>
      )}

      <div className="space-y-4">
        {/* Appointment Selection */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Select Your Appointment
          </label>
          <select
            value={selectedAppointmentId}
            onChange={(e) => setSelectedAppointmentId(e.target.value)}
            disabled={appointmentsLoading}
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground",
              "focus:outline-none focus:ring-2 focus:ring-primary",
              appointmentsLoading && "opacity-50 cursor-not-allowed",
            )}
          >
            <option value="">Choose an appointment...</option>
            {appointments.map((appointment) => (
              <option key={appointment.id} value={appointment.id}>
                {new Date(appointment.startTime).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}{" "}
                - Service ID: {appointment.serviceId}
              </option>
            ))}
          </select>
        </div>

        {/* Appointment Details */}
        {selectedAppointment && (
          <div className="p-4 bg-info/10 rounded-lg border border-info/20">
            <h3 className="font-semibold text-foreground mb-2">
              Appointment Details
            </h3>
            <div className="space-y-1 text-sm text-muted-foreground">
              <p>
                <span className="font-medium">Service:</span> Service ID:{" "}
                {selectedAppointment.serviceId}
              </p>
              <p>
                <span className="font-medium">Time:</span>{" "}
                {new Date(selectedAppointment.startTime).toLocaleString()}
              </p>
              {selectedAppointment.staffId && (
                <p>
                  <span className="font-medium">Staff ID:</span>{" "}
                  {selectedAppointment.staffId}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Info Message */}
        <div className="p-4 bg-warning/10 border border-warning/20 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
          <p className="text-sm text-warning-foreground">
            Please check in within 15 minutes of your appointment time.
          </p>
        </div>

        {/* Check In Button */}
        <button
          onClick={handleCheckIn}
          disabled={!selectedAppointmentId || checkIn.isPending}
          className={cn(
            "w-full px-4 py-3 rounded-lg font-semibold transition-colors",
            !selectedAppointmentId || checkIn.isPending
              ? "bg-muted text-muted-foreground cursor-not-allowed"
              : "bg-success text-success-foreground hover:bg-success/90",
          )}
        >
          {checkIn.isPending ? "Checking In..." : "Check In"}
        </button>

        {/* Error Message */}
        {checkIn.isError && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
            <p className="text-sm text-destructive-foreground">
              Failed to check in. Please try again.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
