import { useState } from "react";
import { apiClient } from "@/lib/utils/api";

interface MediaUploadResponse {
  url: string;
  message: string;
}

interface UseImageUploadOptions {
  folder?: string;
  onSuccess?: (url: string) => void;
  onError?: (error: string) => void;
}

export function useImageUpload(options: UseImageUploadOptions = {}) {
  const { folder = "salon-media", onSuccess, onError } = options;

  const [isUploading, setIsUploading] = useState(false);
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
    setError(null);

    try {
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

      // Upload to backend
      const response = await apiClient.post<MediaUploadResponse>(
        "/media/upload",
        {
          base64_data: base64Data,
          media_type: "image",
          folder,
        },
      );

      const url = (response as any).data?.url || "";
      onSuccess?.(url);
      return url;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to upload image";
      setError(errorMessage);
      onError?.(errorMessage);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const clearPreview = () => {
    setPreview(null);
    setError(null);
  };

  return {
    uploadImage,
    handleFileChange,
    isUploading,
    error,
    preview,
    clearPreview,
  };
}
