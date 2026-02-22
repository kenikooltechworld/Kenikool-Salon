import { useState } from "react";
import { motion } from "framer-motion";
import { Swiper, SwiperSlide } from "swiper/react";
import { Pagination, Autoplay } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import { FeatureCard } from "./feature-card";
import { FeatureDetailModal } from "./feature-detail-modal";
import posImg from "@/assets/features/pos.jpg";
import bookingImg from "@/assets/features/users.jpg";
import clientImg from "@/assets/features/client.jpg";
import staffImg from "@/assets/features/staff.jpg";
import inventoryImg from "@/assets/features/inventory.jpg";
import analyticsImg from "@/assets/features/analytics.jpg";
import marketingImg from "@/assets/features/marketing.jpg";
import loyaltyImg from "@/assets/features/loyalty.jpg";
import packagesImg from "@/assets/features/packages.jpg";
import promoImg from "@/assets/features/promo.jpg";
import giftImg from "@/assets/features/giftcard.jpg";
import notificationImg from "@/assets/features/notification.jpg";
import {
  CalendarIcon,
  UsersIcon,
  ChartIcon,
  ScissorsIcon,
  CreditCardIcon,
  PackageIcon,
  BellIcon,
  TrendingUpIcon,
  ListIcon,
  TagIcon,
  GiftIcon,
  SparklesIcon,
} from "@/components/icons";

interface Feature {
  icon: React.ReactNode;
  title: string;
  description: string;
  colorClass: string;
  imageUrl: string;
  details?: string;
  benefits?: string[];
}

