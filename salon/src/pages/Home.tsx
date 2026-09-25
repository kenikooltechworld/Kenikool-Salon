import {
  HeroSection,
  HowItWorksSection,
  BenefitsSection,
  TestimonialsSection,
  PricingPreviewSection,
  FAQSection,
  CTASection,
  StickyCTA,
  FloatingCTA,
  ExitIntentPopup,
} from "@/components/landing";

export default function Home() {
  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <main className="w-full">
        <section id="hero" className="w-full">
          <HeroSection />
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

      {/* Conversion Elements - Hidden on very small screens */}
      <div className="hidden sm:block">
        <StickyCTA />
        <FloatingCTA />
      </div>
      <ExitIntentPopup />
    </div>
  );
}

// 07015010435
