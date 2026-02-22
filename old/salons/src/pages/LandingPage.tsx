import {
  LandingFooter,
  HeroSection,
  FeaturesSection,
  HowItWorksSection,
  BenefitsSection,
  SalonDirectorySection,
  PricingPreviewSection,
  FAQSection,
  CTASection,
  TestimonialsSection,
} from "@/components/landing";
import { Navbar } from "@/components/layout/navbar";
import { StickyCTA } from "@/components/landing/sticky-cta";
import { FloatingCTA } from "@/components/landing/floating-cta";
import { ExitIntentPopup } from "@/components/landing/exit-intent-popup";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <Navbar />
      <main className="w-full">
        <section id="hero" className="w-full">
          <HeroSection />
        </section>
        <section id="salons" className="w-full">
          <SalonDirectorySection />
        </section>
        <section id="features" className="w-full">
          <FeaturesSection />
        </section>
        <section className="w-full">
          <HowItWorksSection />
        </section>
        <section className="w-full">
          <BenefitsSection />
        </section>
        <section id="testimonials" className="w-full">
          <TestimonialsSection />
        </section>
        <section id="pricing" className="w-full">
          <PricingPreviewSection />
        </section>
        <section className="w-full">
          <FAQSection />
        </section>
        <section className="w-full">
          <CTASection />
        </section>
      </main>
      <LandingFooter />

      {/* Conversion Elements - Hidden on very small screens */}
      <div className="hidden sm:block">
        <StickyCTA />
        <FloatingCTA />
      </div>
      <ExitIntentPopup />
    </div>
  );
}
