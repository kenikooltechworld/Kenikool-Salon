import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section className="py-12 sm:py-16 md:py-20 px-4 sm:px-6 bg-[var(--muted)]/30">
      <div className="container mx-auto text-center max-w-3xl animate__animated animate__fadeInUp">
        <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-4">
          Start Managing Your Salon Today
        </h2>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground mb-8 px-2">
          Join 500+ Nigerian salons using Kenikool. Start your 30-day free trial
          now - no credit card required.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-2">
          <Link to="/register" className="w-full sm:w-auto">
            <Button
              size="lg"
              variant="primary"
              className="w-full sm:w-auto text-sm sm:text-base"
            >
              Start Free 30-Day Trial
            </Button>
          </Link>
          <Link to="/salons" className="w-full sm:w-auto">
            <Button
              size="lg"
              variant="outline"
              className="w-full sm:w-auto text-sm sm:text-base"
            >
              Browse Salon Directory
            </Button>
          </Link>
        </div>
        <p className="text-xs sm:text-sm text-muted-foreground mt-6 px-2">
          Questions? Contact our sales team for a personalized demo
        </p>
      </div>
    </section>
  );
}
