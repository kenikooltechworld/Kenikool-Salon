import { useState } from "react";
import { useAppointments } from "@/hooks/useAppointments";
import { useCheckIn, useQueuePosition } from "@/hooks/useWaitingRoom";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";
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
  const { data: queuePosition } = useQueuePosition(selectedAppointmentId);

  const selectedAppointment = appointments.find(
    (a) => a.id === selectedAppointmentId,
  );

  const handleCheckIn = () => {
    if (!selectedAppointmentId) {
      alert("Please select an appointment");
      return;
    }

    checkIn.mutate(selectedAppointmentId, {
      onSuccess: () => {
        setSuccessMessage(
          `Successfully checked in! Your position in queue: ${queuePosition?.position || "N/A"}`,
        );
        setShowSuccess(true);
        setSelectedAppointmentId("");
        setTimeout(() => setShowSuccess(false), 5000);
      },
    });
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Check In
      </h2>

      {showSuccess && (
        <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-800 dark:text-green-200">
            {successMessage}
          </p>
        </div>
      )}

      <div className="space-y-4">
        {/* Appointment Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Your Appointment
          </label>
          <select
            value={selectedAppointmentId}
            onChange={(e) => setSelectedAppointmentId(e.target.value)}
            disabled={appointmentsLoading}
            className={cn(
              "w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              "focus:outline-none focus:ring-2 focus:ring-blue-500",
              appointmentsLoading && "opacity-50 cursor-not-allowed",
            )}
          >
            <option value="">Choose an appointment...</option>
            {appointments.map((appointment) => (
              <option key={appointment.id} value={appointment.id}>
                {new Date(appointment.start_time).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}{" "}
                - {appointment.service_name}
              </option>
            ))}
          </select>
        </div>

        {/* Appointment Details */}
        {selectedAppointment && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              Appointment Details
            </h3>
            <div className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
              <p>
                <span className="font-medium">Service:</span>{" "}
                {selectedAppointment.service_name}
              </p>
              <p>
                <span className="font-medium">Time:</span>{" "}
                {new Date(selectedAppointment.start_time).toLocaleString()}
              </p>
              {selectedAppointment.staff_name && (
                <p>
                  <span className="font-medium">Staff:</span>{" "}
                  {selectedAppointment.staff_name}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Info Message */}
        <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
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
              ? "bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
              : "bg-green-600 text-white hover:bg-green-700",
          )}
        >
          {checkIn.isPending ? "Checking In..." : "Check In"}
        </button>

        {/* Error Message */}
        {checkIn.isError && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800 dark:text-red-200">
              Failed to check in. Please try again.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
