import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { StarIcon } from "@/components/icons";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Autoplay } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

const testimonials = [
  {
    name: "Sarah Johnson",
    role: "Owner, Beauty Haven Salon",
    content:
      "Kenikool has transformed how I manage my salon. I've saved so much time and my customers love the automated reminders!",
    rating: 5,
  },
  {
    name: "Ahmed Hassan",
    role: "Manager, Fitness Plus Gym",
    content:
      "The analytics dashboard gives me insights I never had before. Revenue increased by 30% in just 3 months.",
    rating: 5,
  },
  {
    name: "Amara Okafor",
    role: "Founder, Spa Serenity",
    content:
      "Customer support is amazing. They helped me set everything up and I was booking appointments within hours.",
    rating: 5,
  },
  {
    name: "Chioma Adeyemi",
    role: "Owner, Glam Studio",
    content:
      "The POS system is incredibly fast and reliable. My staff loves how easy it is to use during busy hours.",
    rating: 5,
  },
  {
    name: "Tunde Okonkwo",
    role: "Manager, Elite Barber Shop",
    content:
      "Best investment for my business. The inventory tracking alone has saved me thousands in wasted products.",
    rating: 5,
  },
  {
    name: "Zainab Mohammed",
    role: "Founder, Luxury Spa & Wellness",
    content:
      "The loyalty program feature has increased our repeat customers by 45%. Highly recommended!",
    rating: 5,
  },
];

export function TestimonialsSection() {
  return (
    <section
      id="testimonials"
      className="py-20 sm:py-32 bg-gradient-to-br from-primary/5 to-secondary/5"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4">
              Loved by Business Owners
            </h2>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              See what our customers have to say about Kenikool
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
            {testimonials.map((testimonial, idx) => (
              <SwiperSlide key={idx}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: idx * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card className="p-6 h-full">
                    <div className="flex gap-1 mb-4">
                      {Array.from({ length: testimonial.rating }).map(
                        (_, i) => (
                          <StarIcon
                            key={i}
                            size={18}
                            className="text-yellow-400 fill-yellow-400"
                          />
                        ),
                      )}
                    </div>
                    <p className="text-foreground mb-4 italic">
                      "{testimonial.content}"
                    </p>
                    <div>
                      <p className="font-semibold text-foreground">
                        {testimonial.name}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {testimonial.role}
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
