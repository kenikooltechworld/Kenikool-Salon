import { motion } from "framer-motion";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Button } from "@/components/ui/button";
import { MapPinIcon, PhoneIcon } from "@/components/icons";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

interface Salon {
  name: string;
  address: string;
  phone: string;
  lat: number;
  lng: number;
}

interface LocationMapProps {
  salon: Salon;
}

export function LocationMap({ salon }: LocationMapProps) {
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

  const handleGetDirections = () => {
    const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(salon.address)}`;
    window.open(mapsUrl, "_blank");
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
        Location
      </motion.h2>

      <motion.div
        className="space-y-4"
        variants={containerVariants}
      >
        {/* Address Card */}
        <motion.div
          className="p-4 bg-[var(--muted)] rounded-lg"
          variants={itemVariants}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-start gap-3 mb-4">
            <MapPinIcon className="text-[var(--primary)] mt-1 flex-shrink-0" size={20} />
            <div className="flex-1">
              <p className="text-sm text-[var(--muted-foreground)] mb-1">Address</p>
              <p className="font-medium text-[var(--foreground)]">{salon.address}</p>
            </div>
          </div>
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              size="sm"
              variant="outline"
              onClick={handleGetDirections}
              className="w-full"
            >
              Get Directions
            </Button>
          </motion.div>
        </motion.div>

        {/* Phone Card */}
        <motion.div
          className="p-4 bg-[var(--muted)] rounded-lg"
          variants={itemVariants}
          whileHover={{ scale: 1.02 }}
        >
          <div className="flex items-center gap-3">
            <PhoneIcon className="text-[var(--primary)] flex-shrink-0" size={20} />
            <div className="flex-1">
              <p className="text-sm text-[var(--muted-foreground)] mb-1">Phone</p>
              <a
                href={`tel:${salon.phone}`}
                className="font-medium text-[var(--primary)] hover:underline"
              >
                {salon.phone}
              </a>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Map */}
      <motion.div
        className="rounded-lg overflow-hidden h-96 border border-[var(--border)]"
        variants={itemVariants}
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 0.3 }}
      >
        <MapContainer
          center={[salon.lat, salon.lng]}
          zoom={15}
          style={{ height: "100%", width: "100%" }}
          className="rounded-lg"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={[salon.lat, salon.lng]}>
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold mb-1">{salon.name}</h3>
                <p className="text-sm text-gray-600">{salon.address}</p>
              </div>
            </Popup>
          </Marker>
        </MapContainer>
      </motion.div>
    </motion.div>
  );
}
