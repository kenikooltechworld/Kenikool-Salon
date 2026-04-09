import { usePublicTestimonials } from "@/hooks/usePublicTestimonials";
import { Card, Spinner, Alert } from "@/components/ui";
import { useState } from "react";

export default function PublicTestimonialsSection() {
  const { testimonials, loading, error } = usePublicTestimonials(5);
  const [currentIndex, setCurrentIndex] = useState(0);

  if (loading) {
    return (
      <div className="w-full py-16 px-4 flex justify-center">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full py-16 px-4">
        <Alert variant="error">
          <p>{error}</p>
        </Alert>
      </div>
    );
  }

  if (testimonials.length === 0) {
    return null;
  }

  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
  const itemsPerView = isMobile ? 1 : 3;
  const visibleTestimonials = testimonials.slice(
    currentIndex,
    currentIndex + itemsPerView,
  );

  const handleNext = () => {
    if (currentIndex + itemsPerView < testimonials.length) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  return (
    <section className="w-full py-16 px-4 sm:px-6 lg:px-8 bg-muted/50">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">
          What Our Customers Say
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {visibleTestimonials.map((testimonial) => (
            <Card key={testimonial.id} className="p-6">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <span
                    key={`star-${testimonial.id}-${i}`}
                    className={`text-lg ${
                      i < testimonial.rating
                        ? "text-yellow-400"
                        : "text-gray-300"
                    }`}
                  >
                    ★
                  </span>
                ))}
              </div>
              <p className="text-muted-foreground mb-4">
                {testimonial.reviewText}
              </p>
              <p className="font-semibold">{testimonial.customerName}</p>
            </Card>
          ))}
        </div>

        {testimonials.length > itemsPerView && (
          <div className="flex justify-center gap-4">
            <button
              onClick={handlePrev}
              disabled={currentIndex === 0}
              className="px-4 py-2 border rounded-lg disabled:opacity-50"
            >
              ← Previous
            </button>
            <button
              onClick={handleNext}
              disabled={currentIndex + itemsPerView >= testimonials.length}
              className="px-4 py-2 border rounded-lg disabled:opacity-50"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
