import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

interface PublicHeroSectionProps {
  salonInfo: {
    id: string;
    name: string;
    description: string;
    email: string;
    logo_url?: string;
    primary_color?: string;
    secondary_color?: string;
  };
  onBookNowClick: () => void;
}

const fadeInUpVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
};

const staggerContainerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2,
    },
  },
};

const scaleInVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5, ease: "easeOut" },
  },
};

export default function PublicHeroSection({
  salonInfo,
  onBookNowClick,
}: PublicHeroSectionProps) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleMediaChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleMediaChange);
    return () => mediaQuery.removeEventListener("change", handleMediaChange);
  }, []);

  const primaryColor = salonInfo.primary_color || "#3B82F6";
  const secondaryColor = salonInfo.secondary_color || "#1F2937";

  return (
    <section className="relative min-h-[500px] sm:min-h-[600px] py-16 sm:py-20 md:py-24 px-4 sm:px-6 overflow-hidden flex items-center justify-center">
      {/* Background with gradient using salon colors */}
      <div
        className="absolute inset-0 z-0"
        style={{
          background: `linear-gradient(135deg, ${primaryColor}20 0%, ${secondaryColor}20 100%)`,
        }}
      />

      {/* Floating Elements */}
      {!prefersReducedMotion && (
        <>
          {/* Large floating blob - top right */}
          <motion.div
            animate={{
              y: [0, 40, 0],
              x: [0, 25, 0],
              transition: {
                duration: 8,
                repeat: Infinity,
                ease: "easeInOut",
              },
            }}
            style={{
              backgroundColor: primaryColor,
              opacity: 0.1,
              willChange: "transform",
              position: "absolute",
              top: "2.5rem",
              right: "1.25rem",
              width: "10rem",
              height: "10rem",
              borderRadius: "9999px",
              filter: "blur(48px)",
            }}
          />

          {/* Large floating blob - bottom left */}
          <motion.div
            animate={{
              y: [0, -40, 0],
              x: [0, -25, 0],
              transition: {
                duration: 10,
                repeat: Infinity,
                ease: "easeInOut",
              },
            }}
            style={{
              backgroundColor: secondaryColor,
              opacity: 0.1,
              willChange: "transform",
              position: "absolute",
              bottom: "2.5rem",
              left: "1.25rem",
              width: "12rem",
              height: "12rem",
              borderRadius: "9999px",
              filter: "blur(48px)",
            }}
          />
        </>
      )}

      {/* Content */}
      <div className="container mx-auto text-center max-w-3xl relative z-10">
        {/* Logo */}
        {salonInfo.logo_url && (
          <motion.div
            variants={fadeInUpVariants}
            initial="hidden"
            animate="visible"
            className="mb-6"
          >
            <img
              src={salonInfo.logo_url}
              alt={salonInfo.name}
              className="h-16 sm:h-20 mx-auto"
            />
          </motion.div>
        )}

        {/* Salon Name */}
        <motion.div
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          <h1
            className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4 sm:mb-6 leading-tight"
            style={{ color: primaryColor }}
          >
            {salonInfo.name}
          </h1>
        </motion.div>

        {/* Description */}
        <motion.div
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          <p className="text-base sm:text-lg md:text-xl text-gray-700 mb-8 sm:mb-10 max-w-2xl mx-auto px-2">
            {salonInfo.description}
          </p>
        </motion.div>

        {/* CTA Button */}
        <motion.div
          variants={staggerContainerVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.3 }}
        >
          <motion.div variants={scaleInVariants}>
            <Button
              onClick={onBookNowClick}
              size="lg"
              className="text-white font-semibold px-8 py-6 text-lg"
              style={{ backgroundColor: primaryColor }}
            >
              Book Now
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
