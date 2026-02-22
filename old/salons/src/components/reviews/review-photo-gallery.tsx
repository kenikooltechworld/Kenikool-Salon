'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X, ChevronLeft, ChevronRight, Trash2 } from 'lucide-react';

interface Photo {
  id: string;
  url: string;
  uploaded_at?: string;
}

interface ReviewPhotoGalleryProps {
  photos: Photo[];
  onDeletePhoto?: (photoId: string) => void;
  canDelete?: boolean;
  isLoading?: boolean;
}

export function ReviewPhotoGallery({
  photos,
  onDeletePhoto,
  canDelete = false,
  isLoading = false
}: ReviewPhotoGalleryProps) {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const [deletingPhotoId, setDeletingPhotoId] = useState<string | null>(null);

  if (!photos || photos.length === 0) {
    return null;
  }

  const currentPhoto = photos[currentPhotoIndex];

  const handlePrevious = () => {
    setCurrentPhotoIndex(prev => (prev === 0 ? photos.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentPhotoIndex(prev => (prev === photos.length - 1 ? 0 : prev + 1));
  };

  const handleDeletePhoto = async (photoId: string) => {
    if (!onDeletePhoto) return;

    setDeletingPhotoId(photoId);
    try {
      await onDeletePhoto(photoId);
    } finally {
      setDeletingPhotoId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Photo Count Badge */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-900">
          Photos ({photos.length})
        </span>
      </div>

      {/* Grid View */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {photos.map((photo, index) => (
          <Card
            key={photo.id}
            className="relative overflow-hidden group cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => {
              setCurrentPhotoIndex(index);
              setLightboxOpen(true);
            }}
          >
            <CardContent className="p-0">
              <img
                src={photo.url}
                alt={`Review photo ${index + 1}`}
                className="w-full h-24 object-cover group-hover:opacity-75 transition-opacity"
              />

              {/* Overlay on hover */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all flex items-center justify-center">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <ChevronRight size={24} className="text-white" />
                </div>
              </div>

              {/* Delete button */}
              {canDelete && onDeletePhoto && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeletePhoto(photo.id);
                  }}
                  disabled={deletingPhotoId === photo.id || isLoading}
                  className="absolute top-1 right-1 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white rounded-full p-1 transition-colors opacity-0 group-hover:opacity-100"
                  title="Delete photo"
                >
                  <Trash2 size={14} />
                </button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Lightbox Modal */}
      {lightboxOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="relative w-full max-w-4xl">
            {/* Close button */}
            <button
              onClick={() => setLightboxOpen(false)}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 transition-colors"
              title="Close"
            >
              <X size={32} />
            </button>

            {/* Main image */}
            <div className="relative bg-black rounded-lg overflow-hidden">
              <img
                src={currentPhoto.url}
                alt={`Review photo ${currentPhotoIndex + 1}`}
                className="w-full h-auto max-h-[70vh] object-contain"
              />

              {/* Navigation buttons */}
              {photos.length > 1 && (
                <>
                  <button
                    onClick={handlePrevious}
                    className="absolute left-4 top-1/2 -translate-y-1/2 bg-white bg-opacity-20 hover:bg-opacity-40 text-white rounded-full p-2 transition-all"
                    title="Previous photo"
                  >
                    <ChevronLeft size={24} />
                  </button>
                  <button
                    onClick={handleNext}
                    className="absolute right-4 top-1/2 -translate-y-1/2 bg-white bg-opacity-20 hover:bg-opacity-40 text-white rounded-full p-2 transition-all"
                    title="Next photo"
                  >
                    <ChevronRight size={24} />
                  </button>
                </>
              )}
            </div>

            {/* Photo counter */}
            {photos.length > 1 && (
              <div className="text-center mt-4 text-white">
                <p className="text-sm">
                  {currentPhotoIndex + 1} of {photos.length}
                </p>
              </div>
            )}

            {/* Thumbnail strip */}
            {photos.length > 1 && (
              <div className="flex gap-2 mt-4 overflow-x-auto pb-2">
                {photos.map((photo, index) => (
                  <button
                    key={photo.id}
                    onClick={() => setCurrentPhotoIndex(index)}
                    className={`flex-shrink-0 w-16 h-16 rounded overflow-hidden border-2 transition-all ${
                      index === currentPhotoIndex
                        ? 'border-white'
                        : 'border-gray-600 opacity-60 hover:opacity-100'
                    }`}
                  >
                    <img
                      src={photo.url}
                      alt={`Thumbnail ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
