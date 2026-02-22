import { useState } from "react";
import { UploadIcon, TrashIcon, CheckCircleIcon } from "@/components/icons";

interface LocationImageUploadProps {
  images: any[];
  onImagesChange: (images: any[]) => void;
  maxImages?: number;
  maxFileSize?: number;
}

export function LocationImageUpload({
  images,
  onImagesChange,
  maxImages = 10,
  maxFileSize = 5,
}: LocationImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    if (!file.type.startsWith("image/")) {
      setError("Only image files are allowed");
      return false;
    }

    if (file.size > maxFileSize * 1024 * 1024) {
      setError(`File size must be less than ${maxFileSize}MB`);
      return false;
    }

    return true;
  };

  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    setError(null);

    const newImages = Array.from(files).filter((file) => {
      if (!validateFile(file)) return false;
      if (images.length + 1 > maxImages) {
        setError(`Maximum ${maxImages} images allowed`);
        return false;
      }
      return true;
    });

    if (newImages.length > 0) {
      const imageObjects = newImages.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
        is_primary: images.length === 0 && newImages.indexOf(file) === 0,
      }));

      onImagesChange([...images, ...imageObjects]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    if (images[index].preview) {
      URL.revokeObjectURL(images[index].preview);
    }
    onImagesChange(newImages);
  };

  const setPrimaryImage = (index: number) => {
    const newImages = images.map((img, i) => ({
      ...img,
      is_primary: i === index,
    }));
    onImagesChange(newImages);
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border bg-muted/30 hover:border-primary/50"
        }`}
      >
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
          id="image-upload"
        />
        <label htmlFor="image-upload" className="cursor-pointer">
          <div className="flex flex-col items-center gap-2">
            <UploadIcon size={32} className="text-muted-foreground" />
            <div>
              <p className="font-medium text-foreground">
                Drag images here or click to select
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                PNG, JPG, GIF up to {maxFileSize}MB
              </p>
            </div>
          </div>
        </label>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/30 text-destructive rounded-md text-sm">
          {error}
        </div>
      )}

      {/* Image Count */}
      <div className="text-xs text-muted-foreground">
        {images.length} / {maxImages} images
      </div>

      {/* Image Grid */}
      {images.length > 0 && (
        <div className="grid gap-3 md:grid-cols-3">
          {images.map((image, index) => (
            <div
              key={index}
              className="relative group rounded-lg overflow-hidden border border-border"
            >
              <img
                src={image.preview || image.url}
                alt={`Location ${index + 1}`}
                className="w-full h-32 object-cover"
              />

              {/* Primary Badge */}
              {image.is_primary && (
                <div className="absolute top-2 left-2 flex items-center gap-1 px-2 py-1 bg-primary text-primary-foreground rounded text-xs font-medium">
                  <CheckCircleIcon size={12} />
                  Primary
                </div>
              )}

              {/* Overlay Actions */}
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                {!image.is_primary && (
                  <button
                    onClick={() => setPrimaryImage(index)}
                    className="px-2 py-1 bg-primary text-primary-foreground rounded text-xs font-medium hover:bg-primary/90 transition-colors"
                  >
                    Set Primary
                  </button>
                )}
                <button
                  onClick={() => removeImage(index)}
                  className="p-1.5 bg-destructive text-destructive-foreground rounded hover:bg-destructive/90 transition-colors"
                >
                  <TrashIcon size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
