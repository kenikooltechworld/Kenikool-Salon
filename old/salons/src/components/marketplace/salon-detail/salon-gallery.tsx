import { useState } from "react";
import { motion } from "framer-motion";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Autoplay, Zoom } from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/zoom";

interface SalonGalleryProps {
  images: string[];
  salonName: string;
}

export function SalonGallery({ images, salonName }: SalonGalleryProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Main Gallery */}
      <div className="relative rounded-2xl overflow-hidden bg-[var(--muted)] h-96 md:h-[500px]">
        <Swiper
          modules={[Navigation, Pagination, Autoplay, Zoom]}
          spaceBetween={0}
          slidesPerView={1}
          navigation
          pagination={{ clickable: true }}
          autoplay={{
            delay: 5000,
            disableOnInteraction: false,
          }}
          zoom={{
            maxRatio: 3,
          }}
          className="h-full"
        >
          {images.map((image, index) => (
            <SwiperSlide key={index} className="h-full">
              <motion.div
                className="w-full h-full flex items-center justify-center cursor-zoom-in"
                whileHover={{ scale: 1.02 }}
                onClick={() => setIsFullscreen(true)}
              >
                <img
                  src={image}
                  alt={`${salonName} - Image ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </motion.div>
            </SwiperSlide>
          ))}
        </Swiper>

        {/* Fullscreen Button */}
        <motion.button
          className="absolute top-4 right-4 bg-black/50 hover:bg-black/70 text-white p-2 rounded-lg transition-colors z-10"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsFullscreen(true)}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
          </svg>
        </motion.button>
      </div>

      {/* Thumbnail Gallery */}
      <motion.div
        className="grid grid-cols-4 md:grid-cols-6 gap-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {images.map((image, index) => (
          <motion.div
            key={index}
            className="relative rounded-lg overflow-hidden h-20 cursor-pointer group"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <img
              src={image}
              alt={`Thumbnail ${index + 1}`}
              className="w-full h-full object-cover group-hover:brightness-75 transition-all"
            />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
          </motion.div>
        ))}
      </motion.div>

      {/* Fullscreen Modal */}
      {isFullscreen && (
        <motion.div
          className="fixed inset-0 bg-black z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.button
            className="absolute top-4 right-4 text-white hover:text-gray-300 transition-colors z-10"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsFullscreen(false)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </motion.button>

          <Swiper
            modules={[Navigation, Pagination, Zoom]}
            spaceBetween={0}
            slidesPerView={1}
            navigation
            pagination={{ clickable: true }}
            zoom={{ maxRatio: 3 }}
            className="w-full h-full"
          >
            {images.map((image, index) => (
              <SwiperSlide key={index} className="h-full flex items-center justify-center">
                <img
                  src={image}
                  alt={`${salonName} - Image ${index + 1}`}
                  className="w-full h-full object-contain"
                />
              </SwiperSlide>
            ))}
          </Swiper>
        </motion.div>
      )}

      <style jsx>{`
        .swiper-pagination {
          bottom: 16px;
        }
        .swiper-pagination-bullet {
          background: white;
          opacity: 0.5;
        }
        .swiper-pagination-bullet-active {
          opacity: 1;
        }
        .swiper-button-next,
        .swiper-button-prev {
          color: white;
          background: rgba(0, 0, 0, 0.5);
          width: 40px;
          height: 40px;
          border-radius: 8px;
        }
        .swiper-button-next:after,
        .swiper-button-prev:after {
          font-size: 16px;
        }
      `}</style>
    </motion.div>
  );
}
