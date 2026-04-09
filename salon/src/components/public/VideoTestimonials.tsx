/**
 * Video Testimonials Component
 * Displays customer video testimonials with play functionality
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, Spinner } from "@/components/ui";
import { PlayIcon, StarIcon, XIcon } from "@/components/icons";
import { apiClient } from "@/lib/utils/api";

interface VideoTestimonial {
  id: string;
  customer_name: string;
  video_url: string;
  thumbnail_url?: string;
  testimonial_text?: string;
  rating: number;
  created_at: string;
}

interface VideoTestimonialsProps {
  limit?: number;
}

export default function VideoTestimonials({
  limit = 6,
}: VideoTestimonialsProps) {
  const [selectedVideo, setSelectedVideo] = useState<VideoTestimonial | null>(
    null,
  );

  const { data: testimonials, isLoading } = useQuery({
    queryKey: ["video-testimonials", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<VideoTestimonial[]>(
        `/social-proof/video-testimonials?limit=${limit}`,
      );
      return data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <Spinner />
      </div>
    );
  }

  if (!testimonials || testimonials.length === 0) {
    return null;
  }

  return (
    <>
      <div className="py-12 px-4 sm:px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2">What Our Customers Say</h2>
            <p className="text-gray-600">Hear from our satisfied customers</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {testimonials.map((testimonial) => (
              <Card
                key={testimonial.id}
                className="overflow-hidden cursor-pointer hover:shadow-lg transition"
                onClick={() => setSelectedVideo(testimonial)}
              >
                <div className="relative aspect-video bg-gray-200">
                  {testimonial.thumbnail_url ? (
                    <img
                      src={testimonial.thumbnail_url}
                      alt={testimonial.customer_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
                      <PlayIcon size={48} className="text-white" />
                    </div>
                  )}

                  {/* Play button overlay */}
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition">
                    <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                      <PlayIcon size={24} className="text-blue-600 ml-1" />
                    </div>
                  </div>
                </div>

                <div className="p-4">
                  <div className="flex items-center gap-1 mb-2">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <StarIcon
                        key={i}
                        size={16}
                        className="text-yellow-400 fill-current"
                      />
                    ))}
                  </div>

                  <h3 className="font-semibold mb-1">
                    {testimonial.customer_name}
                  </h3>

                  {testimonial.testimonial_text && (
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {testimonial.testimonial_text}
                    </p>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Video Modal */}
      {selectedVideo && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedVideo(null)}
        >
          <div
            className="relative w-full max-w-4xl bg-white rounded-lg overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setSelectedVideo(null)}
              className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center transition"
            >
              <XIcon size={20} className="text-white" />
            </button>

            {/* Video player */}
            <div className="aspect-video bg-black">
              <video
                src={selectedVideo.video_url}
                controls
                autoPlay
                className="w-full h-full"
              >
                Your browser does not support the video tag.
              </video>
            </div>

            {/* Video info */}
            <div className="p-6">
              <div className="flex items-center gap-1 mb-2">
                {Array.from({ length: selectedVideo.rating }).map((_, i) => (
                  <StarIcon
                    key={i}
                    size={16}
                    className="text-yellow-400 fill-current"
                  />
                ))}
              </div>

              <h3 className="text-xl font-semibold mb-2">
                {selectedVideo.customer_name}
              </h3>

              {selectedVideo.testimonial_text && (
                <p className="text-gray-600">
                  {selectedVideo.testimonial_text}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
