import { useState, useEffect } from "react";
import { get } from "@/lib/utils/api";

interface Testimonial {
  id: string;
  customerName: string;
  rating: number;
  reviewText: string;
  createdAt: string;
}

export function usePublicTestimonials(limit: number = 5) {
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTestimonials = async () => {
      try {
        setLoading(true);
        const data = await get<Testimonial[]>(
          `/public/bookings/testimonials?limit=${limit}`,
        );
        setTestimonials(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch testimonials",
        );
        setTestimonials([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTestimonials();
  }, [limit]);

  return { testimonials, loading, error };
}
