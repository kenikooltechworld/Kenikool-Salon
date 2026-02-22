import { useState, useEffect, useMemo, Suspense, lazy } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  SearchIcon,
  MapPinIcon,
  StarIcon,
  ListIcon,
  ChevronDownIcon,
} from "@/components/icons";
import {
  useSearchSalons,
  useGetUserLocation,
  SalonCard,
} from "@/lib/api/hooks/useMarketplace";
import { motion } from "framer-motion";

// Lazy load Leaflet map to avoid SSR issues
const SalonMapView = lazy(() =>
  import("./salon-map-view").then((mod) => ({ default: mod.SalonMapView })),
);

const MapLoadingFallback = () => (
  <div className="w-full h-96 bg-muted rounded-lg flex items-center justify-center">
    <p className="text-muted-foreground">Loading map...</p>
  </div>
);

// Skeleton loader component
function SalonCardSkeleton() {
  return (
    <Card className="h-full">
      <CardContent className="p-0">
        <div className="h-40 sm:h-48 bg-muted rounded-t-lg animate-pulse" />
        <div className="p-3 sm:p-4 space-y-3">
          <div className="h-5 bg-muted rounded animate-pulse w-3/4" />
          <div className="h-4 bg-muted rounded animate-pulse w-1/2" />
          <div className="h-4 bg-muted rounded animate-pulse w-2/3" />
        </div>
      </CardContent>
    </Card>
  );
}

// Filter panel component
interface FilterState {
  minPrice: number;
  maxPrice: number;
  minRating: number;
  maxDistance: number;
  services: string[];
}

function FilterPanel({
  onFilterChange,
  isOpen,
  onToggle,
}: {
  onFilterChange: (filters: FilterState) => void;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const [filters, setFilters] = useState<FilterState>({
    minPrice: 0,
    maxPrice: 100000,
    minRating: 0,
    maxDistance: 50,
    services: [],
  });

  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    const updated = { ...filters, ...newFilters };
    setFilters(updated);
    onFilterChange(updated);
  };

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: isOpen ? 1 : 0, height: isOpen ? "auto" : 0 }}
      transition={{ duration: 0.3 }}
      className="overflow-hidden"
    >
      <div className="bg-card border border-border rounded-lg p-4 sm:p-6 mb-6 space-y-4">
        <div>
          <label className="text-sm font-semibold mb-2 block">
            Price Range
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="number"
              placeholder="Min"
              value={filters.minPrice}
              onChange={(e) =>
                handleFilterChange({ minPrice: Number(e.target.value) })
              }
              className="flex-1 px-3 py-2 border border-border rounded text-sm"
            />
            <span className="text-muted-foreground">-</span>
            <input
              type="number"
              placeholder="Max"
              value={filters.maxPrice}
              onChange={(e) =>
                handleFilterChange({ maxPrice: Number(e.target.value) })
              }
              className="flex-1 px-3 py-2 border border-border rounded text-sm"
            />
          </div>
        </div>

        <div>
          <label className="text-sm font-semibold mb-2 block">
            Minimum Rating
          </label>
          <select
            value={filters.minRating}
            onChange={(e) =>
              handleFilterChange({ minRating: Number(e.target.value) })
            }
            className="w-full px-3 py-2 border border-border rounded text-sm"
          >
            <option value={0}>All Ratings</option>
            <option value={3}>3+ Stars</option>
            <option value={4}>4+ Stars</option>
            <option value={4.5}>4.5+ Stars</option>
          </select>
        </div>

        <div>
          <label className="text-sm font-semibold mb-2 block">
            Distance (km)
          </label>
          <input
            type="range"
            min="1"
            max="100"
            value={filters.maxDistance}
            onChange={(e) =>
              handleFilterChange({ maxDistance: Number(e.target.value) })
            }
            className="w-full"
          />
          <span className="text-xs text-muted-foreground">
            Up to {filters.maxDistance} km
          </span>
        </div>
      </div>
    </motion.div>
  );
}

