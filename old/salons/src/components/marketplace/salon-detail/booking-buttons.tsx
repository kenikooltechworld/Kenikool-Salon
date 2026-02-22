import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/hooks/useAuth";
import { useNavigate } from "react-router-dom";
import { BookingModal } from "@/components/marketplace/booking";

interface Salon {
  id: string;
  name: string;
}

interface BookingButtonsProps {
  salon: Salon;
}

export function BookingButtons({ salon }: BookingButtonsProps) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);

  const handleLoginBooking = () => {
    if (!user) {
      navigate("/login", { state: { from: `/marketplace/salon/${salon.id}` } });
    } else {
      setIsBookingModalOpen(true);
    }
  };

  const handleGuestBooking = () => {
    setIsBookingModalOpen(true);
  };

  const containerVariants = {
    hidden: { opacity: 0, x: 20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 }
    }
  };

  return (
    <>
      <motion.div
        className="space-y-4 p-6 bg-[var(--muted)] rounded-2xl sticky top-24"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Salon Name */}
        <motion.h3
          className="text-xl font-bold text-[var(--foreground)]"
          variants={itemVariants}
        >
          {salon.name}
        </motion.h3>

        {/* Booking Options */}
        <motion.div className="space-y-3" variants={containerVariants}>
          {/* Login Booking */}
          <motion.div variants={itemVariants}>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                onClick={handleLoginBooking}
                className="w-full bg-[var(--primary)] hover:bg-[var(--primary-dark)] text-white"
                size="lg"
              >
                {user ? "Book Appointment" : "Sign In & Book"}
              </Button>
            </motion.div>
            <p className="text-xs text-[var(--muted-foreground)] mt-2 text-center">
              {user ? "Book with your account" : "Sign in to your account"}
            </p>
          </motion.div>

          {/* Divider */}
          <motion.div
            className="relative"
            variants={itemVariants}
          >
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[var(--border)]"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-[var(--muted)] text-[var(--muted-foreground)]">
                or
              </span>
            </div>
          </motion.div>

          {/* Guest Booking */}
          <motion.div variants={itemVariants}>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                onClick={handleGuestBooking}
                variant="outline"
                className="w-full"
                size="lg"
              >
                Book as Guest
              </Button>
            </motion.div>
            <p className="text-xs text-[var(--muted-foreground)] mt-2 text-center">
              No account needed
            </p>
          </motion.div>
        </motion.div>

        {/* Info Box */}
        <motion.div
          className="p-3 bg-blue-50 border border-blue-200 rounded-lg"
          variants={itemVariants}
        >
          <p className="text-xs text-blue-700">
            💡 <strong>Tip:</strong> Create an account to save your bookings and preferences.
          </p>
        </motion.div>

        {/* Contact Info */}
        <motion.div
          className="pt-4 border-t border-[var(--border)] space-y-2"
          variants={containerVariants}
        >
          <motion.p
            className="text-sm text-[var(--muted-foreground)]"
            variants={itemVariants}
          >
            <strong>Questions?</strong>
          </motion.p>
          <motion.a
            href="tel:+1234567890"
            className="block text-sm text-[var(--primary)] hover:underline"
            variants={itemVariants}
            whileHover={{ x: 5 }}
          >
            📞 Call us
          </motion.a>
          <motion.a
            href="https://wa.me/1234567890"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-sm text-[var(--primary)] hover:underline"
            variants={itemVariants}
            whileHover={{ x: 5 }}
          >
            💬 WhatsApp us
          </motion.a>
        </motion.div>
      </motion.div>

      {/* Booking Modal */}
      <BookingModal
        isOpen={isBookingModalOpen}
        onClose={() => setIsBookingModalOpen(false)}
        salonId={salon.id}
        salonName={salon.name}
      />
    </>
  );
}
