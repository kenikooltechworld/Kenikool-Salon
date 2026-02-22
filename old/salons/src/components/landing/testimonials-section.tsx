import { Card, CardContent } from "@/components/ui/card";
import { StarIcon, PlayIcon } from "@/components/icons";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination, Autoplay } from "swiper/modules";
import { useState } from "react";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

interface Testimonial {
  name: string;
  role: string;
  salon: string;
  location?: string;
  content: string;
  rating: number;
  photoUrl: string;
  videoUrl?: string;
  isVideo?: boolean;
}

interface VideoPlayerProps {
  videoUrl: string;
  thumbnailUrl: string;
  onClose: () => void;
}

function VideoPlayer({ videoUrl, thumbnailUrl, onClose }: VideoPlayerProps) {
  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl">
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 text-white hover:text-gray-300 text-2xl"
          aria-label="Close video"
        >
          ✕
        </button>
        <div
          className="relative w-full bg-black rounded-lg overflow-hidden"
          style={{ paddingBottom: "56.25%" }}
        >
          <iframe
            src={videoUrl}
            title="Video testimonial"
            className="absolute inset-0 w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </div>
    </div>
  );
}

interface TestimonialCardProps {
  testimonial: Testimonial;
  onPlayVideo?: (videoUrl: string, thumbnailUrl: string) => void;
}

function TestimonialCard({ testimonial, onPlayVideo }: TestimonialCardProps) {
  return (
    <Card hover>
      <CardContent className="pt-6">
        <div className="flex gap-1 mb-4">
          {[...Array(testimonial.rating)].map((_, i) => (
            <StarIcon
              key={i}
              size={20}
              className="text-[var(--warning)] fill-current"
            />
          ))}
        </div>
        <p className="text-[var(--muted-foreground)] mb-4">
          &ldquo;{testimonial.content}&rdquo;
        </p>
        <div className="border-t border-[var(--border)] pt-4">
          {testimonial.isVideo && testimonial.videoUrl ? (
            <div className="mb-4">
              <div
                className="relative w-full bg-black rounded-lg overflow-hidden cursor-pointer group"
                style={{ paddingBottom: "56.25%" }}
                onClick={() =>
                  onPlayVideo?.(testimonial.videoUrl!, testimonial.photoUrl)
                }
              >
                <img
                  src={testimonial.photoUrl}
                  alt={testimonial.name}
                  className="absolute inset-0 w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/40 group-hover:bg-black/50 transition-colors flex items-center justify-center">
                  <div className="w-16 h-16 bg-white/90 rounded-full flex items-center justify-center group-hover:bg-white transition-colors">
                    <PlayIcon size={32} className="text-black ml-1" />
                  </div>
                </div>
              </div>
            </div>
          ) : null}
          <div className="flex items-center gap-3">
            <div className="relative w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
              <img
                src={testimonial.photoUrl}
                alt={testimonial.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <p className="font-semibold">{testimonial.name}</p>
              <p className="text-sm text-[var(--muted-foreground)]">
                {testimonial.role}
                {testimonial.salon && `, ${testimonial.salon}`}
              </p>
              {testimonial.location && (
                <p className="text-xs text-[var(--muted-foreground)]">
                  {testimonial.location}
                </p>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function TestimonialsSection() {
  const [playingVideo, setPlayingVideo] = useState<{
    url: string;
    thumbnail: string;
  } | null>(null);

  const testimonials: Testimonial[] = [
    {
      name: "Chioma Adeyemi",
      role: "Owner",
      salon: "Glam Beauty Lounge",
      location: "Lagos",
      content:
        "Kenikool transformed how we run our salon. The POS system works perfectly even when internet is down, and our clients love the online booking feature.",
      rating: 5,
      photoUrl:
        "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&h=200&fit=crop&auto=format&q=80",
    },
    {
      name: "Ibrahim Musa",
      role: "Manager",
      salon: "Elite Cuts",
      location: "Abuja",
      content:
        "The staff management and commission tracking features save us hours every week. The analytics help us make better business decisions.",
      rating: 5,
      photoUrl:
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format&q=80",
    },
    {
      name: "Blessing Okafor",
      role: "Owner",
      salon: "Divine Touch Spa",
      location: "Port Harcourt",
      content:
        "Best investment for our salon! The automated SMS reminders reduced no-shows by 60%. Customer support is excellent too.",
      rating: 5,
      photoUrl:
        "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&h=200&fit=crop&auto=format&q=80",
    },
    {
      name: "Amara Obi",
      role: "Owner",
      salon: "Radiant Beauty Hub",
      location: "Enugu",
      content:
        "The online booking system increased our bookings by 40%. Clients appreciate the convenience and we love the automated reminders.",
      rating: 5,
      photoUrl:
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format&q=80",
      isVideo: true,
      videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ",
    },
    {
      name: "Tunde Adebayo",
      role: "Manager",
      salon: "Premium Styles",
      location: "Ibadan",
      content:
        "The inventory management system is a game-changer. We never run out of supplies and waste has decreased significantly.",
      rating: 5,
      photoUrl:
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&auto=format&q=80",
    },
    {
      name: "Zainab Hassan",
      role: "Owner",
      salon: "Essence Beauty",
      location: "Kano",
      content:
        "Customer support is outstanding. They helped us set up everything and are always available when we need assistance.",
      rating: 5,
      photoUrl:
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format&q=80",
    },
  ];

  return (
    <section className="py-16 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            Loved by Salon Owners Across Nigeria
          </h2>
          <p className="text-xl text-[var(--muted-foreground)]">
            See what our customers have to say
          </p>
        </div>

        <div className="max-w-7xl mx-auto">
          <Swiper
            modules={[Navigation, Pagination, Autoplay]}
            spaceBetween={24}
            slidesPerView={1}
            breakpoints={{
              640: {
                slidesPerView: 1,
              },
              768: {
                slidesPerView: 2,
              },
              1024: {
                slidesPerView: 3,
              },
            }}
            navigation={{
              nextEl: ".testimonials-button-next",
              prevEl: ".testimonials-button-prev",
            }}
            pagination={{
              clickable: true,
              dynamicBullets: true,
            }}
            autoplay={{
              delay: 5000,
              disableOnInteraction: false,
              pauseOnMouseEnter: true,
            }}
            loop={true}
            className="testimonials-swiper"
          >
            {testimonials.map((testimonial, index) => (
              <SwiperSlide key={index}>
                <TestimonialCard
                  testimonial={testimonial}
                  onPlayVideo={(url, thumbnail) =>
                    setPlayingVideo({ url, thumbnail })
                  }
                />
              </SwiperSlide>
            ))}
          </Swiper>

          {/* Navigation Arrows */}
          <div className="flex justify-center gap-4 mt-8">
            <button
              className="testimonials-button-prev w-10 h-10 rounded-full border border-[var(--border)] hover:bg-[var(--accent)] transition-colors flex items-center justify-center"
              aria-label="Previous testimonial"
            >
              ←
            </button>
            <button
              className="testimonials-button-next w-10 h-10 rounded-full border border-[var(--border)] hover:bg-[var(--accent)] transition-colors flex items-center justify-center"
              aria-label="Next testimonial"
            >
              →
            </button>
          </div>
        </div>
      </div>

      {/* Video Player Modal */}
      {playingVideo && (
        <VideoPlayer
          videoUrl={playingVideo.url}
          thumbnailUrl={playingVideo.thumbnail}
          onClose={() => setPlayingVideo(null)}
        />
      )}
    </section>
  );
}
