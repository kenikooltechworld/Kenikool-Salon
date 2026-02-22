import { useState, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { StarIcon } from "@/components/icons";
import { X, Image as ImageIcon } from "lucide-react";

interface ReviewSubmissionProps {
  isOpen: boolean;
  onClose: () => void;
  bookingId: string;
  stylistId: string;
  stylistName: string;
  serviceName: string;
}

interface PhotoFile {
  id: string;
  file: File;
  preview: string;
  uploading?: boolean;
}

export function ReviewSubmission({
  isOpen,
  onClose,
  bookingId,
  stylistId,
  stylistName,
  serviceName,
}: ReviewSubmissionProps) {
  const { toast } = useToast();
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [reviewText, setReviewText] = useState("");
  const [photos, setPhotos] = useState<PhotoFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragOverRef = useRef(false);

  const submitReviewMutation = useMutation({
    mutationFn: async () => {
      // Create review first
      const response = await apiClient.post("/api/reviews", {
        booking_id: bookingId,
        stylist_id: stylistId,
        rating: rating,
        comment: reviewText,
      });
      
      const reviewId = response.data._id;
      
      // Upload photos if any
      if (photos.length > 0) {
        for (const photo of photos) {
          const formData = new FormData();
          formData.append("file", photo.file);
          
          try {
            await apiClient.post(`/api/reviews/${reviewId}/photos`, formData, {
              headers: {
                "Content-Type": "multipart/form-data",
              },
            });
          } catch (error) {
            console.error("Failed to upload photo:", error);
            // Continue with other photos even if one fails
          }
        }
      }
      
      return response.data;
    },
    onSuccess: () => {
      toast("Review submitted successfully", "success");
      setRating(0);
      setReviewText("");
      setPhotos([]);
      onClose();
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Failed to submit review",
        "error"
      );
    },
  });

  const validateFile = (file: File): boolean => {
    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (!validTypes.includes(file.type)) {
      toast("Invalid file type. Please use JPEG, PNG, or WebP", "error");
      return false;
    }

    if (file.size > maxSize) {
      toast("File size exceeds 5MB limit", "error");
      return false;
    }

    return true;
  };

  const handlePhotoSelect = (files: FileList | null) => {
    if (!files) return;

    const newPhotos: PhotoFile[] = [];
    const remainingSlots = 5 - photos.length;

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
          setPhotos((prev) => [...prev, ...newPhotos]);
        }
      };
      reader.readAsDataURL(file);
    }

    if (files.length > remainingSlots) {
      toast(
        `Only ${remainingSlots} more photo(s) can be added (max 5 total)`,
        "warning"
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
    setPhotos((prev) => prev.filter((p) => p.id !== id));
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      toast("Please select a rating", "error");
      return;
    }

    if (!reviewText.trim()) {
      toast("Please write a review", "error");
      return;
    }

    await submitReviewMutation.mutateAsync();
  };

  const getRatingLabel = (rate: number) => {
    switch (rate) {
      case 1:
        return "Poor";
      case 2:
        return "Fair";
      case 3:
        return "Good";
      case 4:
        return "Very Good";
      case 5:
        return "Excellent";
      default:
        return "";
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="md">
      <ModalHeader>
        <ModalTitle>Share Your Experience</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-6">
        {/* Service Info */}
        <Card>
          <CardContent className="pt-4 space-y-2">
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">Service</p>
              <p className="font-semibold text-[var(--foreground)]">
                {serviceName}
              </p>
            </div>
            <div>
              <p className="text-sm text-[var(--muted-foreground)]">Stylist</p>
              <p className="font-semibold text-[var(--foreground)]">
                {stylistName}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Rating Selection */}
        <div>
          <Label className="text-[var(--foreground)] mb-3 block">
            How would you rate your experience?
          </Label>
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => setRating(star)}
                  className="transition-transform hover:scale-110"
                >
                  <StarIcon
                    size={32}
                    className={
                      star <= (hoverRating || rating)
                        ? "text-[var(--warning)] fill-[var(--warning)]"
                        : "text-[var(--muted)]"
                    }
                  />
                </button>
              ))}
            </div>
            {rating > 0 && (
              <span className="text-sm font-semibold text-[var(--foreground)]">
                {getRatingLabel(rating)}
              </span>
            )}
          </div>
        </div>

        {/* Review Text */}
        <div>
          <Label required>Your Review</Label>
          <Input
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            placeholder="Share your experience with this service and stylist..."
            className="mt-2 min-h-24"
            maxLength={1000}
          />
          <p className="text-xs text-[var(--muted-foreground)] mt-1">
            {reviewText.length}/1000 characters
          </p>
        </div>

        {/* Photo Upload */}
        <div>
          <Label>Add Photos (Optional)</Label>
          <p className="text-xs text-[var(--muted-foreground)] mb-2">
            Upload up to 5 photos (JPEG, PNG, or WebP, max 5MB each)
          </p>

          {/* Drag and Drop Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
              dragOverRef.current
                ? "border-blue-500 bg-blue-50"
                : "border-gray-300 hover:border-gray-400"
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
            <p className="text-sm font-medium text-[var(--foreground)]">
              Drag photos here or click to browse
            </p>
            <p className="text-xs text-[var(--muted-foreground)] mt-1">
              {photos.length}/5 photos selected
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

        {/* Tips */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm font-semibold text-blue-900 mb-2">
            Tips for a helpful review:
          </p>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Be specific about what you liked or didn't like</li>
            <li>• Mention the stylist's professionalism and skill</li>
            <li>• Share details about the service quality</li>
            <li>• Be honest and constructive</li>
          </ul>
        </div>
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Skip
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={
            submitReviewMutation.isPending ||
            rating === 0 ||
            !reviewText.trim()
          }
        >
          {submitReviewMutation.isPending ? "Submitting..." : "Submit Review"}
        </Button>
      </ModalFooter>
    </Modal>
  );
}
