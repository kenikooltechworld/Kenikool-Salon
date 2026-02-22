/**
 * Test component to verify all new frontend dependencies are installed and working
 * This component tests imports for:
 * - framer-motion
 * - swiper
 * - leaflet
 * - react-leaflet
 */

import { motion } from "framer-motion";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Autoplay } from "swiper/modules";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "leaflet/dist/leaflet.css";

export function TestDependencies() {
  // Test Framer Motion
  const fadeInVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  // Test Swiper
  const swiperSlides = [
    { id: 1, title: "Slide 1" },
    { id: 2, title: "Slide 2" },
    { id: 3, title: "Slide 3" },
  ];

  // Test Leaflet
  const defaultPosition: [number, number] = [6.5244, 3.3792]; // Lagos, Nigeria

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold">Frontend Dependencies Test</h1>

      {/* Framer Motion Test */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeInVariants}
        className="p-4 bg-blue-100 rounded-lg"
      >
        <h2 className="text-xl font-semibold">✅ Framer Motion</h2>
        <p className="text-sm text-gray-600">
          This section is animated with Framer Motion
        </p>
      </motion.div>

      {/* Swiper Test */}
      <div className="space-y-2">
        <h2 className="text-xl font-semibold">✅ Swiper</h2>
        <Swiper
          modules={[Navigation, Pagination, Autoplay]}
          spaceBetween={20}
          slidesPerView={1}
          navigation
          pagination={{ clickable: true }}
          autoplay={{ delay: 3000 }}
          className="bg-green-100 rounded-lg"
        >
          {swiperSlides.map((slide) => (
            <SwiperSlide key={slide.id} className="p-8 text-center">
              <h3 className="text-lg font-semibold">{slide.title}</h3>
              <p className="text-sm text-gray-600">
                Swiper carousel is working correctly
              </p>
            </SwiperSlide>
          ))}
        </Swiper>
      </div>

      {/* Leaflet Test */}
      <div className="space-y-2">
        <h2 className="text-xl font-semibold">✅ Leaflet & React-Leaflet</h2>
        <MapContainer
          center={defaultPosition}
          zoom={13}
          style={{ height: "300px", width: "100%", borderRadius: "0.5rem" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          <Marker position={defaultPosition}>
            <Popup>
              <div>
                <h3 className="font-semibold">Test Location</h3>
                <p className="text-sm">Lagos, Nigeria</p>
              </div>
            </Popup>
          </Marker>
        </MapContainer>
      </div>

      {/* Summary */}
      <div className="p-4 bg-green-100 rounded-lg border-2 border-green-500">
        <h2 className="text-xl font-semibold text-green-800">
          ✅ All Dependencies Installed Successfully
        </h2>
        <ul className="mt-2 space-y-1 text-sm text-green-700">
          <li>✓ framer-motion - Animations working</li>
          <li>✓ swiper - Carousel working</li>
          <li>✓ leaflet - Map library working</li>
          <li>✓ react-leaflet - React wrapper working</li>
          <li>✓ @types/leaflet - TypeScript types working</li>
        </ul>
      </div>
    </div>
  );
}
