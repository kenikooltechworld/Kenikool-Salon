import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { UsersIcon as Users, ClockIcon as Clock } from "@/components/icons";
import { apiClient } from "@/lib/utils/api";

interface BookingActivity {
  id: string;
  customer_name: string;
  service_name: string;
  booking_type: string;
  created_at: string;
}

interface LiveBookingNotificationsProps {
  tenantId?: string;
}

function LiveBookingNotifications({ tenantId }: LiveBookingNotificationsProps) {
  const [activities, setActivities] = useState<BookingActivity[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Fetch recent booking activities
    const fetchActivities = async () => {
      try {
        const { data } = await apiClient.get<BookingActivity[]>(
          "/social-proof/recent-bookings?limit=10&hours=24",
        );
        setActivities(data);
      } catch (error) {
        console.error("Error fetching booking activities:", error);
      }
    };

    fetchActivities();
    const interval = setInterval(fetchActivities, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, [tenantId]);

  useEffect(() => {
    if (activities.length === 0) return;

    // Show notification every 10 seconds
    const showInterval = setInterval(() => {
      setIsVisible(true);
      setCurrentIndex((prev) => (prev + 1) % activities.length);

      // Hide after 5 seconds
      setTimeout(() => {
        setIsVisible(false);
      }, 5000);
    }, 10000);

    // Show first notification after 3 seconds
    setTimeout(() => {
      setIsVisible(true);
      setTimeout(() => setIsVisible(false), 5000);
    }, 3000);

    return () => clearInterval(showInterval);
  }, [activities]);

  if (activities.length === 0) return null;

  const currentActivity = activities[currentIndex];
  if (!currentActivity) return null;

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);

    if (diffInMinutes < 1) return "just now";
    if (diffInMinutes === 1) return "1 minute ago";
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours === 1) return "1 hour ago";
    return `${diffInHours} hours ago`;
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 50, scale: 0.9 }}
          transition={{ duration: 0.3 }}
          className="fixed bottom-6 left-6 z-50 max-w-sm"
        >
          <div className="bg-white rounded-lg shadow-2xl border border-gray-200 p-4 flex items-start gap-3">
            <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Users size={20} className="text-white" />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900">
                {currentActivity.customer_name} just booked
              </p>
              <p className="text-sm text-gray-600 truncate">
                {currentActivity.service_name}
              </p>
              <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
                <Clock size={12} />
                <span>{getTimeAgo(currentActivity.created_at)}</span>
              </div>
            </div>

            <button
              onClick={() => setIsVisible(false)}
              className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition"
              aria-label="Close notification"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default LiveBookingNotifications;