export function SalonDirectorySection() {
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"list" | "map">("list");
  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    minPrice: 0,
    maxPrice: 100000,
    minRating: 0,
    maxDistance: 50,
    services: [],
  });
  const [hoveredSalonId, setHoveredSalonId] = useState<string | null>(null);

  const { data: locationData } = useGetUserLocation();
  const { data: salonsData, isLoading } = useSearchSalons({
    limit: 12,
    query: searchQuery || undefined,
    latitude: locationData?.latitude,
    longitude: locationData?.longitude,
    radius_km: filters.maxDistance,
    min_rating: filters.minRating > 0 ? filters.minRating : undefined,
    max_price: filters.maxPrice < 100000 ? filters.maxPrice : undefined,
  });

  const salons = salonsData?.salons || [];

  // Filter salons based on selected filters
  const filteredSalons = useMemo(() => {
    return salons.filter((salon) => {
      const meetsPrice =
        !salon.starting_price ||
        (salon.starting_price >= filters.minPrice &&
          salon.starting_price <= filters.maxPrice);
      const meetsRating = salon.average_rating >= filters.minRating;
      const meetsDistance =
        !filters.maxDistance ||
        (salon.distance_km ? salon.distance_km <= filters.maxDistance : true);

      return meetsPrice && meetsRating && meetsDistance;
    });
  }, [salons, filters]);

  // Responsive view mode
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setViewMode("list");
      }
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  const cardHoverVariants = {
    rest: { scale: 1, boxShadow: "0 4px 6px rgba(0,0,0,0.1)" },
    hover: {
      scale: 1.05,
      boxShadow: "0 20px 25px rgba(0,0,0,0.15)",
      transition: { duration: 0.3 },
    },
  };

  return (
    <section className="py-12 sm:py-16 md:py-20 px-4 sm:px-6" id="salons">
      <div className="container mx-auto">
        {/* Header */}
        <motion.div
          className="text-center mb-8 sm:mb-12"
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 sm:mb-4">
            Find Salons Near You
          </h2>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground mb-6 sm:mb-8 px-2">
            Browse and book appointments at top-rated salons across Nigeria
          </p>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-6 px-2">
            <div className="relative">
              <SearchIcon
                size={20}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <input
                type="text"
                placeholder="Search by salon name or location..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 sm:py-4 rounded-lg border-2 border-border bg-card text-foreground focus:outline-none focus:border-primary transition-colors text-sm sm:text-base"
              />
            </div>
          </div>

          {/* View Toggle and Filter Button */}
          <div className="flex flex-wrap gap-2 justify-center items-center">
            {/* Filter Button */}
            <motion.button
              onClick={() => setFilterOpen(!filterOpen)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border hover:bg-muted transition-colors text-sm"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <ChevronDownIcon size={16} />
              <span>Filters</span>
            </motion.button>

            {/* View Toggle (Desktop only) */}
            <div className="hidden md:flex gap-2 border border-border rounded-lg p-1">
              <motion.button
                onClick={() => setViewMode("list")}
                className={`px-3 py-2 rounded transition-colors text-sm ${
                  viewMode === "list"
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <ListIcon size={16} />
              </motion.button>
              <motion.button
                onClick={() => setViewMode("map")}
                className={`px-3 py-2 rounded transition-colors text-sm ${
                  viewMode === "map"
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <MapPinIcon size={16} />
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Filter Panel */}
        <FilterPanel
          onFilterChange={setFilters}
          isOpen={filterOpen}
          onToggle={() => setFilterOpen(!filterOpen)}
        />

        {/* Content Area */}
        {isLoading ? (
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {[...Array(8)].map((_, i) => (
              <motion.div key={i} variants={itemVariants}>
                <SalonCardSkeleton />
              </motion.div>
            ))}
          </motion.div>
        ) : filteredSalons.length === 0 ? (
          <motion.div
            className="text-center py-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
          >
            <p className="text-muted-foreground text-sm sm:text-base">
              {searchQuery
                ? "No salons found. Try a different search."
                : "No salons available yet. Be the first to register!"}
            </p>
          </motion.div>
        ) : viewMode === "list" ? (
          // List View
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {filteredSalons.slice(0, 8).map((salon: SalonCard) => (
              <motion.div
                key={salon.id}
                variants={itemVariants}
                onMouseEnter={() => setHoveredSalonId(salon.id)}
                onMouseLeave={() => setHoveredSalonId(null)}
              >
                <Link to={`/marketplace/salon/${salon.id}`}>
                  <motion.div
                    variants={cardHoverVariants}
                    initial="rest"
                    animate={hoveredSalonId === salon.id ? "hover" : "rest"}
                  >
                    <Card className="h-full overflow-hidden">
                      <CardContent className="p-0">
                        {/* Salon Image */}
                        <div className="relative h-40 sm:h-48 bg-gradient-to-br from-purple-100 to-pink-100 rounded-t-lg overflow-hidden flex items-center justify-center">
                          {salon.logo_url ? (
                            <img
                              src={salon.logo_url}
                              alt={salon.name || "Salon"}
                              className="w-full h-full object-cover"
                              loading="lazy"
                              onError={(e) => {
                                // Fallback to emoji if image fails to load
                                const container = (e.target as HTMLImageElement)
                                  .parentElement;
                                if (container) {
                                  container.innerHTML = `
                                    <div class="text-center space-y-2 w-full">
                                      <div class="text-5xl">💇‍♀️</div>
                                      <p class="text-xs font-medium text-muted-foreground px-2 line-clamp-2">${salon.name}</p>
                                    </div>
                                  `;
                                }
                              }}
                            />
                          ) : (
                            <div className="text-center space-y-2">
                              <div className="text-5xl">💇‍♀️</div>
                              <p className="text-xs font-medium text-muted-foreground px-2 line-clamp-2">
                                {salon.name}
                              </p>
                            </div>
                          )}
                        </div>

                        {/* Salon Info */}
                        <div className="p-3 sm:p-4">
                          <h3 className="font-bold text-base sm:text-lg mb-2 line-clamp-1">
                            {salon.name}
                          </h3>
                          <div className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground mb-3">
                            <MapPinIcon
                              size={14}
                              className="sm:w-4 sm:h-4 shrink-0"
                            />
                            <span className="line-clamp-1">
                              {salon.city || "Nigeria"}
                            </span>
                          </div>

                          {/* Distance */}
                          {salon.distance_km && (
                            <div className="text-xs text-muted-foreground mb-2">
                              {salon.distance_km.toFixed(1)} km away
                            </div>
                          )}

                          {/* Rating */}
                          {salon.average_rating > 0 && (
                            <div className="flex items-center gap-2 mb-3">
                              <div className="flex items-center gap-1">
                                <StarIcon
                                  size={14}
                                  className="sm:w-4 sm:h-4 text-warning fill-current"
                                />
                                <span className="font-semibold text-sm">
                                  {salon.average_rating.toFixed(1)}
                                </span>
                              </div>
                              {salon.total_reviews > 0 && (
                                <span className="text-xs sm:text-sm text-muted-foreground">
                                  ({salon.total_reviews})
                                </span>
                              )}
                            </div>
                          )}

                          {/* Starting Price */}
                          {salon.starting_price && (
                            <p className="text-xs sm:text-sm text-muted-foreground">
                              From ₦{salon.starting_price.toLocaleString()}
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        ) : (
          // Map View
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="mb-8"
          >
            <Suspense fallback={<MapLoadingFallback />}>
              <SalonMapView
                salons={filteredSalons}
                userLocation={locationData}
                hoveredSalonId={hoveredSalonId}
                onSalonHover={setHoveredSalonId}
              />
            </Suspense>
          </motion.div>
        )}

        {/* View All Button */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
        >
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link to="/marketplace">
              <Button
                size="lg"
                variant="outline"
                className="text-sm sm:text-base"
              >
                View All Salons
              </Button>
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
