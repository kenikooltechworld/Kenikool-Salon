import { motion } from "framer-motion";
import { CheckCircleIcon, CopyIcon, DownloadIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface BookingConfirmationProps {
  reference: string;
  salon: string;
  service: string;
  dateTime: {
    date: string;
    time: string;
  };
}

export function BookingConfirmation({
  reference,
  salon,
  service,
  dateTime,
}: BookingConfirmationProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyReference = () => {
    navigator.clipboard.writeText(reference);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadReceipt = () => {
    // TODO: Implement receipt download
    console.log("Download receipt for:", reference);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6 text-center">
      {/* Success Icon */}
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 20 }}
        className="flex justify-center"
      >
        <div className="relative">
          <motion.div
            className="absolute inset-0 bg-green-400 rounded-full"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            style={{ opacity: 0.2 }}
          />
          <CheckCircleIcon
            size={80}
            className="text-green-500 fill-green-500"
          />
        </div>
      </motion.div>

      {/* Success Message */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-3xl font-bold text-[var(--foreground)] mb-2">
          Booking Confirmed!
        </h2>
        <p className="text-[var(--muted-foreground)]">
          Your appointment has been successfully booked.
        </p>
      </motion.div>

      {/* Booking Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-[var(--muted)] p-6 rounded-lg space-y-4"
      >
        <div className="text-left">
          <p className="text-sm text-[var(--muted-foreground)] mb-1">
            Booking Reference
          </p>
          <div className="flex items-center gap-2">
            <p className="font-mono font-bold text-lg text-[var(--foreground)]">
              {reference}
            </p>
            <motion.button
              onClick={handleCopyReference}
              className="p-2 hover:bg-[var(--border)] rounded-lg transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              title="Copy reference"
            >
              <CopyIcon
                size={18}
                className={copied ? "text-green-500" : "text-[var(--muted-foreground)]"}
              />
            </motion.button>
          </div>
        </div>

        <div className="border-t border-[var(--border)] pt-4 space-y-3">
          <div className="text-left">
            <p className="text-sm text-[var(--muted-foreground)]">Salon</p>
            <p className="font-semibold text-[var(--foreground)]">{salon}</p>
          </div>

          <div className="text-left">
            <p className="text-sm text-[var(--muted-foreground)]">Service</p>
            <p className="font-semibold text-[var(--foreground)]">{service}</p>
          </div>

          <div className="text-left">
            <p className="text-sm text-[var(--muted-foreground)]">Date & Time</p>
            <p className="font-semibold text-[var(--foreground)]">
              {formatDate(dateTime.date)} at {dateTime.time}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Next Steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-left"
      >
        <h3 className="font-semibold text-blue-900 mb-3">What's Next?</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start gap-2">
            <span className="font-bold">1.</span>
            <span>
              Check your email for a confirmation message with booking details
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold">2.</span>
            <span>
              You'll receive an SMS reminder 24 hours before your appointment
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold">3.</span>
            <span>
              Arrive 10 minutes early to complete check-in at the salon
            </span>
          </li>
        </ul>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex flex-col gap-3"
      >
        <Button
          onClick={handleDownloadReceipt}
          variant="outline"
          className="w-full flex items-center justify-center gap-2"
        >
          <DownloadIcon size={18} />
          Download Receipt
        </Button>

        <Button className="w-full bg-[var(--primary)] hover:bg-[var(--primary-dark)] text-white">
          View My Bookings
        </Button>
      </motion.div>

      {/* Contact Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="text-sm text-[var(--muted-foreground)]"
      >
        <p>
          Need help? Contact us at{" "}
          <a href="tel:+2341234567890" className="text-[var(--primary)] hover:underline">
            +234 (0) 123 456 7890
          </a>{" "}
          or{" "}
          <a href="mailto:support@salon.com" className="text-[var(--primary)] hover:underline">
            support@salon.com
          </a>
        </p>
      </motion.div>
    </div>
  );
}
