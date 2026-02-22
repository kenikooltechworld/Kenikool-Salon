import { motion } from "framer-motion";

interface SalonInfoProps {
  salon: {
    name: string;
    description: string;
    hours: Record<string, string>;
  };
}

export function SalonInfo({ salon }: SalonInfoProps) {
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
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.4 }
    }
  };

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  return (
    <motion.div
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
    >
      {/* About Section */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-4">About</h2>
        <p className="text-[var(--muted-foreground)] leading-relaxed text-lg">
          {salon.description}
        </p>
      </motion.div>

      {/* Hours Section */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-4">Hours</h2>
        <motion.div
          className="space-y-3"
          variants={containerVariants}
        >
          {days.map((day, index) => (
            <motion.div
              key={day}
              className="flex justify-between items-center py-2 border-b border-[var(--border)]"
              variants={itemVariants}
              custom={index}
            >
              <span className="font-medium text-[var(--foreground)]">{day}</span>
              <span className={`text-[var(--muted-foreground)] ${
                day === "Sunday" ? "text-red-500" : ""
              }`}>
                {salon.hours[day.toLowerCase()] || "Closed"}
              </span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Amenities Section */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-4">Amenities</h2>
        <motion.div
          className="grid grid-cols-2 md:grid-cols-3 gap-4"
          variants={containerVariants}
        >
          {[
            "Free WiFi",
            "Parking Available",
            "Wheelchair Accessible",
            "Air Conditioning",
            "Comfortable Seating",
            "Refreshments"
          ].map((amenity, index) => (
            <motion.div
              key={amenity}
              className="flex items-center gap-3 p-3 bg-[var(--muted)] rounded-lg"
              variants={itemVariants}
              custom={index}
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-2 h-2 bg-[var(--primary)] rounded-full" />
              <span className="text-[var(--foreground)]">{amenity}</span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
