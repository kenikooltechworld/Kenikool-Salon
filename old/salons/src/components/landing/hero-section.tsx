import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SparklesIcon } from "@/components/icons";
import { useEffect, useState, useRef } from "react";

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

// Floating element variants with improved animation
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

// Animated Counter Component with optimized performance
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
    // Check for prefers-reduced-motion
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

// Statistics Component with enhanced animations
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
      { threshold: 0.1, rootMargin: "-100px" }
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
      className="grid grid-cols-3 gap-4 sm:gap-6 md:gap-8 mt-12 sm:mt-16 px-2"
      variants={staggerContainerVariants}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
    >
      {stats.map((stat, index) => (
        <motion.div
          key={index}
          className="text-center"
          variants={fadeInUpVariants}
        >
          <motion.div
            className="text-2xl sm:text-3xl md:text-4xl font-bold text-accent mb-2"
            initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={isInView ? { opacity: 1 } : { opacity: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            {isInView && (
              <AnimatedCounter
                end={stat.value}
                duration={2}
                suffix={stat.suffix}
              />
            )}
          </motion.div>
          <p className="text-xs sm:text-sm text-white/80">{stat.label}</p>
        </motion.div>
      ))}
    </motion.div>
  );
}

export function HeroSection() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [useVideoBackground, setUseVideoBackground] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Check for prefers-reduced-motion
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handleMediaChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener("change", handleMediaChange);

    // Check if video should be used (not on mobile or slow connection)
    const isDesktop = window.innerWidth >= 1024;
    const hasGoodConnection =
      (navigator.connection as any)?.effectiveType === "4g" ||
      (navigator.connection as any)?.effectiveType === undefined;

    setUseVideoBackground(isDesktop && hasGoodConnection);

    return () => mediaQuery.removeEventListener("change", handleMediaChange);
  }, []);

  // Handle video loading
  const handleVideoCanPlay = () => {
    setVideoLoaded(true);
  };

  const handleVideoError = () => {
    // Fallback to image if video fails to load
    setUseVideoBackground(false);
  };

  return (
    <section className="relative min-h-screen sm:min-h-[600px] md:min-h-[700px] lg:min-h-screen py-16 sm:py-20 md:py-24 lg:py-32 px-4 sm:px-6 overflow-hidden mt-16 sm:mt-20 flex items-center justify-center">
      {/* Background - Video or Image */}
      <div className="absolute inset-0 z-0">
        {useVideoBackground ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              muted
              loop
              playsInline
              className={`w-full h-full object-cover transition-opacity duration-500 ${
                videoLoaded ? "opacity-100" : "opacity-0"
              }`}
              poster="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1920&h=1080&fit=crop&auto=format&q=80"
              onCanPlay={handleVideoCanPlay}
              onError={handleVideoError}
            >
              <source
                src="https://videos.pexels.com/video-files/3045163/3045163-sd_640_360_25fps.mp4"
                type="video/mp4"
              />
              <img
                src="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1920&h=1080&fit=crop&auto=format&q=80"
                alt="Modern salon interior"
                className="w-full h-full object-cover"
              />
            </video>
            {!videoLoaded && (
              <img
                src="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1920&h=1080&fit=crop&auto=format&q=80"
                alt="Modern salon interior"
                className="w-full h-full object-cover"
              />
            )}
          </>
        ) : (
          <img
            src="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1920&h=1080&fit=crop&auto=format&q=80"
            alt="Modern salon interior"
            className="w-full h-full object-cover"
            loading="eager"
          />
        )}
        <div className="absolute inset-0 bg-linear-to-b from-black/50 via-black/60 to-black/70" />
      </div>

      {/* Floating Elements - Enhanced with better animations */}
      {!prefersReducedMotion && (
        <>
          {/* Large floating blob - top right */}
          <motion.div
            className="hidden sm:block absolute top-10 sm:top-20 right-5 sm:right-10 w-40 sm:w-72 h-40 sm:h-72 bg-primary/10 rounded-full blur-3xl"
            variants={floatingElementVariants}
            animate="animate"
            style={{ willChange: "transform" }}
          />

          {/* Large floating blob - bottom left */}
          <motion.div
            className="hidden sm:block absolute bottom-10 sm:bottom-20 left-5 sm:left-10 w-48 sm:w-96 h-48 sm:h-96 bg-accent/10 rounded-full blur-3xl"
            variants={floatingElementVariants2}
            animate="animate"
            style={{ willChange: "transform" }}
          />

          {/* Small floating icon - top left (hidden on mobile) */}
          <motion.div
            className="absolute top-32 left-10 w-16 h-16 bg-white/5 rounded-lg backdrop-blur-sm border border-white/10 hidden md:flex items-center justify-center"
            variants={floatingIconVariants}
            animate="animate"
            style={{ willChange: "transform" }}
          >
            <SparklesIcon size={24} className="text-accent/60" />
          </motion.div>

          {/* Small floating icon - bottom right (hidden on mobile) */}
          <motion.div
            className="absolute bottom-32 right-10 w-16 h-16 bg-white/5 rounded-lg backdrop-blur-sm border border-white/10 hidden md:flex items-center justify-center"
            animate={{
              y: [0, -20, 0],
              rotate: [0, -5, 5, 0],
              transition: {
                duration: 7,
                repeat: Infinity,
                ease: "easeInOut",
              },
            }}
            style={{ willChange: "transform" }}
          >
            <SparklesIcon size={24} className="text-primary/60" />
          </motion.div>
        </>
      )}

      {/* Content */}
      <div className="container mx-auto text-center max-w-4xl relative z-10">
        <motion.div
          className="mb-4 sm:mb-6"
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
        >
          <Badge
            variant="accent"
            size="lg"
            className="mb-4 sm:mb-6 text-xs sm:text-sm bg-white/20 backdrop-blur-sm border border-white/30 text-white hover:bg-white/30 transition-colors"
          >
            <SparklesIcon size={14} className="sm:w-4 sm:h-4" />
            Trusted by 500+ Nigerian Salons
          </Badge>
        </motion.div>

        <motion.h1
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-4 sm:mb-6 text-white leading-tight drop-shadow-2xl"
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.1 }}
        >
          Manage Your Salon with Ease
        </motion.h1>

        <motion.p
          className="text-base sm:text-lg md:text-xl lg:text-2xl text-white mb-8 sm:mb-10 max-w-3xl mx-auto px-2 drop-shadow-lg font-medium"
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.2 }}
        >
          Complete salon management platform with POS, bookings, inventory,
          staff management, and powerful analytics. Built for Nigerian
          businesses with Naira pricing.
        </motion.p>

        <motion.div
          className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center mb-8 px-2"
          variants={staggerContainerVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.3 }}
        >
          <motion.div variants={scaleInVariants} className="w-full sm:w-auto">
            <Link to="/register" className="w-full sm:w-auto block">
              <Button
                size="lg"
                className="w-full sm:w-auto text-sm sm:text-base bg-accent hover:bg-accent-dark text-white font-semibold px-6 sm:px-8 py-3 sm:py-4 transition-all duration-300 hover:shadow-lg hover:shadow-accent/50 active:scale-95"
              >
                Start 30-Day Free Trial
              </Button>
            </Link>
          </motion.div>
          <motion.div variants={scaleInVariants} className="w-full sm:w-auto">
            <Link to="/login" className="w-full sm:w-auto block">
              <Button
                size="lg"
                className="w-full sm:w-auto text-sm sm:text-base bg-white/20 hover:bg-white/30 text-white font-semibold px-6 sm:px-8 py-3 sm:py-4 border border-white/40 backdrop-blur-sm transition-all duration-300 hover:shadow-lg active:scale-95"
              >
                Sign In
              </Button>
            </Link>
          </motion.div>
        </motion.div>

        <motion.p
          className="text-xs sm:text-sm text-white/80 px-2"
          variants={fadeInUpVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.4 }}
        >
          No credit card required • Free 30-day trial • Cancel anytime
        </motion.p>

        {/* Statistics Section */}
        <StatisticsSection />
      </div>
    </section>
  );
}
