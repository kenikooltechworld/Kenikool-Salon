import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeftIcon, ChevronRightIcon } from "@/components/icons";

interface Promotion {
  id: string;
  title: string;
  description: string;
  discount: number;
  code: string;
  expiryDate: string;
}

interface PromotionsCarouselProps {
  promotions?: Promotion[];
}

export function PromotionsCarousel({
  promotions = [],
}: PromotionsCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? promotions.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === promotions.length - 1 ? 0 : prev + 1));
  };

  if (promotions.length === 0) {
    return null;
  }

  const current = promotions[currentIndex];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Current Promotions</h3>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrevious}
            disabled={promotions.length <= 1}
          >
            <ChevronLeftIcon size={16} />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNext}
            disabled={promotions.length <= 1}
          >
            <ChevronRightIcon size={16} />
          </Button>
        </div>
      </div>

      <Card className="p-6 bg-gradient-to-r from-primary/10 to-primary/5">
        <div className="space-y-3">
          <h4 className="text-xl font-bold">{current.title}</h4>
          <p className="text-muted-foreground">{current.description}</p>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Discount</p>
              <p className="text-2xl font-bold text-primary">
                {current.discount}%
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Code</p>
              <p className="text-lg font-mono font-semibold">{current.code}</p>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Expires: {new Date(current.expiryDate).toLocaleDateString()}
          </p>
        </div>
      </Card>

      <div className="flex justify-center gap-2">
        {promotions.map((_, idx) => (
          <Button
            key={idx}
            variant="outline"
            size="sm"
            onClick={() => setCurrentIndex(idx)}
            className={`h-2 rounded-full transition-all ${
              idx === currentIndex ? "bg-primary w-6" : "bg-muted w-2"
            }`}
            aria-label={`Go to promotion ${idx + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
