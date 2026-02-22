import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { BenefitItem } from "./benefit-item";

export function BenefitsSection() {
  const benefits = [
    {
      title: "Built for Nigeria",
      description:
        "Naira pricing, Paystack integration, and Termii SMS support",
    },
    {
      title: "Works Offline",
      description: "Continue taking payments even without internet connection",
    },
    {
      title: "Secure & Reliable",
      description: "Your data is protected with enterprise-grade security",
    },
    {
      title: "24/7 Support",
      description: "Get help whenever you need it from our support team",
    },
    {
      title: "Easy to Use",
      description: "Intuitive interface designed for salon owners and staff",
    },
    {
      title: "Mobile Friendly",
      description: "Manage your salon from anywhere, on any device",
    },
  ];

  return (
    <section className="py-12 sm:py-16 md:py-20 px-4 sm:px-6">
      <div className="container mx-auto max-w-6xl">
        <div className="grid md:grid-cols-2 gap-8 md:gap-12 items-center">
          <div className="animate__animated animate__fadeInLeft">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-6">
              Why Choose Kenikool?
            </h2>
            <div className="space-y-4">
              {benefits.map((benefit, index) => (
                <div
                  key={index}
                  className="animate__animated animate__fadeInUp"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <BenefitItem {...benefit} />
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-6 animate__animated animate__fadeInRight">
            {/* Image Showcase */}
            <div className="relative h-48 sm:h-56 md:h-64 rounded-[var(--radius-lg)] overflow-hidden">
              <img
                src="https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&h=600&fit=crop&auto=format&q=80"
                alt="Salon staff using Kenikool POS system"
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>

            {/* CTA Card */}
            <Card variant="gradient">
              <CardContent className="p-6 sm:p-8">
                <h3 className="text-xl sm:text-2xl font-bold mb-4">
                  Ready to Transform Your Salon?
                </h3>
                <p className="mb-6 opacity-90 text-sm sm:text-base">
                  Join hundreds of Nigerian salons already using Kenikool to
                  streamline their operations and grow their business.
                </p>
                <div className="mb-6 space-y-2 text-xs sm:text-sm opacity-90">
                  <p>✓ 30-day free trial</p>
                  <p>✓ No credit card required</p>
                  <p>✓ Cancel anytime</p>
                  <p>✓ Full access to all features</p>
                </div>
                <Link to="/register">
                  <Button
                    size="lg"
                    variant="outline"
                    fullWidth
                    className="border-white text-white hover:bg-white/20 text-sm sm:text-base"
                  >
                    Start Your Free Trial
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
