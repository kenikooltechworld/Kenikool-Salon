import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { XIcon } from "@/components/icons";
import { Link } from "react-router-dom";

export function ExitIntentPopup() {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    if (isDismissed) return;

    const handleMouseLeave = (e: MouseEvent) => {
      // Only trigger if mouse is leaving from the top of the page
      if (e.clientY <= 0) {
        setIsVisible(true);
      }
    };

    // Mobile: Show popup after 30 seconds of inactivity
    const mobileTimer = setTimeout(() => {
      if (window.innerWidth < 768 && !isDismissed) {
        setIsVisible(true);
      }
    }, 30000);

    document.addEventListener("mouseleave", handleMouseLeave);
    return () => {
      document.removeEventListener("mouseleave", handleMouseLeave);
      clearTimeout(mobileTimer);
    };
  }, [isDismissed]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleDismiss}
          />

          {/* Modal */}
          <motion.div
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 max-w-md w-full mx-4"
            initial={{ opacity: 0, scale: 0.8, y: -50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -50 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <motion.div
              className="bg-white rounded-2xl shadow-2xl overflow-hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              {/* Close Button */}
              <motion.button
                onClick={handleDismiss}
                className="absolute top-4 right-4 text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors z-10"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <XIcon size={24} />
              </motion.button>

              {/* Content */}
              <div className="p-8 text-center">
                <motion.h2
                  className="text-3xl font-bold mb-4 text-[var(--foreground)]"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  Wait! Don't Go Yet
                </motion.h2>

                <motion.p
                  className="text-[var(--muted-foreground)] mb-6 text-lg"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  Get 20% off your first month when you sign up today.
                </motion.p>

                <motion.div
                  className="bg-[var(--accent)]/10 border-2 border-[var(--accent)] rounded-lg p-4 mb-6"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  <p className="text-sm font-semibold text-[var(--accent)]">
                    Use code: <span className="text-lg font-bold">SALON20</span>
                  </p>
                </motion.div>

                <motion.div
                  className="space-y-3"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <Link to="/auth/register" className="block">
                    <Button
                      size="lg"
                      className="w-full bg-primary hover:bg-primary/90 text-white"
                      onClick={handleDismiss}
                    >
                      Claim Your Discount
                    </Button>
                  </Link>

                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full"
                    onClick={handleDismiss}
                  >
                    Maybe Later
                  </Button>
                </motion.div>

                <motion.p
                  className="text-xs text-[var(--muted-foreground)] mt-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 }}
                >
                  Limited time offer. Offer expires in 7 days.
                </motion.p>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
