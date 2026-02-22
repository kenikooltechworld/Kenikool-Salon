import { useParams } from "react-router-dom";
import { Salon } from "@/lib/types/salon";
import { useServices } from "@/lib/api/hooks/useServices";
import { useReviews } from "@/lib/api/hooks/useReviews";
import { ServiceCard } from "@/components/booking/service-card";
import { ReviewCard } from "@/components/booking/review-card";
import { WaitlistForm } from "@/components/booking/waitlist-form";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ScissorsIcon,
  StarIcon,
  SparklesIcon,
  ClockIcon,
} from "@/components/icons";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export default function BookingPage() {
  const { subdomain } = useParams<{ subdomain: string }>();
  const [showWaitlist, setShowWaitlist] = useState(false);

  // Fetch salon by subdomain
  const { data: salon, isLoading: salonLoading } = useQuery({
    queryKey: ["salon", subdomain],
    queryFn: async () => {
      const response = await apiClient.get<Salon>(
        `/api/tenants/subdomain/${subdomain}`
      );
      return response.data;
    },
  });

  // Fetch services for the salon
  const { data: services, isLoading: servicesLoading } = useServices(
    {
      is_active: true,
    },
    {
      enabled: !!salon?.id,
    }
  );

  // Fetch reviews for the salon
  const { data: reviewsResponse } = useReviews(
    {
      limit: 6,
    },
    {
      enabled: !!salon?.id,
    }
  );

  const reviews = reviewsResponse?.reviews || [];

  if (salonLoading) {
    return (
      <div className="min-h-screen bg-background p-8">
        <div className="container mx-auto max-w-6xl">
          <Skeleton className="h-32 w-full mb-8" />
          <div className="grid md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-64" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!salon) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <ScissorsIcon
              size={48}
              className="mx-auto mb-4 text-muted-foreground"
            />
            <h1 className="text-2xl font-bold mb-2">Salon Not Found</h1>
            <p className="text-muted-foreground">
              The salon you&apos;re looking for doesn&apos;t exist or has been
              removed.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b-2 border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center gap-4">
            {salon.logo && (
              <img
                src={salon.logo}
                alt={salon.businessName}
                className="w-16 h-16 rounded-lg object-cover"
              />
            )}
            <div>
              <h1 className="text-3xl font-bold">{salon.businessName}</h1>
              {salon.description && (
                <p className="text-muted-foreground mt-1">
                  {salon.description}
                </p>
              )}
              <div className="flex gap-2 mt-2">
                <Badge variant="default">
                  <SparklesIcon size={14} />
                  Online Booking
                </Badge>
                {reviews.length > 0 && (
                  <Badge variant="accent">
                    <StarIcon size={14} />
                    {(
                      reviews.reduce((acc, r) => acc + r.rating, 0) /
                      reviews.length
                    ).toFixed(1)}{" "}
                    Rating
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        {/* Services Section */}
        <section className="mb-16">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-3xl font-bold">Our Services</h2>
            <Button variant="outline" onClick={() => setShowWaitlist(true)}>
              <ClockIcon size={18} />
              Join Waitlist
            </Button>
          </div>
          {servicesLoading ? (
            <div className="grid md:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-80" />
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {services?.map((service) => (
                <ServiceCard key={service.id} service={service} salon={salon} />
              ))}
            </div>
          )}
        </section>

        {/* Reviews Section */}
        {reviews.length > 0 && (
          <section>
            <h2 className="text-3xl font-bold mb-6">Client Reviews</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reviews.map((review) => (
                <ReviewCard key={review.id} review={review} />
              ))}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-border bg-card mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold mb-2">Contact</h3>
              <p className="text-sm text-muted-foreground">{salon.phone}</p>
              <p className="text-sm text-muted-foreground">{salon.email}</p>
            </div>
            <div>
              <h3 className="font-bold mb-2">Location</h3>
              <p className="text-sm text-muted-foreground">{salon.address}</p>
            </div>
            <div>
              <h3 className="font-bold mb-2">Powered by</h3>
              <p className="text-sm text-muted-foreground">
                Kenikool Salon Management
              </p>
            </div>
          </div>
        </div>
      </footer>

      <WaitlistForm
        isOpen={showWaitlist}
        onClose={() => setShowWaitlist(false)}
        salon={salon}
      />
    </div>
  );
}
