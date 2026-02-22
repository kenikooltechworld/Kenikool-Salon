'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Upload, Trash2, Image as ImageIcon } from 'lucide-react';
import Image from 'next/image';

interface ProductImageUploadProps {
  productId: string;
  category?: string;
}

export function ProductImageUpload({
  productId,
  category = 'other',
}: ProductImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const queryClient = useQueryClient();

  const { data: imageData, isLoading } = useQuery({
    queryKey: ['productImage', productId],
    queryFn: async () => {
      const res = await fetch(`/api/inventory/products/${productId}/image`);
      if (!res.ok) throw new Error('Failed to fetch image');
      return res.json();
    },
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`/api/inventory/products/${productId}/image`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to upload image');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productImage', productId] });
      toast.success('Image uploaded successfully');
    },
    onError: () => {
      toast.error('Failed to upload image');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`/api/inventory/products/${productId}/image`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete image');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productImage', productId] });
      toast.success('Image deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete image');
    },
  });

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }
    uploadMutation.mutate(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const getCategoryPlaceholder = () => {
    const placeholders: Record<string, string> = {
      hair_care: '💇',
      skincare: '✨',
      makeup: '💄',
      tools: '🔧',
      other: '📦',
    };
    return placeholders[category.toLowerCase()] || '📦';
  };

  const currentImage = imageData?.data?.image_url;
  const thumbnail = imageData?.data?.thumbnail_url;

  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <Label>Product Image</Label>

      {currentImage ? (
        <div className="space-y-4">
          <div className="relative w-full h-64 bg-gray-100 rounded-lg overflow-hidden">
            <Image
              src={currentImage}
              alt="Product"
              fill
              className="object-cover"
            />
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                document.getElementById('image-input')?.click()
              }
              disabled={uploadMutation.isPending}
            >
              <Upload className="w-4 h-4 mr-2" />
              Replace Image
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>
      ) : (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
            isDragging
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <div className="text-4xl mb-2">{getCategoryPlaceholder()}</div>
          <p className="text-gray-600 mb-2">
            Drag and drop your image here or click to select
          </p>
          <p className="text-sm text-gray-500">
            Supported formats: JPG, PNG, WebP (Max 5MB)
          </p>

          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={() =>
              document.getElementById('image-input')?.click()
            }
            disabled={uploadMutation.isPending}
          >
            <Upload className="w-4 h-4 mr-2" />
            {uploadMutation.isPending ? 'Uploading...' : 'Select Image'}
          </Button>
        </div>
      )}

      <Input
        id="image-input"
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFileSelect(file);
        }}
      />
    </div>
  );
}
