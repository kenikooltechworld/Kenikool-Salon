import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

interface Service {
  id: string;
  name: string;
  price: string;
  duration: string;
  description?: string;
}

interface ServiceListProps {
  services: Service[];
}

export function ServiceList({ services }: ServiceListProps) {
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
        Services
      </motion.h2>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
        variants={containerVariants}
      >
        {services.map((service, index) => (
          <motion.div
            key={service.id}
            className="p-4 border border-[var(--border)] rounded-lg hover:shadow-lg transition-shadow"
            variants={itemVariants}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-[var(--foreground)] text-lg">
                  {service.name}
                </h3>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {service.duration}
                </p>
              </div>
              <span className="text-lg font-bold text-[var(--primary)]">
                {service.price}
              </span>
            </div>
            {service.description && (
              <p className="text-sm text-[var(--muted-foreground)] mb-3">
                {service.description}
              </p>
            )}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button size="sm" className="w-full">
                Book Now
              </Button>
            </motion.div>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
}
