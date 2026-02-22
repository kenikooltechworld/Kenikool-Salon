import { useState, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  UploadIcon,
  TrashIcon,
  UserIcon,
} from "@/components/icons";
import {
  useUploadProfilePicture,
  useDeleteProfilePicture,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

interface ProfilePictureUploadProps {
  currentPictureUrl?: string;
}

export function ProfilePictureUpload({
  currentPictureUrl,
}: ProfilePictureUploadProps) {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const uploadMutation = useUploadProfilePicture({
    onSuccess: () => {
      setSuccessMessage("Profile picture updated successfully");
      setPreview(null);
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to upload profile picture"
      );
    },
  });

  const deleteMutation = useDeleteProfilePicture({
    onSuccess: () => {
      setSuccessMessage("Profile picture deleted successfully");
      setPreview(null);
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to delete profile picture"
      );
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!validTypes.includes(file.type)) {
      setErrorMessage("Only JPEG, PNG, and WebP images are allowed");
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage("File size must be less than 5MB");
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (event) => {
      setPreview(event.target?.result as string);
      setErrorMessage("");
    };
    reader.readAsDataURL(file);
  };

  const handleUpload = () => {
    if (!preview || !fileInputRef.current?.files?.[0]) return;

    const formData = new FormData();
    formData.append("file", fileInputRef.current.files[0]);

    uploadMutation.mutate(formData);
  };

  const handleDelete = () => {
    if (confirm("Are you sure you want to delete your profile picture?")) {
      deleteMutation.mutate();
    }
  };

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Profile Picture
      </h2>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {errorMessage && (
        <Alert variant="error" className="mb-4">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      <div className="space-y-4">
        {/* Current Picture Preview */}
        <div className="flex items-center gap-4">
          <div className="w-24 h-24 rounded-full bg-muted flex items-center justify-center flex-shrink-0 overflow-hidden">
            {preview ? (
              <img
                src={preview}
                alt="Preview"
                className="w-full h-full object-cover"
              />
            ) : currentPictureUrl ? (
              <img
                src={currentPictureUrl}
                alt="Current"
                className="w-full h-full object-cover"
              />
            ) : (
              <UserIcon size={48} className="text-muted-foreground" />
            )}
          </div>

          <div className="flex-1">
            <p className="text-sm font-medium text-foreground mb-2">
              {preview ? "Preview" : "Current Picture"}
            </p>
            <p className="text-xs text-muted-foreground mb-3">
              JPEG, PNG, or WebP • Max 5MB
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileSelect}
              className="hidden"
            />

            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadMutation.isPending || deleteMutation.isPending}
            >
              <UploadIcon size={16} className="mr-2" />
              Choose Image
            </Button>
          </div>
        </div>

        {/* Preview Actions */}
        {preview && (
          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              onClick={() => {
                setPreview(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = "";
                }
              }}
              disabled={uploadMutation.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploadMutation.isPending}
              className="flex-1"
            >
              {uploadMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Uploading...
                </>
              ) : (
                "Save Picture"
              )}
            </Button>
          </div>
        )}

        {/* Delete Button */}
        {currentPictureUrl && !preview && (
          <Button
            variant="destructive"
            size="sm"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? (
              <>
                <Spinner size="sm" />
                Deleting...
              </>
            ) : (
              <>
                <TrashIcon size={16} className="mr-2" />
                Delete Picture
              </>
            )}
          </Button>
        )}
      </div>
    </Card>
  );
}
