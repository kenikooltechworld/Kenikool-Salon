import { motion } from "framer-motion";
import { Swiper, SwiperSlide } from "swiper/react";
import { Pagination, Autoplay } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import { Card, CardContent } from "@/components/ui/card";
import {
  CheckCircleIcon,
  SparklesIcon,
  TrendingUpIcon,
} from "@/components/icons";

interface Step {
  number: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  imageUrl: string;
}

export function HowItWorksSection() {
  const steps: Step[] = [
    {
      number: "1",
      title: "Sign Up Free",
      description:
        "Create your account in minutes. No credit card required for the 30-day trial.",
      icon: <SparklesIcon size={32} className="text-primary" />,
      imageUrl:
        "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop&auto=format&q=80",
    },
    {
      number: "2",
      title: "Set Up Your Salon",
      description:
        "Add your services, staff, and customize your booking page. We'll guide you through it.",
      icon: <CheckCircleIcon size={32} className="text-secondary" />,
      imageUrl:
        "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop&auto=format&q=80",
    },
    {
      number: "3",
      title: "Start Growing",
      description:
        "Accept bookings, process payments, and watch your business grow with powerful analytics.",
      icon: <TrendingUpIcon size={32} className="text-accent" />,
      imageUrl:
        "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop&auto=format&q=80",
    },
  ];

  // Animation variants
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
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
      },
    },
  };

  const titleVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
      },
    },
  };

  const StepCard = ({ step }: { step: Step }) => (
    <Card hover>
      <CardContent className="pt-0">
        {/* Image */}
        <div className="relative h-32 sm:h-40 rounded-t-lg overflow-hidden mb-4">
          <img
            src={step.imageUrl}
            alt={step.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>

        {/* Content */}
        <div className="px-4 pb-4 text-center">
          <div className="flex justify-center mb-3">{step.icon}</div>
          <div className="w-12 sm:w-14 h-12 sm:h-14 rounded-full bg-primary text-white flex items-center justify-center text-lg sm:text-xl font-bold mx-auto mb-3">
            {step.number}
          </div>
          <h3 className="text-lg sm:text-xl font-bold mb-2">{step.title}</h3>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {step.description}
          </p>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <section className="py-12 sm:py-16 md:py-20 px-4 sm:px-6 bg-[var(--muted)]/30">
      <div className="container mx-auto">
        {/* Title Section with Scroll Animation */}
        <motion.div
          className="text-center mb-8 sm:mb-12"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={titleVariants}
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 sm:mb-4 text-foreground">
            How It Works
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground px-2">
            Get started in 3 simple steps
          </p>
        </motion.div>

        {/* Desktop Grid with Stagger Animation */}
        <motion.div
          className="hidden lg:grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={containerVariants}
        >
          {steps.map((step, index) => (
            <motion.div key={index} variants={itemVariants}>
              <StepCard step={step} />
            </motion.div>
          ))}
        </motion.div>

        {/* Mobile Carousel - Swipeable */}
        <motion.div
          className="lg:hidden"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={itemVariants}
        >
          <Swiper
            modules={[Pagination, Autoplay]}
            spaceBetween={20}
            slidesPerView={1}
            pagination={{ clickable: true }}
            autoplay={{ delay: 5000, disableOnInteraction: false }}
            className="how-it-works-swiper"
            breakpoints={{
              320: {
                slidesPerView: 1,
                spaceBetween: 16,
              },
              640: {
                slidesPerView: 2,
                spaceBetween: 16,
              },
              1024: {
                slidesPerView: 2,
                spaceBetween: 20,
              },
            }}
          >
            {steps.map((step, index) => (
              <SwiperSlide key={index}>
                <div className="pb-12">
                  <StepCard step={step} />
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </motion.div>
      </div>
    </section>
  );
}
