import { Button } from "@/components/ui";

interface PublicHeroSectionProps {
  salonName: string;
  salonDescription: string;
  salonLogo?: string;
  primaryColor?: string;
  secondaryColor?: string;
  onBookNowClick?: () => void;
}

export default function PublicHeroSection({
  salonName,
  salonDescription,
  salonLogo,
  primaryColor = "#000000",
  secondaryColor = "#666666",
  onBookNowClick,
}: PublicHeroSectionProps) {
  return (
    <div
      className="relative w-full py-20 px-4 sm:px-6 lg:px-8 text-center"
      style={{
        background: `linear-gradient(135deg, ${primaryColor}15 0%, ${secondaryColor}15 100%)`,
      }}
    >
      <div className="max-w-4xl mx-auto">
        {salonLogo && (
          <img
            src={salonLogo}
            alt={salonName}
            className="h-16 w-16 mx-auto mb-6 rounded-lg object-cover"
          />
        )}

        <h1
          className="text-4xl sm:text-5xl font-bold mb-4 animate-fade-in"
          style={{ color: primaryColor }}
        >
          {salonName}
        </h1>

        <p className="text-lg sm:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          {salonDescription}
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onBookNowClick}
          style={{ backgroundColor: primaryColor }}
          className="hover:opacity-90 transition-opacity"
        >
          Book Now
        </Button>
      </div>
    </div>
  );
}
