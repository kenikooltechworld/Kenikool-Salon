import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ArrowLeftIcon, ShareIcon, HeartIcon } from "@/components/icons";
import { SalonHeader } from "@/components/marketplace/salon-detail/salon-header";
import { SalonGallery } from "@/components/marketplace/salon-detail/salon-gallery";
import { SalonInfo } from "@/components/marketplace/salon-detail/salon-info";
import { ServiceList } from "@/components/marketplace/salon-detail/service-list";
import { StylistProfiles } from "@/components/marketplace/salon-detail/stylist-profiles";
import { ReviewsSection } from "@/components/marketplace/salon-detail/reviews-section";
import { PortfolioGallery } from "@/components/marketplace/salon-detail/portfolio-gallery";
import { LocationMap } from "@/components/marketplace/salon-detail/location-map";
import { BookingButtons } from "@/components/marketplace/salon-detail/booking-buttons";
import { ReferralTracker } from "@/components/marketplace/salon-detail/referral-tracker";
import { useSalonDetail } from "@/lib/api/hooks/useMarketplaceQueries";
import { useMarketplaceStore } from "@/lib/store/marketplaceStore";

interface Salon {
  id: string;
  name: string;
  rating: number;
  reviews: number;
  address: string;
  phone: string;
  email: string;
  description: string;
  gallery: string[];
  services: Array<{
    id: string;
    name: string;
    price: string;
    duration: string;
  }>;
  stylists: Array<{
    id: string;
    name: string;
    specialty: string;
    image: string;
  }>;
  portfolio: Array<{ before: string; after: string }>;
  lat: number;
  lng: number;
  hours: Record<string, string>;
}

export default function SalonDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: salon, isLoading, error } = useSalonDetail(id || "");
  const { isFavorite, addFavorite, removeFavorite } = useMarketplaceStore();
  const [localIsFavorite, setLocalIsFavorite] = useState(false);

  useEffect(() => {
    if (salon) {
      setLocalIsFavorite(isFavorite(salon.id));
    }
  }, [salon, isFavorite]);

  const handleShare = async () => {
    if (!salon) return;
    if (navigator.share) {
      try {
        await navigator.share({
          title: salon.name,
          text: `Check out ${salon.name} on our platform!`,
          url: window.location.href,
        });
      } catch (error) {
        console.error("Error sharing:", error);
      }
    }
  };

  const handleFavorite = () => {
    if (!salon) return;
    if (localIsFavorite) {
      removeFavorite(salon.id);
    } else {
      addFavorite(salon);
    }
    setLocalIsFavorite(!localIsFavorite);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--primary)] mx-auto mb-4"></div>
          <p className="text-[var(--muted-foreground)]">
            Loading salon details...
          </p>
        </div>
      </div>
    );
  }

  if (error || !salon) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">
            {error?.message || "Salon not found"}
          </p>
          <Button onClick={() => navigate(-1)}>Go Back</Button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="min-h-screen bg-background"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with Back Button */}
      <motion.div
        className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[var(--border)]"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <motion.button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-[var(--foreground)] hover:text-[var(--primary)] transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <ArrowLeftIcon size={24} />
            <span className="hidden sm:inline">Back</span>
          </motion.button>

          <div className="flex items-center gap-2">
            <motion.button
              onClick={handleShare}
              className="p-2 hover:bg-[var(--muted)] rounded-lg transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              title="Share"
            >
              <ShareIcon size={20} />
            </motion.button>
            <motion.button
              onClick={handleFavorite}
              className={`p-2 rounded-lg transition-colors ${
                localIsFavorite
                  ? "bg-red-100 text-red-500"
                  : "hover:bg-[var(--muted)] text-[var(--foreground)]"
              }`}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              title="Add to favorites"
            >
              <HeartIcon
                size={20}
                fill={localIsFavorite ? "currentColor" : "none"}
              />
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        {/* Gallery */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <SalonGallery images={salon.gallery} salonName={salon.name} />
        </motion.div>

        {/* Header Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <SalonHeader salon={salon} />
        </motion.div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-12">
            {/* About Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
            >
              <SalonInfo salon={salon} />
            </motion.div>

            {/* Services Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
            >
              <ServiceList services={salon.services} />
            </motion.div>

            {/* Stylists Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.6 }}
            >
              <StylistProfiles stylists={salon.stylists} />
            </motion.div>

            {/* Portfolio Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.7 }}
            >
              <PortfolioGallery portfolio={salon.portfolio} />
            </motion.div>

            {/* Reviews Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.8 }}
            >
              <ReviewsSection salonId={salon.id} />
            </motion.div>

            {/* Location Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.9 }}
            >
              <LocationMap salon={salon} />
            </motion.div>
          </div>

          {/* Right Column - Booking Sidebar */}
          <motion.div
            className="lg:col-span-1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="sticky top-24 space-y-6">
              <BookingButtons salon={salon} />
              <ReferralTracker
                salonId={salon.id}
                salonName={salon.name}
                salonWebsite={salon.website}
              />
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
