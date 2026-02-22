import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { SalonCard } from "@/lib/api/hooks/useMarketplace";
import { motion } from "framer-motion";

// Fix Leaflet default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

interface SalonMapViewProps {
  salons: SalonCard[];
  userLocation?: { latitude: number; longitude: number };
  hoveredSalonId?: string | null;
  onSalonHover?: (salonId: string | null) => void;
}

export function SalonMapView({
  salons,
  userLocation,
  hoveredSalonId,
  onSalonHover,
}: SalonMapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const markers = useRef<Map<string, L.Marker>>(new Map());

  useEffect(() => {
    if (!mapContainer.current) return;

    // Initialize map
    const defaultCenter: [number, number] = userLocation
      ? [userLocation.latitude, userLocation.longitude]
      : [6.5244, 3.3792]; // Lagos, Nigeria default

    map.current = L.map(mapContainer.current).setView(defaultCenter, 12);

    // Add tile layer
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map.current);

    // Add user location marker if available
    if (userLocation) {
      L.circleMarker([userLocation.latitude, userLocation.longitude], {
        radius: 8,
        fillColor: "#3b82f6",
        color: "#1e40af",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8,
      })
        .addTo(map.current)
        .bindPopup("Your Location");
    }

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [userLocation]);

  // Add/update salon markers
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markers.current.forEach((marker) => {
      map.current?.removeLayer(marker);
    });
    markers.current.clear();

    // Add new markers
    salons.forEach((salon) => {
      // Type assertion to access location property
      const salonWithLocation = salon as any;
      
      // Check if salon has location data - if not, skip
      if (!salonWithLocation.location?.coordinates && !('latitude' in salon) && !('longitude' in salon)) return;

      // Get coordinates from either location object or direct properties
      let latitude: number;
      let longitude: number;

      if (salonWithLocation.location?.coordinates) {
        [longitude, latitude] = salonWithLocation.location.coordinates;
      } else if ('latitude' in salon && 'longitude' in salon) {
        latitude = (salon as any).latitude;
        longitude = (salon as any).longitude;
      } else {
        return; // Skip if no coordinates available
      }

      const isHovered = salon.id === hoveredSalonId;

      // Create custom icon
      const iconColor = isHovered ? "#ef4444" : "#8b5cf6";
      const iconSize = isHovered ? 40 : 32;

      const customIcon = L.divIcon({
        html: `
          <div style="
            background-color: ${iconColor};
            width: ${iconSize}px;
            height: ${iconSize}px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            cursor: pointer;
          ">
            📍
          </div>
        `,
        iconSize: [iconSize, iconSize],
        className: "custom-marker",
      });

      const marker = L.marker([latitude, longitude], { icon: customIcon })
        .addTo(map.current!)
        .bindPopup(`
          <div style="min-width: 200px;">
            <h3 style="font-weight: bold; margin-bottom: 8px;">${salon.name}</h3>
            <p style="margin: 4px 0; font-size: 12px;">
              <strong>Rating:</strong> ${salon.average_rating.toFixed(1)} ⭐ (${salon.total_reviews} reviews)
            </p>
            ${salon.starting_price ? `<p style="margin: 4px 0; font-size: 12px;"><strong>From:</strong> ₦${salon.starting_price.toLocaleString()}</p>` : ""}
            ${salon.distance_km ? `<p style="margin: 4px 0; font-size: 12px;"><strong>Distance:</strong> ${salon.distance_km.toFixed(1)} km</p>` : ""}
            <a href="/marketplace/salon/${salon.id}" style="
              display: inline-block;
              margin-top: 8px;
              padding: 6px 12px;
              background-color: #8b5cf6;
              color: white;
              border-radius: 4px;
              text-decoration: none;
              font-size: 12px;
            ">View Details</a>
          </div>
        `)
        .on("mouseover", () => {
          onSalonHover?.(salon.id);
          marker.openPopup();
        })
        .on("mouseout", () => {
          onSalonHover?.(null);
        });

      markers.current.set(salon.id, marker);
    });

    // Fit bounds to show all markers
    if (markers.current.size > 0) {
      const group = new L.FeatureGroup(Array.from(markers.current.values()));
      map.current?.fitBounds(group.getBounds().pad(0.1));
    }
  }, [salons, hoveredSalonId, onSalonHover]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="w-full rounded-lg overflow-hidden border border-border shadow-lg"
    >
      <div
        ref={mapContainer}
        style={{
          width: "100%",
          height: "500px",
        }}
      />
    </motion.div>
  );
}
