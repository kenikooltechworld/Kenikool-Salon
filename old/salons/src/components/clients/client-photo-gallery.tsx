import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Upload,
  X,
  Image as ImageIcon,
  Download,
  Edit,
  Trash2,
  ZoomIn,
} from "@/components/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
// Image removed;

interface ClientPhoto {
  id: string;
  url: string;
  photo_type: string;
  tags: string[];
  description?: string;
  service_id?: string;
  created_at: string;
}

interface ClientPhotoGalleryProps {
  clientId: string;
}

export function ClientPhotoGallery({ clientId }: ClientPhotoGalleryProps) {
  const queryClient = useQueryClient();
  const [selectedPhoto, setSelectedPhoto] = useState<ClientPhoto | null>(null);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [lightboxPhoto, setLightboxPhoto] = useState<ClientPhoto | null>(null);
  const [filter, setFilter] = useState<string>("all");

  const { data, isLoading } = useQuery({
    queryKey: ["client-photos", clientId, filter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filter !== "all") {
        params.append("photo_type", filter);
      }
      const response = await apiClient.get(
        `/api/clients/${clientId}/photos?${params}`
      );
      return response.data;
    },
  });

  const uploadPhotos = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await apiClient.post(
        `/api/clients/${clientId}/photos/upload`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success("Photos uploaded successfully");
      queryClient.invalidateQueries({ queryKey: ["client-photos", clientId] });
      setUploadDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to upload photos");
    },
  });

  const updatePhoto = useMutation({
    mutationFn: async ({ photoId, data }: { photoId: string; data: any }) => {
      const params = new URLSearchParams();
      if (data.description) params.append("description", data.description);
      if (data.tags) params.append("tags", data.tags.join(","));

      const response = await apiClient.patch(
        `/api/clients/${clientId}/photos/${photoId}?${params}`
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success("Photo updated");
      queryClient.invalidateQueries({ queryKey: ["client-photos", clientId] });
      setEditDialogOpen(false);
      setSelectedPhoto(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to update photo");
    },
  });

  const deletePhoto = useMutation({
    mutationFn: async (photoId: string) => {
      const response = await apiClient.delete(
        `/api/clients/${clientId}/photos/${photoId}`
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success("Photo deleted");
      queryClient.invalidateQueries({ queryKey: ["client-photos", clientId] });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete photo");
    },
  });

  const handleFileUpload = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    uploadPhotos.mutate(formData);
  };

  const handleEditPhoto = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedPhoto) return;

    const formData = new FormData(e.currentTarget);
    const data = {
      description: formData.get("description") as string,
      tags: (formData.get("tags") as string)
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    };

    updatePhoto.mutate({ photoId: selectedPhoto.id, data });
  };

  const photos: ClientPhoto[] = data?.photos || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="h-5 w-5" />
            Photo Gallery
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Photos</SelectItem>
                <SelectItem value="before">Before</SelectItem>
                <SelectItem value="after">After</SelectItem>
              </SelectContent>
            </Select>
            <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Upload className="h-4 w-4 mr-1" />
                  Upload
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Upload Photos</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleFileUpload} className="space-y-4">
                  <div>
                    <Label htmlFor="files">Select Photos</Label>
                    <Input
                      id="files"
                      name="files"
                      type="file"
                      accept="image/*"
                      multiple
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="photo_type">Type</Label>
                    <Select name="photo_type" required>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="before">Before</SelectItem>
                        <SelectItem value="after">After</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="tags">Tags (comma-separated)</Label>
                    <Input
                      id="tags"
                      name="tags"
                      placeholder="e.g., braids, color, cut"
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      name="description"
                      placeholder="Optional description"
                    />
                  </div>
                  <Button type="submit" disabled={uploadPhotos.isPending}>
                    {uploadPhotos.isPending ? "Uploading..." : "Upload Photos"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading photos...</div>
        ) : photos.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <ImageIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No photos yet</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {photos.map((photo) => (
              <div key={photo.id} className="relative group">
                <div className="aspect-square relative rounded-lg overflow-hidden border">
                  <img                     src={photo.url}
                    alt={photo.description || "Client photo"} className="object-cover"
                    sizes="(max-width: 768px) 50vw, (max-width: 1200px) 33vw, 25vw"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setLightboxPhoto(photo)}
                    >
                      <ZoomIn className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => {
                        setSelectedPhoto(photo);
                        setEditDialogOpen(true);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => {
                        if (confirm("Delete this photo?")) {
                          deletePhoto.mutate(photo.id);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="mt-2">
                  <Badge variant="outline" className="text-xs">
                    {photo.photo_type}
                  </Badge>
                  {photo.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {photo.tags.map((tag, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Lightbox Dialog */}
        <Dialog
          open={!!lightboxPhoto}
          onOpenChange={() => setLightboxPhoto(null)}
        >
          <DialogContent className="max-w-4xl">
            {lightboxPhoto && (
              <div className="relative aspect-video">
                <img                   src={lightboxPhoto.url}
                  alt={lightboxPhoto.description || "Client photo"} className="object-contain"
                  sizes="90vw"
                />
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Edit Dialog */}
        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit Photo</DialogTitle>
            </DialogHeader>
            {selectedPhoto && (
              <form onSubmit={handleEditPhoto} className="space-y-4">
                <div>
                  <Label htmlFor="edit-tags">Tags (comma-separated)</Label>
                  <Input
                    id="edit-tags"
                    name="tags"
                    defaultValue={selectedPhoto.tags.join(", ")}
                  />
                </div>
                <div>
                  <Label htmlFor="edit-description">Description</Label>
                  <Textarea
                    id="edit-description"
                    name="description"
                    defaultValue={selectedPhoto.description || ""}
                  />
                </div>
                <Button type="submit" disabled={updatePhoto.isPending}>
                  {updatePhoto.isPending ? "Saving..." : "Save Changes"}
                </Button>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
