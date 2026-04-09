import { usePublicBookingStatistics } from "@/hooks/usePublicBookingStatistics";
import { Card, Spinner } from "@/components/ui";
import { useEffect, useState } from "react";

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  suffix?: string;
}

function AnimatedCounter({
  value,
  duration = 2000,
  suffix = "",
}: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationId: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      setDisplayValue(Math.floor(value * progress));

      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, [value, duration]);

  return (
    <span>
      {displayValue}
      {suffix}
    </span>
  );
}

export default function PublicBookingStatistics() {
  const { statistics, loading } = usePublicBookingStatistics();

  if (loading) {
    return (
      <div className="w-full py-16 px-4 flex justify-center">
        <Spinner />
      </div>
    );
  }

  if (!statistics) {
    return null;
  }

  return (
    <section className="w-full py-16 px-4 sm:px-6 lg:px-8 bg-primary/5">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">Why Choose Us</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="p-8 text-center">
            <div className="text-4xl font-bold mb-2">
              <AnimatedCounter value={statistics.totalBookings} />
            </div>
            <p className="text-muted-foreground">Happy Customers</p>
          </Card>

          <Card className="p-8 text-center">
            <div className="text-4xl font-bold mb-2">
              <AnimatedCounter
                value={Math.round(statistics.averageRating * 10)}
                suffix="/10"
              />
            </div>
            <p className="text-muted-foreground">Average Rating</p>
          </Card>

          <Card className="p-8 text-center">
            <div className="text-4xl font-bold mb-2">
              <AnimatedCounter
                value={statistics.responseTimeMinutes}
                suffix=" min"
              />
            </div>
            <p className="text-muted-foreground">Average Response Time</p>
          </Card>
        </div>
      </div>
    </section>
  );
}
