import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function StickyCTA() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY;
      // Show after scrolling past 500px
      setIsVisible(scrollPosition > 500);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          style={{
            position: "fixed",
            bottom: "1rem",
            right: "1rem",
            zIndex: 40,
            maxWidth: "20rem",
          }}
        >
          <Card className="p-4">
            <button
              onClick={() => setIsVisible(false)}
              className="absolute top-2 right-2 p-1 hover:bg-muted rounded text-lg transition-colors"
            >
              ✕
            </button>
            <h3 className="font-semibold text-foreground mb-2">
              Ready to get started?
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Join thousands of businesses using Kenikool
            </p>
            <Link to="/auth/register" className="block">
              <Button
                size="sm"
                className="w-full hover:shadow-lg transition-shadow duration-300"
              >
                Start Free Trial
              </Button>
            </Link>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
