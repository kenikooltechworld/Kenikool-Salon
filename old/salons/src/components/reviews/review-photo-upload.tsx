'use client';

import React, { useRef, useState } from 'react';
import { X, Image as ImageIcon } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface PhotoFile {
  id: string;
  file: File;
  preview: string;
}

interface ReviewPhotoUploadProps {
  onPhotosSelected: (photos: PhotoFile[]) => void;
  maxPhotos?: number;
  maxFileSize?: number; // in bytes
  acceptedFormats?: string[];
}

export function ReviewPhotoUpload({
  onPhotosSelected,
  maxPhotos = 5,
  maxFileSize = 5 * 1024 * 1024, // 5MB
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
}: ReviewPhotoUploadProps) {
  const { toast } = useToast();
  const [photos, setPhotos] = useState<PhotoFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragOverRef = useRef(false);

  const validateFile = (file: File): boolean => {
    if (!acceptedFormats.includes(file.type)) {
      toast('Invalid file type. Please use JPEG, PNG, or WebP', 'error');
      return false;
    }

    if (file.size > maxFileSize) {
      toast('File size exceeds 5MB limit', 'error');
      return false;
    }

    return true;
  };

  const handlePhotoSelect = (files: FileList | null) => {
    if (!files) return;

    const newPhotos: PhotoFile[] = [];
    const remainingSlots = maxPhotos - photos.length;

    for (let i = 0; i < Math.min(files.length, remainingSlots); i++) {
      const file = files[i];

      if (!validateFile(file)) {
        continue;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        newPhotos.push({
          id: `${Date.now()}-${i}`,
          file,
          preview: e.target?.result as string,
        });

        if (newPhotos.length === Math.min(files.length, remainingSlots)) {
          const updatedPhotos = [...photos, ...newPhotos];
          setPhotos(updatedPhotos);
          onPhotosSelected(updatedPhotos);
        }
      };
      reader.readAsDataURL(file);
    }

    if (files.length > remainingSlots) {
      toast(
        `Only ${remainingSlots} more photo(s) can be added (max ${maxPhotos} total)`,
        'warning'
      );
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    dragOverRef.current = true;
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    dragOverRef.current = false;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    dragOverRef.current = false;
    handlePhotoSelect(e.dataTransfer.files);
  };

  const removePhoto = (id: string) => {
    const updatedPhotos = photos.filter((p) => p.id !== id);
    setPhotos(updatedPhotos);
    onPhotosSelected(updatedPhotos);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">
          Add Photos (Optional)
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Upload up to {maxPhotos} photos (JPEG, PNG, or WebP, max 5MB each)
        </p>

        {/* Drag and Drop Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
            dragOverRef.current
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => handlePhotoSelect(e.target.files)}
            className="hidden"
          />
          <ImageIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
          <p className="text-sm font-medium text-gray-900">
            Drag photos here or click to browse
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {photos.length}/{maxPhotos} photos selected
          </p>
        </div>

        {/* Photo Previews */}
        {photos.length > 0 && (
          <div className="mt-4 grid grid-cols-5 gap-2">
            {photos.map((photo) => (
              <div
                key={photo.id}
                className="relative group rounded-lg overflow-hidden bg-gray-100"
              >
                <img
                  src={photo.preview}
                  alt="Preview"
                  className="w-full h-20 object-cover"
                />
                <button
                  onClick={() => removePhoto(photo.id)}
                  className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
