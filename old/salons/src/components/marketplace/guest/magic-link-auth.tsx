import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { MailIcon, CheckCircleIcon } from "@/components/icons";
import { useGenerateMagicLink } from "@/lib/api/hooks/useMarketplaceQueries";

interface MagicLinkAuthProps {
  onSuccess: (email: string, token: string) => void;
}

export function MagicLinkAuth({ onSuccess }: MagicLinkAuthProps) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const generateMagicLinkMutation = useGenerateMagicLink();
  const isLoading = generateMagicLinkMutation.isPending;

  const validateEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email.trim()) {
      setError("Email is required");
      return;
    }

    if (!validateEmail(email)) {
      setError("Please enter a valid email address");
      return;
    }

    try {
      const response = await generateMagicLinkMutation.mutateAsync({ email });
      setIsSubmitted(true);
      // In a real app, the token would be sent via email
      // For now, we'll simulate receiving it
      setTimeout(() => {
        onSuccess(email, response.token);
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to generate magic link"
      );
    }
  };

  if (isSubmitted) {
    return (
      <motion.div
        className="text-center space-y-6"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
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

        {/* Message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-2xl font-bold text-[var(--foreground)] mb-2">
            Check Your Email
          </h2>
          <p className="text-[var(--muted-foreground)]">
            We've sent a magic link to <span className="font-semibold">{email}</span>
          </p>
        </motion.div>

        {/* Instructions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-left"
        >
          <h3 className="font-semibold text-blue-900 mb-3">What to do next:</h3>
          <ol className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="font-bold">1.</span>
              <span>Check your email inbox for a message from us</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">2.</span>
              <span>Click the "View Booking" link in the email</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">3.</span>
              <span>You'll be able to manage your booking</span>
            </li>
          </ol>
        </motion.div>

        {/* Note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-sm text-[var(--muted-foreground)]"
        >
          The link will expire in 24 hours. If you don't see the email, check
          your spam folder.
        </motion.p>

        {/* Resend Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <Button
            variant="outline"
            onClick={() => setIsSubmitted(false)}
            className="w-full"
          >
            Try Another Email
          </Button>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Icon */}
      <motion.div
        className="flex justify-center"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <div className="p-4 bg-[var(--primary)]/10 rounded-full">
          <MailIcon size={40} className="text-[var(--primary)]" />
        </div>
      </motion.div>

      {/* Title */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-2">
          Access Your Booking
        </h2>
        <p className="text-[var(--muted-foreground)]">
          Enter your email to receive a magic link
        </p>
      </motion.div>

      {/* Email Input */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
          Email Address
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            setError("");
          }}
          placeholder="your@email.com"
          className={`w-full px-4 py-3 rounded-lg border-2 transition-colors focus:outline-none ${
            error
              ? "border-red-500 focus:border-red-600"
              : "border-[var(--border)] focus:border-[var(--primary)]"
          }`}
          disabled={isLoading}
        />
        {error && (
          <motion.p
            className="text-sm text-red-500 mt-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {error}
          </motion.p>
        )}
      </motion.div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-blue-50 border border-blue-200 p-4 rounded-lg"
      >
        <p className="text-sm text-blue-800">
          <span className="font-semibold">🔒 Secure & Private:</span> No password
          needed. We'll send you a secure link to access your booking.
        </p>
      </motion.div>

      {/* Submit Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Button
          type="submit"
          disabled={isLoading || !email.trim()}
          className="w-full bg-[var(--primary)] hover:bg-[var(--primary-dark)] text-white"
        >
          {isLoading ? "Sending..." : "Send Magic Link"}
        </Button>
      </motion.div>

      {/* Footer */}
      <motion.p
        className="text-xs text-center text-[var(--muted-foreground)]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        We'll never share your email. You can unsubscribe at any time.
      </motion.p>
    </form>
  );
}
