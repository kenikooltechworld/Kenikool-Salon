import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { StarIcon } from "@/components/icons";
import axios from "axios";

interface Review {
  id: string;
  author: string;
  rating: number;
  text: string;
  date: string;
  avatar?: string;
}

interface ReviewsSectionProps {
  salonId: string;
}

export function ReviewsSection({ salonId }: ReviewsSectionProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<number | null>(null);

  useEffect(() => {
    const fetchReviews = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`/api/marketplace/salons/${salonId}/reviews`);
        setReviews(response.data);
      } catch (error) {
        console.error("Error fetching reviews:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReviews();
  }, [salonId]);

  const filteredReviews = filter
    ? reviews.filter((review) => review.rating === filter)
    : reviews;

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
        Reviews ({reviews.length})
      </motion.h2>

      {/* Filter Buttons */}
      <motion.div
        className="flex gap-2 flex-wrap"
        variants={itemVariants}
      >
        <motion.button
          onClick={() => setFilter(null)}
          className={`px-4 py-2 rounded-full transition-all ${
            filter === null
              ? "bg-[var(--primary)] text-white"
              : "bg-[var(--muted)] text-[var(--foreground)] hover:bg-[var(--border)]"
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          All
        </motion.button>
        {[5, 4, 3, 2, 1].map((rating) => (
          <motion.button
            key={rating}
            onClick={() => setFilter(rating)}
            className={`px-4 py-2 rounded-full transition-all flex items-center gap-1 ${
              filter === rating
                ? "bg-[var(--primary)] text-white"
                : "bg-[var(--muted)] text-[var(--foreground)] hover:bg-[var(--border)]"
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {rating}
            <StarIcon size={16} className="fill-current" />
          </motion.button>
        ))}
      </motion.div>

      {/* Reviews List */}
      {isLoading ? (
        <motion.div
          className="text-center py-8"
          variants={itemVariants}
        >
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--primary)] mx-auto"></div>
        </motion.div>
      ) : filteredReviews.length === 0 ? (
        <motion.div
          className="text-center py-8 text-[var(--muted-foreground)]"
          variants={itemVariants}
        >
          No reviews found
        </motion.div>
      ) : (
        <motion.div
          className="space-y-4"
          variants={containerVariants}
        >
          {filteredReviews.map((review, index) => (
            <motion.div
              key={review.id}
              className="p-4 border border-[var(--border)] rounded-lg"
              variants={itemVariants}
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-start gap-4">
                {/* Avatar */}
                {review.avatar && (
                  <motion.img
                    src={review.avatar}
                    alt={review.author}
                    className="w-12 h-12 rounded-full object-cover flex-shrink-0"
                    whileHover={{ scale: 1.1 }}
                  />
                )}

                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-[var(--foreground)]">
                      {review.author}
                    </h4>
                    <span className="text-sm text-[var(--muted-foreground)]">
                      {new Date(review.date).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Rating */}
                  <motion.div
                    className="flex items-center gap-1 mb-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 + index * 0.05 }}
                  >
                    {[...Array(5)].map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{
                          delay: 0.3 + i * 0.05 + index * 0.05,
                          type: "spring",
                          stiffness: 200
                        }}
                      >
                        <StarIcon
                          size={16}
                          className={`${
                            i < review.rating
                              ? "text-yellow-400 fill-current"
                              : "text-gray-300"
                          }`}
                        />
                      </motion.div>
                    ))}
                  </motion.div>

                  {/* Review Text */}
                  <p className="text-[var(--muted-foreground)]">
                    {review.text}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