export function FeaturesSection() {
  const [selectedFeature, setSelectedFeature] = useState<Feature | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const features: Feature[] = [
    {
      icon: <CreditCardIcon size={32} className="text-primary" />,
      title: "Point of Sale (POS)",
      description:
        "Complete POS system with offline mode, split payments, and receipt printing",
      colorClass: "bg-primary/10",
      imageUrl: posImg,
      details:
        "Our advanced POS system is designed specifically for salons. Process payments quickly, manage multiple payment methods, and keep detailed transaction records.",
      benefits: [
        "Offline mode for uninterrupted service",
        "Split payments between multiple clients",
        "Integrated receipt printing",
        "Real-time sales tracking",
        "Multiple payment gateway support",
      ],
    },
    {
      icon: <CalendarIcon size={32} className="text-secondary" />,
      title: "Online Booking",
      description:
        "Let clients book appointments 24/7 through your custom booking page",
      colorClass: "bg-secondary/10",
      imageUrl: bookingImg,
      details:
        "Enable your clients to book appointments anytime, anywhere. Reduce no-shows with automated reminders and manage your schedule efficiently.",
      benefits: [
        "24/7 online booking availability",
        "Automated appointment reminders",
        "Customizable booking page",
        "Real-time availability updates",
        "Reduce no-shows by 40%",
      ],
    },
    {
      icon: <UsersIcon size={32} className="text-accent" />,
      title: "Client Management",
      description:
        "Track client history, preferences, and build lasting relationships",
      colorClass: "bg-accent/10",
      imageUrl: clientImg,
      details:
        "Build comprehensive client profiles with service history, preferences, and contact information. Personalize every interaction.",
      benefits: [
        "Complete client history tracking",
        "Service preferences storage",
        "Birthday and anniversary reminders",
        "Client segmentation",
        "Loyalty program integration",
      ],
    },
    {
      icon: <ScissorsIcon size={32} className="text-success" />,
      title: "Staff Management",
      description: "Manage schedules, commissions, and track staff performance",
      colorClass: "bg-success/10",
      imageUrl: staffImg,
      details:
        "Streamline staff management with automated scheduling, commission tracking, and performance analytics.",
      benefits: [
        "Automated schedule management",
        "Commission calculation",
        "Performance tracking",
        "Staff availability management",
        "Payroll integration",
      ],
    },
    {
      icon: <ListIcon size={32} className="text-primary" />,
      title: "Inventory Management",
      description: "Track products, low stock alerts, and automated reordering",
      colorClass: "bg-primary/10",
      imageUrl: inventoryImg,
      details:
        "Never run out of stock again. Track inventory in real-time with automatic low-stock alerts and reordering.",
      benefits: [
        "Real-time inventory tracking",
        "Low stock alerts",
        "Automated reordering",
        "Supplier management",
        "Inventory forecasting",
      ],
    },
    {
      icon: <ChartIcon size={32} className="text-secondary" />,
      title: "Analytics & Reports",
      description:
        "Get insights into revenue, performance, and business growth",
      colorClass: "bg-secondary/10",
      imageUrl: analyticsImg,
      details:
        "Make data-driven decisions with comprehensive analytics and customizable reports.",
      benefits: [
        "Revenue analytics",
        "Performance metrics",
        "Custom report generation",
        "Trend analysis",
        "Predictive insights",
      ],
    },
    {
      icon: <SparklesIcon size={32} className="text-accent" />,
      title: "Marketing Campaigns",
      description: "Automated SMS/email campaigns to bring clients back",
      colorClass: "bg-accent/10",
      imageUrl: marketingImg,
      details:
        "Engage your clients with targeted marketing campaigns via SMS and email.",
      benefits: [
        "Automated SMS campaigns",
        "Email marketing tools",
        "Campaign scheduling",
        "Client segmentation",
        "Performance tracking",
      ],
    },
    {
      icon: <TrendingUpIcon size={32} className="text-success" />,
      title: "Loyalty Programs",
      description: "Reward repeat customers with points and special offers",
      colorClass: "bg-success/10",
      imageUrl: loyaltyImg,
      details:
        "Build customer loyalty with customizable rewards programs and special offers.",
      benefits: [
        "Points-based rewards",
        "Tiered loyalty levels",
        "Special offers",
        "Referral rewards",
        "Automated redemption",
      ],
    },
    {
      icon: <PackageIcon size={32} className="text-primary" />,
      title: "Packages & Memberships",
      description: "Create service packages and recurring membership plans",
      colorClass: "bg-primary/10",
      imageUrl: packagesImg,
      details:
        "Increase revenue with customizable service packages and membership plans.",
      benefits: [
        "Custom package creation",
        "Membership management",
        "Recurring billing",
        "Package analytics",
        "Flexible pricing",
      ],
    },
    {
      icon: <TagIcon size={32} className="text-secondary" />,
      title: "Promo Codes",
      description: "Create discount codes for special promotions and events",
      colorClass: "bg-secondary/10",
      imageUrl: promoImg,
      details:
        "Run targeted promotions with customizable discount codes and tracking.",
      benefits: [
        "Custom discount codes",
        "Usage tracking",
        "Time-limited offers",
        "Client segmentation",
        "ROI analytics",
      ],
    },
    {
      icon: <GiftIcon size={32} className="text-accent" />,
      title: "Gift Cards",
      description: "Sell and manage digital gift cards for your salon",
      colorClass: "bg-accent/10",
      imageUrl: giftImg,
      details:
        "Increase revenue with digital gift cards that are easy to purchase and redeem.",
      benefits: [
        "Digital gift card sales",
        "Automated delivery",
        "Redemption tracking",
        "Customizable designs",
        "Revenue analytics",
      ],
    },
    {
      icon: <BellIcon size={32} className="text-success" />,
      title: "Smart Notifications",
      description: "Automated reminders via SMS, email, and push notifications",
      colorClass: "bg-success/10",
      imageUrl: notificationImg,
      details:
        "Keep clients engaged with timely notifications about appointments and offers.",
      benefits: [
        "Appointment reminders",
        "SMS notifications",
        "Email notifications",
        "Push notifications",
        "Customizable templates",
      ],
    },
  ];

  const handleFeatureClick = (feature: Feature) => {
    setSelectedFeature(feature);
    setIsModalOpen(true);
  };

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
            Everything You Need
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground px-2">
            Powerful features to run your salon efficiently
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
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              onClick={() => handleFeatureClick(feature)}
            >
              <FeatureCard
                {...feature}
                onCardClick={() => handleFeatureClick(feature)}
              />
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
            className="features-swiper"
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
            {features.map((feature, index) => (
              <SwiperSlide key={index}>
                <div className="pb-12">
                  <FeatureCard
                    {...feature}
                    onCardClick={() => handleFeatureClick(feature)}
                  />
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </motion.div>
      </div>

      {/* Feature Detail Modal */}
      {selectedFeature && (
        <FeatureDetailModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setTimeout(() => setSelectedFeature(null), 300);
          }}
          feature={selectedFeature}
        />
      )}
    </section>
  );
}
