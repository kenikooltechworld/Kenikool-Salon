import { motion } from "framer-motion";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

interface PortfolioItem {
  before: string;
  after: string;
}

interface PortfolioGalleryProps {
  portfolio: PortfolioItem[];
}

export function PortfolioGallery({ portfolio }: PortfolioGalleryProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 }
    }
  };

  return (
    <motion.div
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
    >
      <motion.h2 className="text-2xl font-bold text-[var(--foreground)]" variants={itemVariants}>
        Portfolio - Before & After
      </motion.h2>

      <motion.div variants={itemVariants}>
        <Swiper
          modules={[Navigation, Pagination]}
          spaceBetween={20}
          slidesPerView={1}
          navigation
          pagination={{ clickable: true }}
          breakpoints={{
            640: {
              slidesPerView: 1,
              spaceBetween: 20,
            },
            768: {
              slidesPerView: 2,
              spaceBetween: 20,
            },
            1024: {
              slidesPerView: 2,
              spaceBetween: 30,
            },
          }}
          className="portfolio-swiper"
        >
          {portfolio.map((item, index) => (
            <SwiperSlide key={index}>
              <motion.div
                className="grid grid-cols-2 gap-4 h-80"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
              >
                {/* Before */}
                <motion.div
                  className="relative rounded-lg overflow-hidden bg-[var(--muted)]"
                  whileHover={{ scale: 1.05 }}
                >
                  <img
                    src={item.before}
                    alt="Before"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 left-2 bg-black/70 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Before
                  </div>
                </motion.div>

                {/* After */}
                <motion.div
                  className="relative rounded-lg overflow-hidden bg-[var(--muted)]"
                  whileHover={{ scale: 1.05 }}
                >
                  <img
                    src={item.after}
                    alt="After"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-2 left-2 bg-[var(--primary)] text-white px-3 py-1 rounded-full text-sm font-medium">
                    After
                  </div>
                </motion.div>
              </motion.div>
            </SwiperSlide>
          ))}
        </Swiper>
      </motion.div>

      <style jsx>{`
        .portfolio-swiper {
          padding: 20px 0;
        }
        .portfolio-swiper .swiper-pagination {
          bottom: 0;
        }
        .portfolio-swiper .swiper-pagination-bullet {
          background: var(--primary);
          opacity: 0.3;
        }
        .portfolio-swiper .swiper-pagination-bullet-active {
          opacity: 1;
        }
        .portfolio-swiper .swiper-button-next,
        .portfolio-swiper .swiper-button-prev {
          color: var(--primary);
        }
      `}</style>
    </motion.div>
  );
}
