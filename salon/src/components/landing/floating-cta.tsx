import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";

const floatingVariants = {
  animate: {
    y: [0, 10, 0],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { type: "spring", stiffness: 300, damping: 30 },
  },
};

export function FloatingCTA() {
  return (
    <motion.div
      className="fixed bottom-4 left-4 z-40 flex gap-2"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.a
        href="https://wa.me/1234567890"
        target="_blank"
        rel="noopener noreferrer"
        className="w-14 h-14 bg-green-500 text-white rounded-full flex items-center justify-center shadow-lg text-2xl"
        title="Chat on WhatsApp"
        variants={itemVariants}
        whileHover={{
          scale: 1.15,
          boxShadow: "0 10px 25px rgba(34, 197, 94, 0.4)",
        }}
        whileTap={{ scale: 0.95 }}
        animate={floatingVariants.animate}
      >
        💬
      </motion.a>
      <motion.div variants={itemVariants}>
        <Link to="/auth/register" className="hidden sm:block">
          <Button size="sm" className="gap-2">
            <motion.span
              animate={{ opacity: [1, 0.7, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Start Free
            </motion.span>
          </Button>
        </Link>
      </motion.div>
    </motion.div>
  );
}
