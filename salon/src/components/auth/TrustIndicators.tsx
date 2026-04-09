import { motion } from "framer-motion";
import { LockIcon, CheckIcon, ShieldIcon } from "@/components/icons";

export function TrustIndicators() {
  const indicators = [
    { icon: LockIcon, label: "Secure Login" },
    { icon: CheckIcon, label: "SSL Encrypted" },
    { icon: ShieldIcon, label: "Data Protected" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.5 }}
      className="flex items-center justify-center gap-6 mt-6 pt-6 border-t border-border"
    >
      {indicators.map((indicator, idx) => {
        const IconComponent = indicator.icon;
        return (
          <div
            key={idx}
            className="flex items-center gap-2 text-xs text-muted-foreground"
          >
            <IconComponent size={16} className="text-primary" />
            <span>{indicator.label}</span>
          </div>
        );
      })}
    </motion.div>
  );
}
