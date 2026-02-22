import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

export function ExitIntentPopup() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleMouseLeave = (e: MouseEvent) => {
      if ((e as any).clientY <= 0) {
        setIsVisible(true);
      }
    };

    document.addEventListener("mouseleave", handleMouseLeave);
    return () => document.removeEventListener("mouseleave", handleMouseLeave);
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
        <Dialog open={isVisible} onOpenChange={setIsVisible}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Wait! Don't go yet</DialogTitle>
            </DialogHeader>
            <DialogDescription>
              Get 30 days free access to Kenikool. No credit card required.
            </DialogDescription>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              style={{
                backgroundColor: "var(--accent-10)",
                border: "1px solid var(--accent)",
                borderRadius: "0.5rem",
                padding: "0.75rem",
                marginBottom: "1.5rem",
              }}
            >
              <p className="text-sm font-semibold text-accent">
                Use code: <span className="text-lg">SALON20</span>
              </p>
              <p className="text-xs text-muted-foreground">
                20% off your first 3 months
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
              }}
            >
              <Link to="/auth/register" className="block">
                <Button className="w-full">Start Free Trial</Button>
              </Link>
              <Button
                onClick={() => setIsVisible(false)}
                variant="outline"
                className="w-full"
              >
                Maybe later
              </Button>
            </motion.div>
          </DialogContent>
        </Dialog>
      )}
    </AnimatePresence>
  );
}
