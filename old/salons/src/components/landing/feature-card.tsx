import { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  colorClass: string;
  imageUrl: string;
  details?: string;
  benefits?: string[];
  onCardClick?: () => void;
}

export function FeatureCard({
  icon,
  title,
  description,
  colorClass,
  imageUrl,
  details,
  benefits,
  onCardClick,
}: FeatureCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const cardVariants = {
    rest: {
      scale: 1,
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    },
    hover: {
      scale: 1.05,
      boxShadow: "0 20px 25px rgba(0, 0, 0, 0.15)",
      transition: { duration: 0.3 },
    },
  };

  const imageVariants = {
    rest: { scale: 1 },
    hover: {
      scale: 1.1,
      transition: { duration: 0.3 },
    },
  };

  const handleClick = () => {
    if (onCardClick) {
      onCardClick();
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="rest"
      whileHover="hover"
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onClick={handleClick}
      className="cursor-pointer h-full"
    >
      <Card hover className="h-full flex flex-col overflow-hidden">
        <CardContent className="p-0 flex flex-col h-full">
          {/* Image Container */}
          <motion.div
            className="relative w-full aspect-video bg-gradient-to-br from-gray-200 to-gray-300 overflow-hidden flex-shrink-0"
            variants={imageVariants}
          >
            <motion.img
              src={imageUrl}
              alt={title}
              className="w-full h-full object-cover object-center"
              loading="lazy"
              initial={{ opacity: 0 }}
              animate={{ opacity: imageLoaded ? 1 : 0 }}
              transition={{ duration: 0.3 }}
              onLoad={() => setImageLoaded(true)}
            />
            {!imageLoaded && (
              <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse" />
            )}
            {/* Overlay on hover */}
            <motion.div
              className="absolute inset-0 bg-black/20 flex items-center justify-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: isHovered ? 1 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <motion.span
                className="text-white font-semibold text-sm sm:text-base"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: isHovered ? 1 : 0.8, opacity: isHovered ? 1 : 0 }}
                transition={{ duration: 0.2 }}
              >
                Click to Learn More
              </motion.span>
            </motion.div>
          </motion.div>

          {/* Content Container */}
          <div className="flex-1 flex flex-col p-4 sm:p-5 md:p-6">
            {/* Icon */}
            <motion.div
              className={`w-12 sm:w-14 md:w-16 h-12 sm:h-14 md:h-16 rounded-full ${colorClass} flex items-center justify-center flex-shrink-0 mb-3 sm:mb-4`}
              animate={{ scale: isHovered ? 1.1 : 1 }}
              transition={{ duration: 0.2 }}
            >
              {icon}
            </motion.div>

            {/* Title */}
            <h3 className="text-base sm:text-lg md:text-xl font-bold mb-2 sm:mb-3 text-foreground line-clamp-2">
              {title}
            </h3>

            {/* Description */}
            <p className="text-xs sm:text-sm md:text-base text-muted-foreground leading-relaxed flex-1">
              {description}
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
