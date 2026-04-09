import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SparklesIcon } from "@/components/icons";
import { useEffect, useState, useRef } from "react";
import bgImage from "@/assets/bg.jpg";

// Animation variants
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

// Floating element variants
const floatingElementVariants = {
  animate: {
    y: [0, 40, 0],
    x: [0, 25, 0],
    transition: {
      duration: 8,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

const floatingElementVariants2 = {
  animate: {
    y: [0, -40, 0],
    x: [0, -25, 0],
    transition: {
      duration: 10,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Floating icon variants
const floatingIconVariants = {
  animate: {
    y: [0, 20, 0],
    rotate: [0, 5, -5, 0],
    transition: {
      duration: 6,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Animated Counter Component
function AnimatedCounter({
  end,
  duration = 2,
  suffix = "",
}: {
  end: number;
  duration?: number;
  suffix?: string;
}) {
  const [count, setCount] = useState(0);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const startTimeRef = useRef<number | null>(null);
  const animationFrameIdRef = useRef<number | null>(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleMediaChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleMediaChange);
    return () => mediaQuery.removeEventListener("change", handleMediaChange);
  }, []);

  useEffect(() => {
    if (prefersReducedMotion) {
      setCount(end);
      return;
    }

    const animate = (currentTime: number) => {
      if (startTimeRef.current === null) {
        startTimeRef.current = currentTime;
      }

      const elapsed = currentTime - startTimeRef.current;
      const progress = Math.min(elapsed / (duration * 1000), 1);

      setCount(Math.floor(end * progress));

      if (progress < 1) {
        animationFrameIdRef.current = requestAnimationFrame(animate);
      }
    };

    animationFrameIdRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameIdRef.current !== null) {
        cancelAnimationFrame(animationFrameIdRef.current);
      }
    };
  }, [end, duration, prefersReducedMotion]);

  return (
    <span>
      {count.toLocaleString()}
      {suffix}
    </span>
  );
}

// Statistics Section Component
function StatisticsSection() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleMediaChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleMediaChange);
    return () => mediaQuery.removeEventListener("change", handleMediaChange);
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1, rootMargin: "-100px" },
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  const stats = [
    { label: "Active Salons", value: 500, suffix: "+" },
    { label: "Bookings Processed", value: 10000, suffix: "+" },
    { label: "Happy Customers", value: 50000, suffix: "+" },
  ];

  return (
    <motion.div
      ref={ref}
      variants={staggerContainerVariants}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
    >
      <div className="grid grid-cols-3 gap-4 sm:gap-6 md:gap-8 mt-12 sm:mt-16 px-2">
        {stats.map((stat, index) => (
          <motion.div key={index} variants={fadeInUpVariants}>
            <div className="text-center">
              <motion.div
                initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
                animate={isInView ? { opacity: 1 } : { opacity: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div
                  className="text-2xl sm:text-3xl md:text-4xl font-bold mb-2"
                  style={{ color: "var(--accent)" }}
                >
                  {isInView && (
                    <AnimatedCounter
                      end={stat.value}
                      duration={2}
                      suffix={stat.suffix}
                    />
                  )}
                </div>
              </motion.div>
              <p className="text-xs sm:text-sm text-white/80">{stat.label}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

export function HeroSection() {
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

  return (
    <section className="relative min-h-screen sm:min-h-[600px] md:min-h-[700px] lg:min-h-screen py-16 sm:py-20 md:py-24 lg:py-32 px-4 sm:px-6 overflow-hidden mt-0 pt-24 flex items-center justify-center">
      {/* Background Image with Overlay */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />
      <div className="absolute inset-0 z-0 bg-black/40" />

      {/* Floating Elements */}
      {!prefersReducedMotion && (
        <>
          {/* Large floating blob - top right */}
          <motion.div
            variants={floatingElementVariants}
            animate="animate"
            style={{
              backgroundColor: "var(--primary)",
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
            variants={floatingElementVariants2}
            animate="animate"
            style={{
              backgroundColor: "var(--accent)",
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

          {/* Small floating icon - top left */}
          <motion.div
            variants={floatingIconVariants}
            animate="animate"
            style={{
              willChange: "transform",
              position: "absolute",
              top: "8rem",
              left: "2.5rem",
              width: "4rem",
              height: "4rem",
              backgroundColor: "rgba(255, 255, 255, 0.05)",
              borderRadius: "0.5rem",
              backdropFilter: "blur(4px)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              display: "none",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <SparklesIcon size={24} className="text-accent/60" />
          </motion.div>

          {/* Small floating icon - bottom right */}
          <motion.div
            animate={{
              y: [0, -20, 0],
              rotate: [0, -5, 5, 0],
              transition: {
                duration: 7,
                repeat: Infinity,
                ease: "easeInOut",
              },
            }}
            style={{
              willChange: "transform",
              position: "absolute",
              bottom: "8rem",
              right: "2.5rem",
              width: "4rem",
              height: "4rem",
              backgroundColor: "rgba(255, 255, 255, 0.05)",
              borderRadius: "0.5rem",
              backdropFilter: "blur(4px)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              display: "none",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <SparklesIcon size={24} className="text-primary/60" />
          </motion.div>
        </>
      )}

      {/* Content */}
      <div className="container mx-auto text-center max-w-4xl relative z-10">
        <motion.div
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
        >
          <div className="mb-4 sm:mb-6">
            <Badge
              variant="accent"
              size="lg"
              className="mb-4 sm:mb-6 text-xs sm:text-sm bg-white/20 backdrop-blur-sm border border-white/30 text-white hover:bg-white/30 transition-colors inline-block"
            >
              <SparklesIcon size={14} className="sm:w-4 sm:h-4 inline mr-2" />
              Trusted by 10,000+ salons across Africa
            </Badge>
          </div>
        </motion.div>

        <motion.div
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-4 sm:mb-6 text-white leading-tight drop-shadow-2xl">
            Manage Your Salon with Ease
          </h1>
        </motion.div>

        <motion.div
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-white mb-8 sm:mb-10 max-w-3xl mx-auto px-2 drop-shadow-lg font-medium">
            Complete salon management platform with POS, bookings, inventory,
            staff management, and powerful analytics. Built for Nigerian
            businesses with Naira pricing.
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainerVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.3 }}
        >
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center mb-8 px-2">
            <motion.div variants={scaleInVariants}>
              <div className="w-full sm:w-auto">
                <Link to="/auth/register" className="w-full sm:w-auto block">
                  <Button
                    variant="accent"
                    size="lg"
                    className="w-full sm:w-auto"
                  >
                    Sign Up
                  </Button>
                </Link>
              </div>
            </motion.div>
            <motion.div variants={scaleInVariants}>
              <div className="w-full sm:w-auto">
                <Link to="/auth/login" className="w-full sm:w-auto block">
                  <Button
                    variant="outline"
                    size="lg"
                    className="w-full sm:w-auto bg-white/20 hover:bg-white/30 text-white border-white/40 backdrop-blur-sm"
                  >
                    Sign In
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </motion.div>

        <motion.div
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.4 }}
        >
          <p className="text-xs sm:text-sm text-white/80 px-2">
            No credit card required • Free 30-day trial • Cancel anytime
          </p>
        </motion.div>

        {/* Statistics Section */}
        <StatisticsSection />
      </div>
    </section>
  );
}
