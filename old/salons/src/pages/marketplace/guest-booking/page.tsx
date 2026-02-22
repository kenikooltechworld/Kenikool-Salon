import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { MagicLinkAuth } from "@/components/marketplace/guest/magic-link-auth";
import { BookingManagement } from "@/components/marketplace/guest/booking-management";
import { useGuestBooking } from "@/lib/api/hooks/useMarketplaceQueries";

type Step = "auth" | "management";

export default function GuestBookingPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<Step>("auth");
  const [guestEmail, setGuestEmail] = useState<string | null>(null);
  const [magicToken, setMagicToken] = useState<string | null>(null);

  // Get magic token from URL if present
  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      setMagicToken(token);
      setCurrentStep("management");
    }
  }, [searchParams]);

  const { data: bookingData, isLoading: isLoadingBooking } = useGuestBooking(
    magicToken || ""
  );

  const handleAuthSuccess = (email: string, token: string) => {
    setGuestEmail(email);
    setMagicToken(token);
    setCurrentStep("management");
  };

  const handleBackToAuth = () => {
    setGuestEmail(null);
    setMagicToken(null);
    setCurrentStep("auth");
  };

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-br from-[var(--background)] to-[var(--muted)] py-12 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="text-4xl font-bold text-[var(--foreground)] mb-2">
            Manage Your Booking
          </h1>
          <p className="text-[var(--muted-foreground)]">
            View, reschedule, or cancel your appointment
          </p>
        </motion.div>

        {/* Content */}
        <motion.div
          className="bg-white rounded-2xl shadow-lg p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {currentStep === "auth" ? (
            <MagicLinkAuth onSuccess={handleAuthSuccess} />
          ) : (
            <BookingManagement
              magicToken={magicToken || ""}
              guestEmail={guestEmail || ""}
              onBack={handleBackToAuth}
            />
          )}
        </motion.div>

        {/* Footer */}
        <motion.div
          className="text-center mt-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <p className="text-sm text-[var(--muted-foreground)]">
            Need help?{" "}
            <a
              href="mailto:support@salon.com"
              className="text-[var(--primary)] hover:underline font-medium"
            >
              Contact support
            </a>
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
