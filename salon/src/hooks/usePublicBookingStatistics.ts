import { useState, useEffect } from "react";
import { get } from "@/lib/utils/api";

interface Statistics {
  total_bookings: number;
  average_rating: number;
  average_response_time: number;
}

export function usePublicBookingStatistics() {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        setLoading(true);
        const data = await get<Statistics>("/public/bookings/statistics");
        setStatistics(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch statistics",
        );
        setStatistics(null);
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

  return { statistics, loading, error };
}
