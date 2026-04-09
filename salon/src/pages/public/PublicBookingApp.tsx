/**
 * Public Booking App - Main entry point for public booking interface
 * Accessible via salon's unique subdomain (e.g., acme-salon.kenikool.com)
 */

import { useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Card, Button, Spinner, ToastProvider } from "@/components/ui";
import ServiceSelector from "@/components/public/ServiceSelector";
import StaffSelector from "@/components/public/StaffSelector";
import TimeSlotSelector from "@/components/public/TimeSlotSelector";
import BookingForm from "@/components/public/BookingForm";
import BookingConfirmation from "@/components/public/BookingConfirmation";
import PublicHeroSection from "@/components/public/PublicHeroSection";
import PublicTestimonialsSection from "@/components/public/PublicTestimonialsSection";
import PublicFAQSection from "@/components/public/PublicFAQSection";
import PublicBookingStatistics from "@/components/public/PublicBookingStatistics";
import ServiceRecommendations from "@/components/public/ServiceRecommendations";
import InstallPWAPrompt from "@/components/public/InstallPWAPrompt";
import PWAUpdatePrompt from "@/components/public/PWAUpdatePrompt";
import LiveBookingNotifications from "@/components/public/LiveBookingNotifications";
import { useCreatePublicBooking } from "@/hooks/usePublicBooking";
import {
  useIsCustomerAuthenticated,
  useCustomerProfile,
} from "@/hooks/useCustomerAuth";
import { apiClient } from "@/lib/utils/api";
import { UserIcon, LogInIcon } from "@/components/icons";

type BookingStep = "service" | "staff" | "time" | "form" | "confirmation";

interface BookingData {
  service_id: string;
  staff_id: string;
  booking_date: string;
  booking_time: string;
  duration_minutes: number;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  notes?: string;
}

interface SalonInfo {
  id: string;
  name: string;
  description: string;
  email: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
}

