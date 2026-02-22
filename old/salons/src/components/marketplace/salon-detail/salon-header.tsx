import { motion } from "framer-motion";
import { StarIcon, MapPinIcon, PhoneIcon, MailIcon, ClockIcon } from "@/components/icons";

interface SalonHeaderProps {
  salon: {
    name: string;
    rating: number;
    reviews: number;
    address: string;
    phone: string;
    email: string;
    description: string;
  };
}

export function SalonHeader({ salon }: SalonHeaderProps) {
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
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 }
    }
  };

  return (
    <motion.div
      className="space-y-4"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Name and Rating */}
      <motion.div variants={itemVariants}>
        <h1 className="text-4xl md:text-5xl font-bold text-[var(--foreground)] mb-2">
          {salon.name}
        </h1>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{
                  delay: 0.5 + i * 0.1,
                  type: "spring",
                  stiffness: 200
                }}
              >
                <StarIcon
                  size={20}
                  className={`${
                    i < Math.floor(salon.rating)
                      ? "text-yellow-400 fill-current"
                      : "text-gray-300"
                  }`}
                />
              </motion.div>
            ))}
          </div>
          <span className="text-lg font-semibold text-[var(--foreground)]">
            {salon.rating}
          </span>
          <span className="text-[var(--muted-foreground)]">
            ({salon.reviews} reviews)
          </span>
        </div>
      </motion.div>

      {/* Description */}
      <motion.p
        className="text-lg text-[var(--muted-foreground)] max-w-2xl"
        variants={itemVariants}
      >
        {salon.description}
      </motion.p>

      {/* Contact Information */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4"
        variants={containerVariants}
      >
        {/* Address */}
        <motion.div
          className="flex items-start gap-3"
          variants={itemVariants}
        >
          <MapPinIcon className="text-[var(--primary)] mt-1 flex-shrink-0" size={20} />
          <div>
            <p className="text-sm text-[var(--muted-foreground)]">Address</p>
            <p className="font-medium text-[var(--foreground)]">{salon.address}</p>
          </div>
        </motion.div>

        {/* Phone */}
        <motion.div
          className="flex items-start gap-3"
          variants={itemVariants}
        >
          <PhoneIcon className="text-[var(--primary)] mt-1 flex-shrink-0" size={20} />
          <div>
            <p className="text-sm text-[var(--muted-foreground)]">Phone</p>
            <a
              href={`tel:${salon.phone}`}
              className="font-medium text-[var(--primary)] hover:underline"
            >
              {salon.phone}
            </a>
          </div>
        </motion.div>

        {/* Email */}
        <motion.div
          className="flex items-start gap-3"
          variants={itemVariants}
        >
          <MailIcon className="text-[var(--primary)] mt-1 flex-shrink-0" size={20} />
          <div>
            <p className="text-sm text-[var(--muted-foreground)]">Email</p>
            <a
              href={`mailto:${salon.email}`}
              className="font-medium text-[var(--primary)] hover:underline"
            >
              {salon.email}
            </a>
          </div>
        </motion.div>

        {/* Hours */}
        <motion.div
          className="flex items-start gap-3"
          variants={itemVariants}
        >
          <ClockIcon className="text-[var(--primary)] mt-1 flex-shrink-0" size={20} />
          <div>
            <p className="text-sm text-[var(--muted-foreground)]">Hours</p>
            <p className="font-medium text-[var(--foreground)]">9:00 AM - 6:00 PM</p>
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
