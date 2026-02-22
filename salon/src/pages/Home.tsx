import { Navbar } from "@/components/Navbar";
import {
  HeroSection,
  FeaturesSection,
  HowItWorksSection,
  BenefitsSection,
  TestimonialsSection,
  PricingPreviewSection,
  FAQSection,
  CTASection,
  LandingFooter,
  StickyCTA,
  FloatingCTA,
  ExitIntentPopup,
} from "@/components/landing";

export default function Home() {
  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <Navbar />
      <main className="w-full">
        <section id="hero" className="w-full">
          <HeroSection />
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