export default function PublicBookingApp() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<BookingStep>("service");
  const [bookingData, setBookingData] = useState<Partial<BookingData>>({});
  const [confirmationData, setConfirmationData] = useState<any>(null);
  const bookingFormRef = useRef<HTMLDivElement>(null);

  const isAuthenticated = useIsCustomerAuthenticated();
  const { data: customerProfile } = useCustomerProfile();

  // Fetch salon info from subdomain
  const { data: salonInfo, isLoading: salonLoading } = useQuery({
    queryKey: ["salon-info"],
    queryFn: async () => {
      const { data } = await apiClient.get<SalonInfo>("/public/salon-info");
      return data;
    },
  });

  const createBooking = useCreatePublicBooking();

  if (salonLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  if (!salonInfo) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="p-8 text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">
            Salon Not Found
          </h1>
          <p className="text-gray-600">
            The salon you're looking for is not available.
          </p>
        </Card>
      </div>
    );
  }

  const handleBookNowClick = () => {
    bookingFormRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleServiceSelect = (serviceId: string, durationMinutes: number) => {
    setBookingData((prev) => ({
      ...prev,
      service_id: serviceId,
      duration_minutes: durationMinutes,
    }));
    setCurrentStep("staff");
  };

  const handleStaffSelect = (staffId: string) => {
    setBookingData((prev) => ({
      ...prev,
      staff_id: staffId,
    }));
    setCurrentStep("time");
  };

  const handleTimeSelect = (bookingDate: string, bookingTime: string) => {
    setBookingData((prev) => ({
      ...prev,
      booking_date: bookingDate,
      booking_time: bookingTime,
    }));
    setCurrentStep("form");
  };

  const handleFormSubmit = async (formData: {
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    notes?: string;
    paymentOption: "now" | "later";
  }) => {
    try {
      const response = await createBooking.mutateAsync({
        service_id: bookingData.service_id!,
        staff_id: bookingData.staff_id!,
        booking_date: bookingData.booking_date!,
        booking_time: bookingData.booking_time!,
        customer_name: formData.customerName,
        customer_email: formData.customerEmail,
        customer_phone: formData.customerPhone,
        notes: formData.notes,
        payment_option: formData.paymentOption,
      });

      setConfirmationData(response);
      setCurrentStep("confirmation");
    } catch (error) {
      console.error("Booking failed:", error);
      throw error;
    }
  };

  const handleBackClick = () => {
    const steps: BookingStep[] = ["service", "staff", "time", "form"];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  return (
    <ToastProvider>
      {/* PWA Install Prompt */}
      <InstallPWAPrompt delay={30000} position="bottom" />

      {/* PWA Update Prompt */}
      <PWAUpdatePrompt />

      {/* Live Booking Notifications */}
      <LiveBookingNotifications />

      <div
        className="min-h-screen bg-linear-to-br from-gray-50 to-gray-100"
        style={
          {
            "--primary-color": salonInfo?.primary_color || "#3B82F6",
            "--secondary-color": salonInfo?.secondary_color || "#1F2937",
          } as React.CSSProperties
        }
      >
        {/* Top Navigation Bar */}
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {salonInfo?.logo_url && (
                  <img
                    src={salonInfo.logo_url}
                    alt={salonInfo.name}
                    className="h-10 w-auto"
                  />
                )}
                <h1 className="text-xl font-bold">{salonInfo?.name}</h1>
              </div>
              <div className="flex items-center gap-2">
                {isAuthenticated && customerProfile ? (
                  <>
                    <Button
                      variant="ghost"
                      onClick={() => navigate("/public/portal")}
                    >
                      <UserIcon size={16} className="mr-2" />
                      {customerProfile.first_name}
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="ghost"
                      onClick={() => navigate("/public/login")}
                    >
                      <LogInIcon size={16} className="mr-2" />
                      Sign In
                    </Button>
                    <Button onClick={() => navigate("/public/register")}>
                      Create Account
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <PublicHeroSection
          salonName={salonInfo.name}
          salonDescription={salonInfo.description}
          salonLogo={salonInfo.logo_url}
          primaryColor={salonInfo.primary_color}
          secondaryColor={salonInfo.secondary_color}
          onBookNowClick={handleBookNowClick}
        />

        {/* Testimonials Section */}
        <PublicTestimonialsSection />

        {/* Booking Form Section */}
        <div ref={bookingFormRef} className="py-8 px-4 sm:px-6">
          <div className="max-w-2xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-2">Book Your Appointment</h2>
              <p className="text-gray-600">
                Follow the steps below to reserve your spot
              </p>
            </div>

            {/* Progress Indicator */}
            <div className="mb-8">
              <div className="flex justify-between items-center">
                {["service", "staff", "time", "form", "confirmation"].map(
                  (step, index) => (
                    <div key={step} className="flex items-center flex-1">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${
                          [
                            "service",
                            "staff",
                            "time",
                            "form",
                            "confirmation",
                          ].indexOf(currentStep) >= index
                            ? "bg-blue-600 text-white"
                            : "bg-gray-300 text-gray-600"
                        }`}
                      >
                        {index + 1}
                      </div>
                      {index < 4 && (
                        <div
                          className={`flex-1 h-1 mx-2 ${
                            [
                              "service",
                              "staff",
                              "time",
                              "form",
                              "confirmation",
                            ].indexOf(currentStep) > index
                              ? "bg-blue-600"
                              : "bg-gray-300"
                          }`}
                        />
                      )}
                    </div>
                  ),
                )}
              </div>
            </div>

            {/* Content */}
            <Card className="p-8">
              {currentStep === "service" && (
                <>
                  {/* Show recommendations for authenticated customers */}
                  <ServiceRecommendations
                    limit={3}
                    onServiceSelect={(serviceId) =>
                      handleServiceSelect(serviceId, 0)
                    }
                  />

                  <div className="mt-8">
                    <h3 className="text-lg font-semibold mb-4">
                      Or Browse All Services
                    </h3>
                    <ServiceSelector onSelect={handleServiceSelect} />
                  </div>
                </>
              )}

              {currentStep === "staff" && bookingData.service_id && (
                <>
                  <Button
                    variant="ghost"
                    onClick={handleBackClick}
                    className="mb-4"
                  >
                    ← Back
                  </Button>
                  <StaffSelector
                    serviceId={bookingData.service_id}
                    onSelect={handleStaffSelect}
                  />
                </>
              )}

              {currentStep === "time" &&
                bookingData.service_id &&
                bookingData.staff_id && (
                  <>
                    <Button
                      variant="ghost"
                      onClick={handleBackClick}
                      className="mb-4"
                    >
                      ← Back
                    </Button>
                    <TimeSlotSelector
                      serviceId={bookingData.service_id}
                      staffId={bookingData.staff_id}
                      onSelect={handleTimeSelect}
                    />
                  </>
                )}

              {currentStep === "form" && bookingData.service_id && (
                <>
                  <Button
                    variant="ghost"
                    onClick={handleBackClick}
                    className="mb-4"
                  >
                    ← Back
                  </Button>
                  <BookingForm onSubmit={handleFormSubmit} />
                </>
              )}

              {currentStep === "confirmation" && confirmationData && (
                <BookingConfirmation booking={confirmationData} />
              )}
            </Card>

            {/* Contact Footer */}
            <div className="mt-8 text-center text-sm text-gray-600">
              <p>
                Questions? Contact us at{" "}
                <a
                  href={`mailto:${salonInfo?.email}`}
                  className="text-blue-600 hover:underline"
                >
                  {salonInfo?.email}
                </a>
              </p>
            </div>
          </div>
        </div>

        {/* Statistics Section */}
        <div className="py-8 px-4 sm:px-6 bg-white">
          <div className="max-w-7xl mx-auto">
            <PublicBookingStatistics />
          </div>
        </div>

        {/* FAQ Section */}
        <PublicFAQSection />

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-gray-400">
              © {new Date().getFullYear()} {salonInfo?.name}. All rights
              reserved.
            </p>
          </div>
        </footer>
      </div>
    </ToastProvider>
  );
}
