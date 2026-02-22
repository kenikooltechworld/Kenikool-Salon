import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { PhoneIcon, MessageCircleIcon } from "@/components/icons";

export function FloatingCTA() {
  const containerVariants = {
    hidden: { opacity: 0, scale: 0 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 200,
        damping: 20
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, scale: 0 },
    visible: (i: number) => ({
      opacity: 1,
      scale: 1,
      transition: {
        delay: i * 0.1,
        type: "spring",
        stiffness: 200,
        damping: 20
      }
    })
  };

  return (
    <motion.div
      className="fixed bottom-8 left-8 z-40 flex flex-col gap-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* WhatsApp Button */}
      <motion.div
        custom={0}
        variants={itemVariants}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          size="lg"
          className="rounded-full w-14 h-14 p-0 bg-green-500 hover:bg-green-600 text-white shadow-lg"
          asChild
        >
          <a 
            href="https://wa.me/1234567890" 
            target="_blank" 
            rel="noopener noreferrer"
            title="Chat on WhatsApp"
          >
            <MessageCircleIcon size={24} />
          </a>
        </Button>
      </motion.div>

      {/* Phone Button */}
      <motion.div
        custom={1}
        variants={itemVariants}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <Button
          size="lg"
          className="rounded-full w-14 h-14 p-0 bg-blue-500 hover:bg-blue-600 text-white shadow-lg"
          asChild
        >
          <a 
            href="tel:+1234567890"
            title="Call us"
          >
            <PhoneIcon size={24} />
          </a>
        </Button>
      </motion.div>

      {/* Floating Label */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
        className="text-xs text-[var(--muted-foreground)] whitespace-nowrap"
      >
        Need help?
      </motion.div>
    </motion.div>
  );
}
