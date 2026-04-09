import { useState } from "react";
import { apiClient } from "@/lib/utils/api";

interface MediaUploadResponse {
  url: string;
  message: string;
}

interface UseImageUploadOptions {
  folder?: string;
  mediaType?: "image" | "document";
  onSuccess?: (url: string) => void;
  onError?: (error: string) => void;
}

const FILE_SIZE_LIMITS = {
  image: 5 * 1024 * 1024, // 5 MB
  document: 10 * 1024 * 1024, // 10 MB
};

export function useImageUpload(options: UseImageUploadOptions = {}) {
  const {
    folder = "salon-media",
    mediaType = "image",
    onSuccess,
    onError,
  } = options;

  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setError(null);
      // Show preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
    return file;
  };

  const uploadImage = async (file: File): Promise<string> => {
    setIsUploading(true);
    setUploadProgress(0);
    setError(null);

    let progressInterval: NodeJS.Timeout | null = null;

    try {
      // Validate file size
      const maxSize = FILE_SIZE_LIMITS[mediaType];
      if (file.size > maxSize) {
        const maxSizeMB = maxSize / (1024 * 1024);
        const errorMessage = `File size exceeds ${maxSizeMB}MB limit for ${mediaType}s`;
        setError(errorMessage);
        onError?.(errorMessage);
        throw new Error(errorMessage);
      }

      // Phase 1: Smooth file reading progress (0-45%)
      const startReadingProgress = () => {
        let progress = 0;
        progressInterval = setInterval(() => {
          progress += 1;
          if (progress <= 45) {
            setUploadProgress(progress);
          }
        }, 20); // Faster increments for smoother animation
      };

      startReadingProgress();

      // Convert file to base64
      const reader = new FileReader();
      const base64Promise = new Promise<string>((resolve, reject) => {
        reader.onload = () => {
          const result = reader.result as string;
          resolve(result);
        };
        reader.onerror = reject;
      });

      reader.readAsDataURL(file);
      const base64Data = await base64Promise;

      // Clear reading interval and set to 50%
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }
      setUploadProgress(50);

      // Small delay to show 50% milestone
      await new Promise((resolve) => setTimeout(resolve, 100));

      // Phase 2: Smooth upload progress (50-90%)
      const startUploadProgress = () => {
        let progress = 50;
        progressInterval = setInterval(() => {
          progress += 1;
          if (progress <= 90) {
            setUploadProgress(progress);
          }
        }, 25); // Smooth increments
      };

      startUploadProgress();

      // Upload to backend
      const response = await apiClient.post<MediaUploadResponse>(
        "/media/upload",
        {
          base64_data: base64Data,
          media_type: mediaType,
          folder,
        },
      );

      // Clear upload interval
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }

      // Smooth transition to 100%
      setUploadProgress(95);
      await new Promise((resolve) => setTimeout(resolve, 100));
      setUploadProgress(100);

      const url = (response as any).data?.url || "";
      onSuccess?.(url);
      return url;
    } catch (err) {
      // Clear any running intervals on error
      if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
      }

      const errorMessage =
        err instanceof Error ? err.message : "Failed to upload image";
      setError(errorMessage);
      onError?.(errorMessage);
      throw err;
    } finally {
      setIsUploading(false);
      // Reset progress after a short delay
      setTimeout(() => setUploadProgress(0), 500);
    }
  };

  const clearPreview = () => {
    setPreview(null);
    setError(null);
    setUploadProgress(0);
  };

  return {
    uploadImage,
    handleFileChange,
    isUploading,
    uploadProgress,
    error,
    preview,
    clearPreview,
  };
}
