import { FeaturesSection, LandingFooter } from "@/components/landing";
import { Navbar } from "@/components/Navbar";

export default function Features() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="pt-16">
        <FeaturesSection />
      </main>
      <LandingFooter />
    </div>
  );
}
