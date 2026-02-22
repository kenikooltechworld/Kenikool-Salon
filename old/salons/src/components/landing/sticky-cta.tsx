import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { XIcon, ArrowRightIcon } from "@/components/icons";
import { Link } from "react-router-dom";

export function StickyCTA() {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      const windowHeight = window.innerHeight;

      // Show CTA after scrolling past the hero section
      if (scrollPosition > windowHeight * 0.8 && !isDismissed) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [isDismissed]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed bottom-6 right-6 z-50"
          initial={{ opacity: 0, y: 100, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 100, scale: 0.8 }}
          transition={{
            type: "spring",
            stiffness: 300,
            damping: 30,
          }}
        >
          <motion.div
            className="bg-[var(--primary)] text-white p-4 rounded-2xl shadow-2xl max-w-sm"
            whileHover={{ scale: 1.05 }}
            animate={{
              boxShadow: [
                "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
              ],
            }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <motion.h3
                  className="font-semibold mb-2 text-lg"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  Ready to Transform Your Salon?
                </motion.h3>
                <motion.p
                  className="text-sm opacity-90 mb-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  Start your free trial today and see the difference.
                </motion.p>
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <Button
                    size="sm"
                    className="bg-[var(--accent)] hover:bg-[var(--accent-dark)] text-white w-full"
                    asChild
                  >
                    <Link
                      to="/register"
                      className="flex items-center justify-center gap-2"
                    >
                      Start Free Trial
                      <ArrowRightIcon size={16} />
                    </Link>
                  </Button>
                </motion.div>
              </div>
              <motion.button
                onClick={handleDismiss}
                className="text-white/70 hover:text-white transition-colors flex-shrink-0"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <XIcon size={20} />
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
