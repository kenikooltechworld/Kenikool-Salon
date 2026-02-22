import { motion } from "framer-motion";
import { StarIcon } from "@/components/icons";

interface Stylist {
  id: string;
  name: string;
  specialty: string;
  image: string;
  rating?: number;
  reviews?: number;
  bio?: string;
}

interface StylistProfilesProps {
  stylists: Stylist[];
}

export function StylistProfiles({ stylists }: StylistProfilesProps) {
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
        Our Stylists
      </motion.h2>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        variants={containerVariants}
      >
        {stylists.map((stylist) => (
          <motion.div
            key={stylist.id}
            className="text-center"
            variants={itemVariants}
            whileHover={{ y: -10 }}
          >
            {/* Image */}
            <motion.div
              className="mb-4 relative overflow-hidden rounded-2xl h-64 bg-[var(--muted)]"
              whileHover={{ scale: 1.05 }}
            >
              <img
                src={stylist.image}
                alt={stylist.name}
                className="w-full h-full object-cover"
              />
            </motion.div>

            {/* Info */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h3 className="text-xl font-semibold text-[var(--foreground)] mb-1">
                {stylist.name}
              </h3>
              <p className="text-[var(--primary)] font-medium mb-2">
                {stylist.specialty}
              </p>

              {/* Rating */}
              {stylist.rating && (
                <motion.div
                  className="flex items-center justify-center gap-2 mb-3"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{
                          delay: 0.4 + i * 0.05,
                          type: "spring",
                          stiffness: 200
                        }}
                      >
                        <StarIcon
                          size={16}
                          className={`${
                            i < Math.floor(stylist.rating!)
                              ? "text-yellow-400 fill-current"
                              : "text-gray-300"
                          }`}
                        />
                      </motion.div>
                    ))}
                  </div>
                  <span className="text-sm text-[var(--muted-foreground)]">
                    {stylist.rating} ({stylist.reviews} reviews)
                  </span>
                </motion.div>
              )}

              {/* Bio */}
              {stylist.bio && (
                <p className="text-sm text-[var(--muted-foreground)] mb-4">
                  {stylist.bio}
                </p>
              )}
            </motion.div>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
}
