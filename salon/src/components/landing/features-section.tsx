import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Autoplay } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
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
import giftcardImg from "@/assets/features/giftcard.jpg";
import notificationImg from "@/assets/features/notification.jpg";

const features = [
  {
    title: "Point of Sale (POS)",
    description: "Fast, secure checkout with multiple payment methods",
    image: posImg,
  },
  {
    title: "Online Booking",
    description: "Automated appointment booking with calendar sync",
    image: bookingImg,
  },
  {
    title: "Client Management",
    description: "Build loyalty with customer profiles and history tracking",
    image: clientImg,
  },
  {
    title: "Staff Management",
    description: "Manage team members, roles, and availability effortlessly",
    image: staffImg,
  },
  {
    title: "Inventory Management",
    description: "Track stock levels and automate reordering",
    image: inventoryImg,
  },
  {
    title: "Analytics & Reports",
    description: "Real-time insights into revenue, bookings, and trends",
    image: analyticsImg,
  },
  {
    title: "Marketing Campaigns",
    description: "Email and SMS campaigns to engage customers",
    image: marketingImg,
  },
  {
    title: "Loyalty Programs",
    description: "Reward repeat customers with points and discounts",
    image: loyaltyImg,
  },
  {
    title: "Packages & Memberships",
    description: "Create and manage service packages and memberships",
    image: packagesImg,
  },
  {
    title: "Promo Codes",
    description: "Generate and track promotional codes and discounts",
    image: promoImg,
  },
  {
    title: "Gift Cards",
    description: "Sell and manage digital and physical gift cards",
    image: giftcardImg,
  },
  {
    title: "Smart Notifications",
    description: "Real-time alerts for bookings, cancellations, and updates",
    image: notificationImg,
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 sm:py-32 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Everything You Need
            </h2>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Powerful features designed to streamline your business operations
            </p>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <Swiper
            modules={[Navigation, Pagination, Autoplay]}
            spaceBetween={24}
            slidesPerView={1}
            navigation
            pagination={{ clickable: true }}
            autoplay={{ delay: 5000, disableOnInteraction: false }}
            breakpoints={{
              640: { slidesPerView: 2, spaceBetween: 20 },
              1024: { slidesPerView: 3, spaceBetween: 24 },
            }}
            className="pb-12"
          >
            {features.map((feature, idx) => (
              <SwiperSlide key={idx}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: idx * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card className="p-0 h-full cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-105 overflow-hidden">
                    <div className="relative w-full h-48 overflow-hidden">
                      <img
                        src={feature.image}
                        alt={feature.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="p-6">
                      <h3 className="text-xl font-semibold text-foreground mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-muted-foreground text-sm">
                        {feature.description}
                      </p>
                    </div>
                  </Card>
                </motion.div>
              </SwiperSlide>
            ))}
          </Swiper>
        </motion.div>
      </div>
    </section>
  );
}
