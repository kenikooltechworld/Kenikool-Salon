import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FeatureDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  feature: {
    icon: React.ReactNode;
    title: string;
    description: string;
    colorClass: string;
    imageUrl: string;
    details?: string;
    benefits?: string[];
  };
}

export function FeatureDetailModal({
  isOpen,
  onClose,
  feature,
}: FeatureDetailModalProps) {
  const [imageLoaded, setImageLoaded] = useState(false);

  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
    exit: { opacity: 0 },
  };

  const modalVariants = {
    hidden: { opacity: 0, scale: 0.95, y: 20 },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: { duration: 0.3 },
    },
    exit: {
      opacity: 0,
      scale: 0.95,
      y: 20,
      transition: { duration: 0.2 },
    },
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          onClick={onClose}
        >
          <motion.div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            variants={modalVariants}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 p-4 sm:p-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-full ${feature.colorClass} flex items-center justify-center`}>
                  {feature.icon}
                </div>
                <h2 className="text-xl sm:text-2xl font-bold text-foreground">
                  {feature.title}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={24} className="text-gray-600" />
              </button>
            </div>

            {/* Content */}
            <div className="p-4 sm:p-6">
              {/* Image */}
              <div className="relative w-full aspect-video bg-gradient-to-br from-gray-200 to-gray-300 rounded-lg overflow-hidden mb-6">
                <motion.img
                  src={feature.imageUrl}
                  alt={feature.title}
                  className="w-full h-full object-cover object-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: imageLoaded ? 1 : 0 }}
                  transition={{ duration: 0.3 }}
                  onLoad={() => setImageLoaded(true)}
                />
                {!imageLoaded && (
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse" />
                )}
              </div>

              {/* Description */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <p className="text-base sm:text-lg text-muted-foreground mb-6">
                  {feature.description}
                </p>
              </motion.div>

              {/* Details */}
              {feature.details && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="mb-6"
                >
                  <h3 className="text-lg font-semibold text-foreground mb-3">
                    Key Features
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.details}
                  </p>
                </motion.div>
              )}

              {/* Benefits */}
              {feature.benefits && feature.benefits.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="mb-6"
                >
                  <h3 className="text-lg font-semibold text-foreground mb-3">
                    Benefits
                  </h3>
                  <ul className="space-y-2">
                    {feature.benefits.map((benefit, index) => (
                      <motion.li
                        key={index}
                        className="flex items-start gap-3 text-muted-foreground"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 + index * 0.05 }}
                      >
                        <span className="text-primary font-bold mt-1">✓</span>
                        <span>{benefit}</span>
                      </motion.li>
                    ))}
                  </ul>
                </motion.div>
              )}

              {/* CTA */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="flex gap-3 pt-4 border-t border-gray-200"
              >
                <Button
                  variant="outline"
                  onClick={onClose}
                  className="flex-1"
                >
                  Close
                </Button>
                <Button className="flex-1">
                  Learn More
                </Button>
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
